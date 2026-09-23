"""Ponto de entrada do plugin ClaudIA QGIS: botão na barra, menu, janela de
conexão e a ponte entre a comunidade (thread de rede) e o executor (thread
principal do QGIS).

Modificado por OagronomIA (2026-09-13) a partir de nkarasiak/qgis-mcp — GPLv2+.
"""

import contextlib
import functools
import os

from qgis.core import Qgis, QgsMessageLog, QgsProject, QgsSettings
from qgis.PyQt.QtCore import QSize, Qt, QThread, QTimer, QUrl
from qgis.PyQt.QtGui import QColor, QDesktopServices, QIcon, QPainter, QPen
from qgis.PyQt.QtWidgets import (
    QAction,
    QCheckBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMenu,
    QPushButton,
    QToolButton,
    QVBoxLayout,
)

from . import updater
from .community import ComunidadeWorker
from .compat import (
    MSG_CRITICAL,
    MSG_INFO,
    MSG_WARNING,
    PAINTER_ANTIALIAS,
    TOOLBUTTON_MENU_POPUP,
)
from .constants import (
    DEFAULT_BASE_URL,
    LOG_TAG,
    PAGINA_CONECTOR,
    REPO_URL,
    RELEASES_URL,
    SETTINGS_PREFIX,
    UPSTREAM_URL,
    plugin_version,
    versao_tupla,
)
from .server import ClaudiaExecutor

MENU = "ClaudIA QGIS"

# Qt5 e Qt6 nomeiam os enums de jeitos diferentes; o compat.py cobre os que o
# projeto original usa, estes são só do plugin.
_ECHO_PASSWORD = getattr(getattr(QLineEdit, "EchoMode", QLineEdit), "Password")
_ECHO_NORMAL = getattr(getattr(QLineEdit, "EchoMode", QLineEdit), "Normal")
_ROLE_ACCEPT = getattr(getattr(QDialogButtonBox, "ButtonRole", QDialogButtonBox), "AcceptRole")
_ROLE_REJECT = getattr(getattr(QDialogButtonBox, "ButtonRole", QDialogButtonBox), "RejectRole")
_QUEUED = getattr(getattr(Qt, "ConnectionType", Qt), "QueuedConnection")
_ALIGN_RIGHT = getattr(getattr(Qt, "AlignmentFlag", Qt), "AlignRight")
_TEXT_BESIDE_ICON = getattr(getattr(Qt, "ToolButtonStyle", Qt), "ToolButtonTextBesideIcon")

# Estado da conexão → (cor, rótulo na barra, texto da barra de status, negrito)
ESTADOS = {
    "parado": ("#9E9E9E", "ClaudIA QGIS", "desconectado — clique no botão da ClaudIA para conectar", False),
    "conectando": ("#F9A825", "ClaudIA · conectando…", "conectando à comunidade…", False),
    "conectado": ("#52C937", "ClaudIA · CONECTADO", "conectado à comunidade — a sua IA já pode operar este QGIS", True),
    "sem_rede": ("#F9A825", "ClaudIA · sem conexão", "sem conexão com a comunidade (tentando de novo)", False),
    "token_invalido": ("#D32F2F", "ClaudIA · token recusado", "token recusado — gere outro na comunidade", True),
}
_COR_TEXTO = {"#52C937": "#1B7F2A", "#F9A825": "#8A5A00", "#D32F2F": "#B71C1C", "#9E9E9E": "#616161"}


def _cfg(chave, padrao=None, tipo=None):
    s = QgsSettings()
    if tipo is not None:
        return s.value(f"{SETTINGS_PREFIX}/{chave}", padrao, type=tipo)
    return s.value(f"{SETTINGS_PREFIX}/{chave}", padrao)


def _set_cfg(chave, valor):
    QgsSettings().setValue(f"{SETTINGS_PREFIX}/{chave}", valor)


def _normalizar_base(texto):
    """Qualquer URL do site vira só esquema + host[:porta].

    O fundador colou a URL da PÁGINA do conector no campo (13/09) e o plugin
    passou a chamar …/solucoes/mcp/claudia-qgis/api/qgis/poll. Caminho,
    query e barra final saem; sem esquema assume https.
    """
    from urllib.parse import urlsplit

    t = (texto or "").strip()
    if not t:
        return DEFAULT_BASE_URL
    if not t.startswith(("https://", "http://")):
        t = "https://" + t
    p = urlsplit(t)
    return f"{p.scheme}://{p.netloc}" if p.netloc else DEFAULT_BASE_URL


def _base_url():
    return _normalizar_base(_cfg("base_url", DEFAULT_BASE_URL) or DEFAULT_BASE_URL)


def _pagina_conector():
    return _base_url() + PAGINA_CONECTOR


class ConectarDialog(QDialog):
    """Token da comunidade + opções. Salva em QgsSettings e devolve accept()."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("ClaudIA QGIS — Conectar à comunidade")
        self.setMinimumWidth(540)
        layout = QVBoxLayout(self)

        intro = QLabel(
            "<p>Gere um <b>token do plugin</b> na sua página da comunidade agrônomo10X "
            "e cole abaixo. O token identifica o SEU QGIS: a sua IA (Claude, ChatGPT…) "
            "conversa com a comunidade, e a comunidade fala com este QGIS.</p>"
        )
        intro.setWordWrap(True)
        layout.addWidget(intro)

        abrir = QPushButton("Abrir minha página na comunidade para gerar o token")
        abrir.clicked.connect(lambda: QDesktopServices.openUrl(QUrl(_pagina_conector())))
        layout.addWidget(abrir)

        form = QFormLayout()
        self.token = QLineEdit()
        self.token.setPlaceholderText("cq_…")
        self.token.setEchoMode(_ECHO_PASSWORD)
        self.token.setText(_cfg("token", "") or "")
        self.token.textEdited.connect(lambda _t: self.token.setStyleSheet(""))
        form.addRow("Token do plugin:", self.token)
        mostrar = QCheckBox("Mostrar o token")
        mostrar.toggled.connect(lambda on: self.token.setEchoMode(_ECHO_NORMAL if on else _ECHO_PASSWORD))
        form.addRow("", mostrar)
        self.autostart = QCheckBox("Conectar sozinho quando o QGIS abrir")
        self.autostart.setChecked(bool(_cfg("autostart", False, bool)))
        form.addRow("", self.autostart)
        layout.addLayout(form)

        avancado = QGroupBox("Avançado")
        avancado.setCheckable(True)
        avancado.setChecked(_base_url() != DEFAULT_BASE_URL)
        av_layout = QFormLayout(avancado)
        self.base_url = QLineEdit(_base_url())
        av_layout.addRow("Endereço da comunidade:", self.base_url)
        dica = QLabel("Só mude se a equipe da comunidade pedir (ambiente de testes).")
        dica.setStyleSheet("color: gray")
        av_layout.addRow("", dica)
        layout.addWidget(avancado)
        self._avancado = avancado

        privacidade = QLabel(
            "<small>O que o plugin envia à comunidade: a versão do QGIS, o nome do projeto aberto e o "
            "resultado dos comandos que a SUA IA pedir (dados das camadas, imagens do mapa). "
            "Nada sai sem um comando seu. Revogue o token na sua página a qualquer momento.</small>"
        )
        privacidade.setWordWrap(True)
        layout.addWidget(privacidade)

        botoes = QDialogButtonBox()
        salvar = botoes.addButton("Salvar e conectar", _ROLE_ACCEPT)
        botoes.addButton("Cancelar", _ROLE_REJECT)
        salvar.setDefault(True)
        botoes.accepted.connect(self._salvar)
        botoes.rejected.connect(self.reject)
        layout.addWidget(botoes)

    def _salvar(self):
        token = self.token.text().strip()
        if not token.startswith("cq_") or len(token) < 20:
            self.token.setFocus()
            self.token.setStyleSheet("border: 1px solid #D32F2F")
            return
        base = DEFAULT_BASE_URL
        if self._avancado.isChecked():
            base = _normalizar_base(self.base_url.text())
            self.base_url.setText(base)
        _set_cfg("token", token)
        _set_cfg("base_url", base)
        _set_cfg("autostart", self.autostart.isChecked())
        self.accept()


class ClaudiaQgisPlugin:
    """Plugin ClaudIA QGIS — comunidade agrônomo10X (OagronomIA)."""

    def __init__(self, iface):
        self.iface = iface
        self.executor = None
        self.worker = None
        self.thread = None
        self.action = None
        self.conectar_action = None
        self.pagina_action = None
        self.sobre_action = None
        self.tool_button = None
        self.status_label = None
        self._toolbar_action = None
        self._estado = "parado"
        self._detalhe = ""
        self._timer_info = None
        self._avisou_conexao = False
        self._avisou_rede = False
        self.atualizar_action = None
        self._versao_oferecida = None
        self._atualizando = False

    # --------------------------------------------------------------- ícones
    def _icone_base(self):
        return QIcon(os.path.join(os.path.dirname(__file__), "icons", "icon.png"))

    def _icone_estado(self, cor):
        """Ícone da ClaudIA com ANEL na cor do estado e um ponto no canto."""
        pixmap = self._icone_base().pixmap(QSize(64, 64))
        tamanho = pixmap.width()
        painter = QPainter(pixmap)
        painter.setRenderHint(PAINTER_ANTIALIAS)
        anel = QPen(QColor(cor))
        anel.setWidth(max(4, tamanho // 12))
        painter.setPen(anel)
        painter.setBrush(QColor(0, 0, 0, 0))
        m = anel.width() // 2 + 1
        painter.drawEllipse(m, m, tamanho - 2 * m, tamanho - 2 * m)
        d = int(tamanho * 0.34)
        painter.setBrush(QColor(cor))
        borda = QPen(QColor("white"))
        borda.setWidth(max(2, tamanho // 24))
        painter.setPen(borda)
        painter.drawEllipse(tamanho - d - 1, tamanho - d - 1, d, d)
        painter.end()
        return QIcon(pixmap)

    def _mostrar_estado(self, estado, detalhe=""):
        """Um lugar só para refletir o estado: ícone, rótulo, cor, tooltip e barra de status."""
        cor, rotulo, texto, negrito = ESTADOS.get(estado, ESTADOS["parado"])
        if self.action:
            self.action.setIcon(self._icone_base() if estado == "parado" else self._icone_estado(cor))
            self.action.setText(rotulo)
            self.action.setToolTip(f"ClaudIA QGIS — {texto}" + (f" · {detalhe}" if detalhe else ""))
        if self.tool_button:
            peso = "bold" if negrito else "normal"
            self.tool_button.setStyleSheet(
                f"QToolButton {{ color: {_COR_TEXTO.get(cor, cor)}; font-weight: {peso}; padding: 2px 6px; }}"
            )
        if self.status_label:
            self.status_label.setText(
                f'<span style="color:{cor}; font-size:14px;">●</span> '
                f'<b style="color:{_COR_TEXTO.get(cor, cor)};">ClaudIA QGIS</b>: {texto}'
                + (f" <span style='color:#757575'>· {detalhe}</span>" if detalhe else "")
            )

    # ------------------------------------------------------------------ gui
    def initGui(self):
        toolbar = self.iface.pluginToolBar()

        self.action = QAction(self._icone_base(), "ClaudIA QGIS", self.iface.mainWindow())
        self.action.setCheckable(True)
        self.action.setToolTip("ClaudIA QGIS — clique para conectar à comunidade")
        self.action.triggered.connect(self._alternar)

        self.conectar_action = QAction("Conectar à comunidade…", self.iface.mainWindow())
        self.conectar_action.triggered.connect(self._abrir_dialogo)
        self.pagina_action = QAction("Minha página na comunidade", self.iface.mainWindow())
        self.pagina_action.triggered.connect(lambda: QDesktopServices.openUrl(QUrl(_pagina_conector())))
        self.atualizar_action = QAction("Atualizar o plugin…", self.iface.mainWindow())
        self.atualizar_action.triggered.connect(self._verificar_atualizacao)
        self.sobre_action = QAction("Sobre a ClaudIA QGIS", self.iface.mainWindow())
        self.sobre_action.triggered.connect(self._sobre)

        menu = QMenu()
        menu.addAction(self.conectar_action)
        menu.addAction(self.pagina_action)
        menu.addSeparator()
        menu.addAction(self.atualizar_action)
        menu.addAction(self.sobre_action)

        self.tool_button = QToolButton()
        self.tool_button.setDefaultAction(self.action)
        self.tool_button.setMenu(menu)
        self.tool_button.setPopupMode(TOOLBUTTON_MENU_POPUP)
        self.tool_button.setToolButtonStyle(_TEXT_BESIDE_ICON)
        self._toolbar_action = toolbar.addWidget(self.tool_button)

        # indicador permanente no rodapé do QGIS (o ícone sozinho era discreto demais — fundador, 13/09)
        self.status_label = QLabel()
        self.status_label.setContentsMargins(6, 0, 6, 0)
        with contextlib.suppress(Exception):
            self.iface.mainWindow().statusBar().addPermanentWidget(self.status_label)
        self._mostrar_estado("parado")

        self.iface.addPluginToMenu(MENU, self.action)
        self.iface.addPluginToMenu(MENU, self.conectar_action)
        self.iface.addPluginToMenu(MENU, self.pagina_action)
        self.iface.addPluginToMenu(MENU, self.atualizar_action)
        self.iface.addPluginToMenu(MENU, self.sobre_action)
        for sub in self.iface.pluginMenu().actions():
            if sub.text() == MENU and sub.menu():
                sub.setIcon(self._icone_base())
                break

        if _cfg("reconectar_apos_update", False, bool):
            # a versão anterior se atualizou e pediu para voltar conectada
            _set_cfg("reconectar_apos_update", False)
            with contextlib.suppress(Exception):
                self.iface.messageBar().pushSuccess(LOG_TAG, f"Plugin atualizado para a versão {plugin_version()}.")
            if _cfg("token", ""):
                self.action.setChecked(True)
                self._conectar()
        elif _cfg("autostart", False, bool) and _cfg("token", ""):
            self.action.setChecked(True)
            self._conectar()

        QTimer.singleShot(1200, self._boas_vindas)

    def unload(self):
        self._desconectar()
        # (0.15.0) os checkpoints do projeto vivem numa pasta temporária do executor
        if self.executor:
            with contextlib.suppress(Exception):
                self.executor.limpar_checkpoints()
        if self.action:
            with contextlib.suppress(Exception):
                self.action.triggered.disconnect(self._alternar)
            self.iface.removePluginMenu(MENU, self.action)
            self.action = None
        for a in (self.conectar_action, self.pagina_action, self.atualizar_action, self.sobre_action):
            if a:
                self.iface.removePluginMenu(MENU, a)
        self.conectar_action = self.pagina_action = self.atualizar_action = self.sobre_action = None
        if self._toolbar_action:
            self.iface.pluginToolBar().removeAction(self._toolbar_action)
            self._toolbar_action = None
        if self.status_label:
            with contextlib.suppress(Exception):
                self.iface.mainWindow().statusBar().removeWidget(self.status_label)
            self.status_label.deleteLater()
            self.status_label = None

    # ------------------------------------------------------------- diálogos
    def _boas_vindas(self):
        if not _cfg("first_run", True, bool):
            return
        _set_cfg("first_run", False)
        dlg = QDialog(self.iface.mainWindow())
        dlg.setWindowTitle("ClaudIA QGIS instalada")
        dlg.setMinimumWidth(480)
        layout = QVBoxLayout(dlg)
        corpo = QLabel(
            "<h2>ClaudIA QGIS</h2>"
            "<p>A sua IA (Claude, ChatGPT…) passa a enxergar e operar este QGIS pela "
            "comunidade <b>agrônomo10X</b>.</p>"
            "<p><b>Três passos:</b></p>"
            "<ol>"
            "<li>Na comunidade, abra <b>Soluções → MCP → ClaudIA QGIS</b> e gere um token do plugin.</li>"
            "<li>Aqui, clique no botão da ClaudIA na barra → <b>Conectar à comunidade…</b> e cole o token.</li>"
            "<li>Conecte a ClaudIA QGIS na sua IA (a mesma página explica) e peça: "
            "<i>“lista as camadas do meu projeto”</i>.</li>"
            "</ol>"
            f"<p><small>Software livre (GPLv2+), derivado do QGIS MCP de Nicolas Karasiak. "
            f"Código-fonte: <a href='{REPO_URL}'>{REPO_URL}</a></small></p>"
        )
        corpo.setWordWrap(True)
        corpo.setOpenExternalLinks(True)
        layout.addWidget(corpo)
        botoes = QHBoxLayout()
        abrir = QPushButton("Abrir a comunidade")
        abrir.clicked.connect(lambda: QDesktopServices.openUrl(QUrl(_pagina_conector())))
        conectar = QPushButton("Conectar agora")
        conectar.setDefault(True)
        conectar.clicked.connect(dlg.accept)
        conectar.clicked.connect(self._abrir_dialogo)
        fechar = QPushButton("Depois")
        fechar.clicked.connect(dlg.reject)
        botoes.addWidget(abrir)
        botoes.addStretch()
        botoes.addWidget(fechar)
        botoes.addWidget(conectar)
        layout.addLayout(botoes)
        dlg.exec()

    def _sobre(self):
        dlg = QDialog(self.iface.mainWindow())
        dlg.setWindowTitle("Sobre a ClaudIA QGIS")
        layout = QVBoxLayout(dlg)
        n = self.executor.comunidade["comandos_executados"] if self.executor else 0
        texto = QLabel(
            f"<h3>ClaudIA QGIS {plugin_version()}</h3>"
            "<p>Plugin da comunidade <b>agrônomo10X</b> (OagronomIA): a sua IA opera o QGIS.</p>"
            f"<p>Código-fonte e licença (GPLv2+): <a href='{REPO_URL}'>{REPO_URL}</a></p>"
            f"<p>Derivado de <b>QGIS MCP</b>, de Nicolas Karasiak (GPLv2+): "
            f"<a href='{UPSTREAM_URL}'>{UPSTREAM_URL}</a>. Os handlers que executam os comandos "
            "no QGIS são o trabalho dele; a ClaudIA QGIS troca o servidor local por uma conexão "
            "com a comunidade.</p>"
            f"<p>Estado: <b>{self._estado}</b> {self._detalhe} · {n} comando(s) nesta sessão</p>"
        )
        texto.setWordWrap(True)
        texto.setOpenExternalLinks(True)
        layout.addWidget(texto)
        ok = QPushButton("Fechar")
        ok.clicked.connect(dlg.accept)
        layout.addWidget(ok, alignment=_ALIGN_RIGHT)
        dlg.exec()

    def _abrir_dialogo(self):
        dlg = ConectarDialog(self.iface.mainWindow())
        if dlg.exec():
            self._desconectar()
            self.action.setChecked(True)
            self._conectar()

    # ------------------------------------------------------------- conexão
    def _alternar(self, ligado):
        if ligado:
            if not _cfg("token", ""):
                self.action.setChecked(False)
                self._abrir_dialogo()
                return
            self._conectar()
        else:
            self._desconectar()

    def _info_projeto(self):
        projeto = QgsProject.instance()
        nome = projeto.baseName() or (os.path.basename(projeto.fileName()) if projeto.fileName() else None)
        return {"qgis_versao": Qgis.version(), "plugin_versao": plugin_version(), "projeto": nome or None}

    def _conectar(self):
        token = _cfg("token", "")
        base = _base_url()
        if self.executor is None:
            self.executor = ClaudiaExecutor(iface=self.iface)
        self.executor.ligar_log()
        self.executor.comunidade.update({"base_url": base, "estado": "conectando", "conectado": False})

        self.worker = ComunidadeWorker(base, token, self._info_projeto())
        self.thread = QThread()
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.comando_recebido.connect(self._executar_comando, _QUEUED)
        self.worker.estado_mudou.connect(self._estado_mudou, _QUEUED)
        self.worker.versao_disponivel.connect(self._oferecer_atualizacao, _QUEUED)
        self.thread.start()

        # nome do projeto aberto acompanha o poll (aparece na página da comunidade)
        self._timer_info = QTimer()
        self._timer_info.setInterval(30_000)
        self._timer_info.timeout.connect(self._atualizar_info)
        self._timer_info.start()
        projeto = QgsProject.instance()
        with contextlib.suppress(Exception):
            projeto.readProject.connect(self._atualizar_info)
            projeto.projectSaved.connect(self._atualizar_info)
            projeto.cleared.connect(self._atualizar_info)

        self._mostrar_estado("conectando", base)
        QgsMessageLog.logMessage(f"Conectando à comunidade em {base}", LOG_TAG, MSG_INFO)

    def _desconectar(self):
        if self._timer_info:
            self._timer_info.stop()
            self._timer_info = None
        projeto = QgsProject.instance()
        for sinal in (projeto.readProject, projeto.projectSaved, projeto.cleared):
            with contextlib.suppress(Exception):
                sinal.disconnect(self._atualizar_info)
        if self.worker:
            self.worker.parar()
        if self.thread:
            self.thread.quit()
            self.thread.wait(3000)
            self.thread = None
        self.worker = None
        if self.executor:
            self.executor.desligar_log()
            self.executor.comunidade.update({"conectado": False, "estado": "parado"})
        if self.action:
            self.action.setChecked(False)
        self._mostrar_estado("parado")
        self._estado, self._detalhe = "parado", ""
        self._avisou_conexao = False
        self._avisou_rede = False

    def _atualizar_info(self, *_args):
        if self.worker:
            self.worker.atualizar_info(**self._info_projeto())

    # -------------------------------------------------- ponte comunidade→QGIS
    def _executar_comando(self, comando):
        """Thread principal: executa e devolve ao worker (que sobe o resultado)."""
        worker = self.worker
        if worker is None or self.executor is None:
            return
        envelope = self.executor.executar({"type": comando.get("type"), "params": comando.get("params") or {}})
        worker.entregar_resultado(comando.get("id"), envelope)
        n = self.executor.comunidade["comandos_executados"]
        self._mostrar_estado("conectado", f"{n} comando(s) · último: {comando.get('type')}")

    # ------------------------------------------------------------ atualização
    def _oferecer_atualizacao(self, info):
        """Barra 'Versão X disponível — Atualizar agora' (uma vez por versão)."""
        versao = str(info.get("versao") or "")
        if not versao or not info.get("zip_url") or self._versao_oferecida == versao or self._atualizando:
            return
        self._versao_oferecida = versao
        try:
            barra = self.iface.messageBar()
            w = barra.createMessage(LOG_TAG, f"Versão {versao} do plugin disponível (você está na {plugin_version()}).")
            botao = QPushButton("Atualizar agora")
            botao.clicked.connect(functools.partial(self._atualizar, dict(info)))
            w.layout().addWidget(botao)
            barra.pushWidget(w, MSG_INFO)
        except Exception as e:  # sem barra (headless) — fica no log
            QgsMessageLog.logMessage(f"Versão {versao} disponível em {info.get('url') or RELEASES_URL} ({e})", LOG_TAG, MSG_INFO)

    def _verificar_atualizacao(self):
        """Menu 'Atualizar o plugin…': consulta a comunidade agora."""
        try:
            info = updater.consultar_ultima(_base_url())
        except Exception as e:
            with contextlib.suppress(Exception):
                self.iface.messageBar().pushWarning(LOG_TAG, f"Não consegui consultar a versão mais recente: {e}")
            return
        versao = str(info.get("versao") or "")
        if versao and info.get("zip_url") and versao_tupla(versao) > versao_tupla(plugin_version()):
            self._versao_oferecida = None
            self._oferecer_atualizacao(info)
        else:
            with contextlib.suppress(Exception):
                self.iface.messageBar().pushInfo(LOG_TAG, f"Você já está na versão mais recente ({plugin_version()}).")

    def _atualizar(self, info):
        """Baixa o ZIP da release, valida, desconecta e troca o plugin (recarrega sozinho)."""
        if self._atualizando:
            return
        self._atualizando = True
        versao = str(info.get("versao") or "?")
        try:
            with contextlib.suppress(Exception):
                self.iface.messageBar().pushInfo(LOG_TAG, f"Baixando a versão {versao}…")
            caminho = updater.baixar_zip(str(info["zip_url"]))
            updater.validar_zip(caminho)
        except Exception as e:
            self._atualizando = False
            QgsMessageLog.logMessage(f"Atualização falhou: {e!r}", LOG_TAG, MSG_CRITICAL)
            with contextlib.suppress(Exception):
                self.iface.messageBar().pushCritical(LOG_TAG, f"Não consegui baixar a atualização: {e}. Baixe em {info.get('url') or RELEASES_URL}.")
            return
        # a versão nova volta conectada com o mesmo token
        _set_cfg("reconectar_apos_update", bool(_cfg("token", "")))
        self._desconectar()
        # fora deste objeto: o unloadPlugin vai descarregar o plugin atual
        QTimer.singleShot(0, functools.partial(updater.instalar_e_recarregar_seguro, caminho, self.iface))

    def _estado_mudou(self, estado, detalhe):
        self._estado, self._detalhe = estado, detalhe
        if self.executor:
            self.executor.comunidade.update({"estado": estado, "detalhe": detalhe, "conectado": estado == "conectado"})
        if not self.action:
            return
        if estado == "conectado":
            self._mostrar_estado("conectado")
            if not self._avisou_conexao:
                self._avisou_conexao = True
                with contextlib.suppress(Exception):
                    self.iface.messageBar().pushSuccess(
                        LOG_TAG, "Conectado à comunidade. Peça à sua IA: “lista as camadas do meu projeto”."
                    )
        elif estado == "sem_rede":
            self._mostrar_estado("sem_rede", detalhe)
            QgsMessageLog.logMessage(detalhe, LOG_TAG, MSG_WARNING)
            # Uma vez por tentativa de conexão: só no log ninguém vê (13/09 —
            # o plugin apontava para o endereço errado e parecia "conectado").
            if not self._avisou_rede:
                self._avisou_rede = True
                with contextlib.suppress(Exception):
                    self.iface.messageBar().pushWarning(
                        LOG_TAG,
                        f"Não consegui falar com a comunidade ({detalhe}). Vou continuar tentando; "
                        "confira o endereço em Conectar à comunidade… → Avançado.",
                    )
        elif estado == "token_invalido":
            self._mostrar_estado("token_invalido")
            QgsMessageLog.logMessage(detalhe, LOG_TAG, MSG_CRITICAL)
            with contextlib.suppress(Exception):
                self.iface.messageBar().pushCritical(
                    LOG_TAG,
                    "Token recusado pela comunidade. Gere um token novo na sua página e cole em Conectar à comunidade…",
                )
            self._desconectar()
            self._mostrar_estado("token_invalido")


def classFactory(iface):
    return ClaudiaQgisPlugin(iface)
