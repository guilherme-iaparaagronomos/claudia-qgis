"""Executor de comandos: recebe ``{"type", "params"}``, valida contra a
assinatura do handler e devolve o envelope ``{"status": "success", "result"}``
ou ``{"status": "error", "message"}``.

Derivado do ``QgisMCPServer`` de nkarasiak/qgis-mcp, SEM a parte de socket:
na ClaudIA QGIS os comandos chegam pela comunidade agrônomo10X
(:mod:`community`), que os enfileira em nome da IA do usuário, e são
executados aqui, na thread principal do QGIS. Os handlers (``handlers/``)
são os do projeto original; nada neste módulo sabe o que cada um faz.

Modificado por OagronomIA (2026-09-13) a partir de nkarasiak/qgis-mcp — GPLv2+.
"""

import inspect
import traceback
from collections import deque
from typing import ClassVar

from qgis.core import QgsApplication, QgsMessageLog
from qgis.PyQt.QtCore import QObject

from .compat import MSG_CRITICAL, MSG_INFO, MSG_WARNING
from .constants import LOG_TAG
from .errors import CommandError
from .handlers import (
    CanvasHandlers,
    ConnectionHandlers,
    FeatureHandlers,
    HandlerBase,
    LayerHandlers,
    LayoutHandlers,
    ProcessingHandlers,
    ProjectHandlers,
    StyleHandlers,
    SystemHandlers,
)
from .registry import BATCH_BLOCKED_COMMANDS, COMMANDS, command


class ClaudiaExecutor(
    SystemHandlers,
    ProjectHandlers,
    LayerHandlers,
    FeatureHandlers,
    StyleHandlers,
    CanvasHandlers,
    ProcessingHandlers,
    LayoutHandlers,
    ConnectionHandlers,
    HandlerBase,
    QObject,
):
    """Despacha comandos para os handlers.

    Os mixins contribuem os comandos; ``HandlerBase`` vem por último para que
    os mixins de domínio não sobrescrevam nada de ``QObject`` por acidente.
    """

    LOG_TAG: ClassVar[str] = LOG_TAG

    def __init__(self, iface=None):
        super().__init__()
        self.iface = iface
        self._signatures = {}  # cmd_type -> inspect.Signature, preenchido no 1º uso
        self._message_log = deque(maxlen=1000)
        self._log_ligado = False
        # Guarda contra reentrância: handlers longos (render_map, processing
        # com feedback) bombeiam o event loop do Qt para a interface não
        # travar, e um sinal enfileirado poderia entrar NO MEIO do handler.
        self._in_dispatch = False
        # Estado da conexão com a comunidade, preenchido pelo plugin e lido
        # pelo handler `diagnose`.
        self.comunidade = {
            "conectado": False,
            "base_url": None,
            "estado": "parado",
            "detalhe": None,
            "ultimo_comando": None,
            "comandos_executados": 0,
        }

    # ------------------------------------------------------------------ log
    def ligar_log(self):
        """Passa a capturar o log de mensagens do QGIS (para get_message_log)."""
        if self._log_ligado:
            return
        msg_log = QgsApplication.messageLog()
        # QGIS 4.x só emite messageReceivedWithFormat; 3.x, messageReceived.
        if hasattr(msg_log, "messageReceivedWithFormat"):
            msg_log.messageReceivedWithFormat.connect(self._capture_message)
        else:
            msg_log.messageReceived.connect(self._capture_message)
        self._log_ligado = True

    def desligar_log(self):
        if not self._log_ligado:
            return
        msg_log = QgsApplication.messageLog()
        try:
            if hasattr(msg_log, "messageReceivedWithFormat"):
                msg_log.messageReceivedWithFormat.disconnect(self._capture_message)
            else:
                msg_log.messageReceived.disconnect(self._capture_message)
        except (TypeError, RuntimeError):
            pass
        self._log_ligado = False

    # ------------------------------------------------------------- despacho
    def _signature(self, cmd_type, handler):
        """Assinatura (em cache) de um handler, para validar os parâmetros.

        Em cache porque ``batch`` pode despachar muitos comandos numa mensagem
        e ``inspect.signature()`` não é de graça.
        """
        signature = self._signatures.get(cmd_type)
        if signature is None:
            signature = inspect.signature(handler)
            self._signatures[cmd_type] = signature
        return signature

    def executar(self, comando):
        """Ponto de entrada do plugin: um comando vindo da comunidade."""
        if not isinstance(comando, dict):
            return {"status": "error", "message": "Comando inválido: esperava um objeto"}
        if self._in_dispatch:
            return {
                "status": "error",
                "message": "O QGIS ainda está executando o comando anterior. Tente de novo em instantes.",
            }
        self._in_dispatch = True
        try:
            envelope = self._dispatch(comando)
        finally:
            self._in_dispatch = False
        self.comunidade["ultimo_comando"] = comando.get("type")
        self.comunidade["comandos_executados"] += 1
        return envelope

    def _dispatch(self, command):
        """Despacha um comando para o handler dele."""
        try:
            cmd_type = command.get("type")
            params = command.get("params", {})

            # Entrada externa: `type` pode ser qualquer valor JSON — confira
            # que é string antes da busca no conjunto e só então resolva. A
            # pertinência a COMMANDS é o que impede getattr de alcançar
            # atributos que não são handlers.
            if not isinstance(cmd_type, str) or cmd_type not in COMMANDS:
                QgsMessageLog.logMessage(f"Comando desconhecido: {cmd_type}", self.LOG_TAG, MSG_WARNING)
                return {"status": "error", "message": f"Unknown command type: {cmd_type}"}
            if params is None:
                params = {}
            if not isinstance(params, dict):
                return {"status": "error", "message": "Invalid params: expected an object"}
            handler = getattr(self, cmd_type)

            # Parâmetro errado é engano de quem chamou, não defeito do plugin:
            # valida contra a assinatura antes de chamar, para não despejar um
            # traceback CRITICAL no log do usuário por um argumento faltando.
            try:
                self._signature(cmd_type, handler).bind(**params)
            except TypeError as exc:
                message = f"{cmd_type}: {exc}"
                QgsMessageLog.logMessage(f"Parâmetros inválidos: {message}", self.LOG_TAG, MSG_WARNING)
                return {"status": "error", "message": message}

            try:
                QgsMessageLog.logMessage(f"Executando: {cmd_type}", self.LOG_TAG, MSG_INFO)
                return {"status": "success", "result": handler(**params)}
            except CommandError as e:
                # Falha esperada, que quem chamou consegue tratar — só a
                # mensagem, sem traceback.
                QgsMessageLog.logMessage(f"Erro em {cmd_type}: {e!s}", self.LOG_TAG, MSG_WARNING)
                return {"status": "error", "message": str(e)}
            except Exception as e:
                # Qualquer outra coisa é defeito do plugin (TypeError de
                # assinatura, AttributeError de método renomeado no PyQGIS…):
                # loga o traceback e marca a resposta.
                QgsMessageLog.logMessage(
                    f"Erro não tratado em {cmd_type}: {e!r}\n{traceback.format_exc()}",
                    self.LOG_TAG,
                    MSG_CRITICAL,
                )
                return {"status": "error", "message": str(e), "internal": True}

        except Exception as e:
            QgsMessageLog.logMessage(
                f"Erro ao executar comando: {e!r}\n{traceback.format_exc()}",
                self.LOG_TAG,
                MSG_CRITICAL,
            )
            return {"status": "error", "message": str(e), "internal": True}

    @command
    def batch(self, commands, **kwargs):
        """Executa vários comandos em sequência e devolve a lista de resultados.

        Comandos destrutivos são recusados AQUI também, não só no servidor da
        comunidade: recusar um não aborta o lote — a recusa vai na posição
        daquele comando.
        """
        results = []
        for cmd in commands:
            cmd_type = cmd.get("type") if isinstance(cmd, dict) else None
            if cmd_type in BATCH_BLOCKED_COMMANDS:
                QgsMessageLog.logMessage(f"Recusado {cmd_type!r} dentro de batch", self.LOG_TAG, MSG_WARNING)
                results.append(
                    {
                        "status": "error",
                        "message": (
                            f"Command {cmd_type!r} is not allowed in batch - "
                            "call it individually so confirmation can be requested"
                        ),
                    }
                )
                continue
            results.append(self._dispatch({"type": cmd_type, "params": (cmd or {}).get("params", {})}))
        return results
