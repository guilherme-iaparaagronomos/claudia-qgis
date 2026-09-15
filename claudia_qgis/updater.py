"""Atualização do próprio plugin a partir do ZIP da release (13/09).

Fluxo: a comunidade manda `plugin_ultima` no poll (ou o menu consulta
``/api/qgis/plugin``); se a versão for maior que a instalada, o plugin mostra
"Atualizar agora". O botão baixa o ZIP, valida (precisa conter
``claudia_qgis/metadata.txt``), DESCARREGA o plugin, troca a pasta inteira e
recarrega — o mesmo que o Gerenciador de Complementos faz em "Instalar a
partir de um ZIP", sem as caixas de diálogo dele.

Este módulo é importado com nome próprio e roda com funções de módulo (não
métodos do plugin): durante a troca o objeto do plugin antigo já foi
descarregado.

Modificado por OagronomIA (2026-09-13) a partir de nkarasiak/qgis-mcp — GPLv2+.
"""

from __future__ import annotations

import configparser
import contextlib
import http.client
import os
import shutil
import ssl
import tempfile
import urllib.parse
import zipfile

from .constants import ENDPOINT_PLUGIN, LOG_TAG, PLUGIN_DIR, user_agent

NOME_PACOTE = os.path.basename(PLUGIN_DIR)  # claudia_qgis
MAX_ZIP_BYTES = 20 * 1024 * 1024


MAX_REDIRECIONAMENTOS = 5


def _abrir(url: str, headers: dict, timeout: int, *, so_https: bool) -> tuple[http.client.HTTPConnection, http.client.HTTPResponse]:
    """GET por ``http.client`` — só ``http``/``https`` (nada de ``file:`` ou esquemas
    customizados), seguindo até 5 redirecionamentos (o ZIP da release do GitHub
    redireciona para o CDN). Devolve (conexão, resposta); quem chama fecha a conexão."""
    for _ in range(MAX_REDIRECIONAMENTOS + 1):
        u = urllib.parse.urlsplit(url)
        if u.scheme == "https":
            conn = http.client.HTTPSConnection(u.hostname, u.port, timeout=timeout, context=_ssl())
        elif u.scheme == "http" and not so_https:
            conn = http.client.HTTPConnection(u.hostname, u.port, timeout=timeout)
        else:
            raise ValueError(f"esquema não permitido na atualização: {u.scheme or '(vazio)'}")
        caminho = (u.path or "/") + (f"?{u.query}" if u.query else "")
        conn.request("GET", caminho, headers={**headers, "Host": u.netloc})
        resp = conn.getresponse()
        if resp.status in (301, 302, 303, 307, 308):
            destino = resp.getheader("Location")
            resp.read()
            conn.close()
            if not destino:
                raise ValueError("redirecionamento sem destino")
            url = urllib.parse.urljoin(url, destino)
            continue
        if resp.status != 200:
            resp.read()
            conn.close()
            raise ValueError(f"HTTP {resp.status} ao buscar {u.netloc}{u.path}")
        return conn, resp
    raise ValueError("redirecionamentos demais")


def consultar_ultima(base_url: str, timeout: int = 10) -> dict:
    """GET {base}/api/qgis/plugin → {"versao", "zip_url", "url", "minima"}."""
    import json

    # http só para o dev local; em produção o endereço da comunidade é https
    conn, resp = _abrir(
        base_url.rstrip("/") + ENDPOINT_PLUGIN,
        {"User-Agent": user_agent(), "Accept": "application/json"},
        timeout,
        so_https=False,
    )
    try:
        return json.loads(resp.read().decode("utf-8"))
    finally:
        conn.close()


def instalar_e_recarregar_seguro(caminho_zip: str, iface=None) -> None:
    """Versão para QTimer.singleShot: erro vira barra de mensagem, nunca traceback perdido."""
    try:
        versao = instalar_e_recarregar(caminho_zip)
    except Exception as e:
        # avisar é o melhor esforço: se o próprio QGIS não aceitar o log/barra
        # (fechando, sem iface), não há mais a quem avisar
        with contextlib.suppress(Exception):
            from qgis.core import QgsMessageLog

            from .compat import MSG_CRITICAL

            QgsMessageLog.logMessage(f"Atualização falhou: {e!r}", LOG_TAG, MSG_CRITICAL)
            if iface is not None:
                iface.messageBar().pushCritical(LOG_TAG, f"A atualização falhou ({e}). Instale pelo ZIP em Complementos → Instalar a partir de um ZIP.")
        return
    with contextlib.suppress(Exception):
        from qgis.core import QgsMessageLog

        from .compat import MSG_INFO

        QgsMessageLog.logMessage(f"Plugin atualizado para {versao}", LOG_TAG, MSG_INFO)


def _ssl():
    ctx = ssl.create_default_context()
    # o Python do QGIS no Windows traz certifi; sem ele, a loja do sistema basta
    with contextlib.suppress(ImportError, OSError, ssl.SSLError):
        import certifi

        ctx.load_verify_locations(certifi.where())
    return ctx


def baixar_zip(url: str, timeout: int = 60) -> str:
    """Baixa o ZIP para um arquivo temporário e devolve o caminho."""
    if not url.startswith("https://"):
        raise ValueError("só baixo atualização por https")
    conn, resp = _abrir(url, {"User-Agent": user_agent(), "Accept": "application/octet-stream"}, timeout, so_https=True)
    fd, destino = tempfile.mkstemp(prefix="claudia_qgis-", suffix=".zip")
    try:
        with os.fdopen(fd, "wb") as f:
            total = 0
            while True:
                bloco = resp.read(65536)
                if not bloco:
                    break
                total += len(bloco)
                if total > MAX_ZIP_BYTES:
                    raise ValueError("ZIP maior que o esperado — abortei")
                f.write(bloco)
    except BaseException:
        with contextlib.suppress(OSError):
            os.remove(destino)
        raise
    finally:
        conn.close()
    return destino


def validar_zip(caminho: str) -> str:
    """Confere que o ZIP é o plugin (pasta claudia_qgis/ com metadata.txt) e devolve a versão dentro dele."""
    with zipfile.ZipFile(caminho) as z:
        nomes = z.namelist()
        if f"{NOME_PACOTE}/metadata.txt" not in nomes or f"{NOME_PACOTE}/__init__.py" not in nomes:
            raise ValueError("o ZIP não contém o plugin claudia_qgis")
        for n in nomes:
            if n.startswith("/") or ".." in n.split("/"):
                raise ValueError(f"caminho suspeito no ZIP: {n}")
        cfg = configparser.ConfigParser()
        cfg.read_string(z.read(f"{NOME_PACOTE}/metadata.txt").decode("utf-8"))
        return cfg.get("general", "version", fallback="?")


def instalar_e_recarregar(caminho_zip: str) -> str:
    """Troca a pasta do plugin pelo conteúdo do ZIP e recarrega. Devolve a versão instalada.

    Chamar SEM referências vivas ao plugin antigo (QTimer.singleShot a partir
    do plugin) — o ``unloadPlugin`` chama o ``unload()`` dele.
    """
    import qgis.utils

    versao = validar_zip(caminho_zip)
    pasta_plugins = os.path.dirname(PLUGIN_DIR)
    destino = os.path.join(pasta_plugins, NOME_PACOTE)
    with tempfile.TemporaryDirectory(prefix="claudia_qgis-novo-") as tmp:
        with zipfile.ZipFile(caminho_zip) as z:
            z.extractall(tmp)
        novo = os.path.join(tmp, NOME_PACOTE)
        if NOME_PACOTE in qgis.utils.active_plugins:
            qgis.utils.unloadPlugin(NOME_PACOTE)
        backup = destino + ".anterior"
        shutil.rmtree(backup, ignore_errors=True)
        os.rename(destino, backup)
        try:
            shutil.copytree(novo, destino)
        except Exception:
            shutil.rmtree(destino, ignore_errors=True)
            os.rename(backup, destino)
            raise
        shutil.rmtree(backup, ignore_errors=True)
    try:
        os.remove(caminho_zip)
    except OSError:
        pass
    qgis.utils.updateAvailablePlugins()
    # purga os módulos antigos e carrega os novos (reloadPlugin faz unload+load+start)
    if NOME_PACOTE in qgis.utils.active_plugins:
        qgis.utils.reloadPlugin(NOME_PACOTE)
    else:
        qgis.utils.loadPlugin(NOME_PACOTE)
        qgis.utils.startPlugin(NOME_PACOTE)
    return versao
