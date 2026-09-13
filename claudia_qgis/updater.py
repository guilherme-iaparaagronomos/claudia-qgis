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
import os
import shutil
import ssl
import tempfile
import urllib.request
import zipfile

from .constants import ENDPOINT_PLUGIN, LOG_TAG, PLUGIN_DIR, user_agent

NOME_PACOTE = os.path.basename(PLUGIN_DIR)  # claudia_qgis
MAX_ZIP_BYTES = 20 * 1024 * 1024


def consultar_ultima(base_url: str, timeout: int = 10) -> dict:
    """GET {base}/api/qgis/plugin → {"versao", "zip_url", "url", "minima"}."""
    import json

    req = urllib.request.Request(
        base_url.rstrip("/") + ENDPOINT_PLUGIN,
        headers={"User-Agent": user_agent(), "Accept": "application/json"},
    )
    ctx = _ssl() if base_url.startswith("https://") else None
    with urllib.request.urlopen(req, timeout=timeout, context=ctx) as r:
        return json.loads(r.read().decode("utf-8"))


def instalar_e_recarregar_seguro(caminho_zip: str, iface=None) -> None:
    """Versão para QTimer.singleShot: erro vira barra de mensagem, nunca traceback perdido."""
    try:
        versao = instalar_e_recarregar(caminho_zip)
    except Exception as e:
        try:
            from qgis.core import QgsMessageLog

            from .compat import MSG_CRITICAL

            QgsMessageLog.logMessage(f"Atualização falhou: {e!r}", LOG_TAG, MSG_CRITICAL)
            if iface is not None:
                iface.messageBar().pushCritical(LOG_TAG, f"A atualização falhou ({e}). Instale pelo ZIP em Complementos → Instalar a partir de um ZIP.")
        except Exception:
            pass
        return
    try:
        from qgis.core import QgsMessageLog

        from .compat import MSG_INFO

        QgsMessageLog.logMessage(f"Plugin atualizado para {versao}", LOG_TAG, MSG_INFO)
    except Exception:
        pass


def _ssl():
    ctx = ssl.create_default_context()
    try:
        import certifi

        ctx.load_verify_locations(certifi.where())
    except Exception:
        pass
    return ctx


def baixar_zip(url: str, timeout: int = 60) -> str:
    """Baixa o ZIP para um arquivo temporário e devolve o caminho."""
    if not url.startswith("https://"):
        raise ValueError("só baixo atualização por https")
    req = urllib.request.Request(url, headers={"User-Agent": user_agent(), "Accept": "application/octet-stream"})
    fd, destino = tempfile.mkstemp(prefix="claudia_qgis-", suffix=".zip")
    with os.fdopen(fd, "wb") as f, urllib.request.urlopen(req, timeout=timeout, context=_ssl()) as r:
        total = 0
        while True:
            bloco = r.read(65536)
            if not bloco:
                break
            total += len(bloco)
            if total > MAX_ZIP_BYTES:
                raise ValueError("ZIP maior que o esperado — abortei")
            f.write(bloco)
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
