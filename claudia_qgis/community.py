"""Cliente da comunidade agrônomo10X: busca comandos e devolve resultados.

Protocolo (HTTPS, JSON, token do plugin no Bearer):

* ``POST {base}/api/qgis/poll``  corpo ``{qgis_versao, plugin_versao, projeto}``
  → a comunidade segura a requisição por até ~20 s esperando um comando da IA
  do usuário e responde ``{"comando": {"id", "type", "params"}}`` ou
  ``{"comando": null}`` (aí o plugin chama de novo — é um long-poll, sem
  porta aberta na máquina do usuário e sem firewall para configurar).
* ``POST {base}/api/qgis/result`` corpo ``{id, status, result | message}``
  — o mesmo envelope que o executor devolve.

A rede roda numa thread própria (:class:`ComunidadeWorker` dentro de um
``QThread``). PyQGIS NÃO é thread-safe, então o worker nunca toca no QGIS:
ele emite ``comando_recebido`` (entregue na thread principal por conexão
enfileirada do Qt), o plugin executa e chama :meth:`entregar_resultado`, e o
worker então sobe a resposta.

Modificado por OagronomIA (2026-09-13) a partir de nkarasiak/qgis-mcp — GPLv2+.
"""

from __future__ import annotations

import http.client
import json
import queue
import socket
import ssl
import threading
import time
from urllib.parse import urlsplit

from qgis.PyQt.QtCore import QObject, pyqtSignal

from .constants import MAX_RESULT_BYTES, user_agent

POLL_TIMEOUT_S = 45  # a comunidade segura ~20 s; folga para rede lenta
RESULT_TIMEOUT_S = 90  # resultados grandes (render em base64) sobem devagar
ESPERA_RESULTADO_S = 330  # o servidor MCP desiste em ~300 s; o plugin um pouco depois
BACKOFF_INICIAL_S = 2
BACKOFF_MAX_S = 30


class TokenInvalido(Exception):
    """A comunidade respondeu 401: token revogado, vencido ou errado."""


class ErroHttp(Exception):
    """Qualquer outra resposta que não seja 2xx."""


class ErroRede(Exception):
    """Sem conexão, DNS, TLS, timeout…"""


def _contexto_ssl():
    ctx = ssl.create_default_context()
    try:  # o Python do QGIS no Windows traz certifi; a loja do sistema costuma bastar
        import certifi

        ctx.load_verify_locations(certifi.where())
    except Exception:
        pass
    return ctx


class ComunidadeWorker(QObject):
    """Loop de long-poll. Vive num QThread; só fala com o QGIS por sinais."""

    # comando vindo da comunidade: {"id", "type", "params"}
    comando_recebido = pyqtSignal(dict)
    # estado: conectando | conectado | sem_rede | token_invalido | parado — e um detalhe legível
    estado_mudou = pyqtSignal(str, str)

    def __init__(self, base_url: str, token: str, info: dict):
        super().__init__()
        self._base = base_url.rstrip("/")
        self._token = token
        self._info = dict(info)
        self._lock = threading.Lock()
        self._parar = threading.Event()
        self._resultados: queue.Queue = queue.Queue()
        self._conn = None
        self._ssl = _contexto_ssl()
        self._estado = None

    # ------------------------------------------------ chamados da thread principal
    def atualizar_info(self, **campos):
        """Versão do QGIS / projeto aberto, enviados a cada poll (status na página)."""
        with self._lock:
            self._info.update(campos)

    def entregar_resultado(self, comando_id: str, envelope: dict):
        self._resultados.put((comando_id, envelope))

    def parar(self):
        """Interrompe na hora: fecha o socket do poll em curso e solta a fila."""
        self._parar.set()
        self._resultados.put(None)
        conn = self._conn
        if conn is not None:
            try:
                conn.close()
            except Exception:
                pass

    # ---------------------------------------------------------- thread do worker
    def run(self):
        backoff = BACKOFF_INICIAL_S
        self._emitir("conectando", "conectando à comunidade…")
        while not self._parar.is_set():
            try:
                with self._lock:
                    corpo = dict(self._info)
                resposta = self._post("/api/qgis/poll", corpo, POLL_TIMEOUT_S)
            except TokenInvalido:
                self._emitir("token_invalido", "token recusado pela comunidade (revogado ou errado)")
                break
            except (ErroRede, ErroHttp) as e:
                if self._parar.is_set():
                    break
                self._emitir("sem_rede", f"{e} — tentando de novo em {backoff} s")
                self._parar.wait(backoff)
                backoff = min(backoff * 2, BACKOFF_MAX_S)
                continue
            except Exception as e:  # nunca deixar a thread morrer em silêncio
                if self._parar.is_set():
                    break
                self._emitir("sem_rede", f"{type(e).__name__}: {e} — tentando de novo em {backoff} s")
                self._parar.wait(backoff)
                backoff = min(backoff * 2, BACKOFF_MAX_S)
                continue

            backoff = BACKOFF_INICIAL_S
            self._emitir("conectado", "conectado à comunidade")
            comando = resposta.get("comando") if isinstance(resposta, dict) else None
            if not comando or not isinstance(comando, dict):
                continue

            self.comando_recebido.emit(comando)
            try:
                item = self._resultados.get(timeout=ESPERA_RESULTADO_S)
            except queue.Empty:
                item = (comando.get("id"), {"status": "error", "message": "o plugin não recebeu o resultado a tempo"})
            if item is None:  # parar()
                break
            comando_id, envelope = item
            self._subir_resultado(comando_id, envelope)
        self._emitir("parado", "desconectado")

    def _subir_resultado(self, comando_id, envelope):
        corpo = {"id": comando_id}
        corpo.update(envelope if isinstance(envelope, dict) else {"status": "error", "message": "envelope inválido"})
        dados = json.dumps(corpo, ensure_ascii=False, default=str).encode("utf-8")
        if len(dados) > MAX_RESULT_BYTES:
            mb = len(dados) / (1024 * 1024)
            dados = json.dumps(
                {
                    "id": comando_id,
                    "status": "error",
                    "message": f"resultado grande demais ({mb:.1f} MB) — peça uma imagem/recorte menor",
                },
            ).encode("utf-8")
        for tentativa in (1, 2):
            try:
                self._post_bruto("/api/qgis/result", dados, RESULT_TIMEOUT_S)
                return
            except TokenInvalido:
                self._emitir("token_invalido", "token recusado ao enviar o resultado")
                return
            except Exception as e:
                if tentativa == 2 or self._parar.is_set():
                    self._emitir("sem_rede", f"não consegui enviar o resultado: {e}")
                    return
                self._parar.wait(2)

    # ------------------------------------------------------------------- http
    def _post(self, caminho, corpo, timeout):
        return self._post_bruto(caminho, json.dumps(corpo, ensure_ascii=False, default=str).encode("utf-8"), timeout)

    def _post_bruto(self, caminho, dados: bytes, timeout):
        partes = urlsplit(self._base)
        seguro = partes.scheme == "https"
        porta = partes.port or (443 if seguro else 80)
        if seguro:
            conn = http.client.HTTPSConnection(partes.hostname, porta, timeout=timeout, context=self._ssl)
        else:  # ambiente de desenvolvimento da equipe
            conn = http.client.HTTPConnection(partes.hostname, porta, timeout=timeout)
        self._conn = conn
        try:
            conn.request(
                "POST",
                (partes.path.rstrip("/") + caminho) or caminho,
                body=dados,
                headers={
                    "Authorization": f"Bearer {self._token}",
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                    "User-Agent": user_agent(),
                    "Content-Length": str(len(dados)),
                },
            )
            resp = conn.getresponse()
            payload = resp.read()
            if resp.status == 401:
                raise TokenInvalido()
            if resp.status < 200 or resp.status >= 300:
                trecho = payload[:120].decode("utf-8", "replace")
                if b"<html" in payload[:400].lower():
                    trecho = "página HTML (bloqueio de rede/WAF?)"
                raise ErroHttp(f"HTTP {resp.status} em {caminho}: {trecho}")
            if not payload:
                return {}
            try:
                return json.loads(payload.decode("utf-8"))
            except ValueError as e:
                raise ErroHttp(f"resposta não é JSON em {caminho}: {e}") from None
        except (TokenInvalido, ErroHttp):
            raise
        except (OSError, socket.timeout, http.client.HTTPException, ssl.SSLError) as e:
            raise ErroRede(str(e) or type(e).__name__) from None
        finally:
            self._conn = None
            try:
                conn.close()
            except Exception:
                pass

    def _emitir(self, estado, detalhe):
        # `conectado` a cada poll seria um sinal a cada 20 s à toa; só muda de estado
        if estado == self._estado and estado in ("conectado", "conectando"):
            return
        self._estado = estado
        self.estado_mudou.emit(estado, detalhe)


def agora_iso():
    return time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime())
