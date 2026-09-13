"""Valores compartilhados pelo executor, pelo plugin e pelo cliente da comunidade.

Só stdlib, sem importar ``qgis`` — como :mod:`errors` e :mod:`registry`.

Modificado por OagronomIA (2026-09-13) a partir de nkarasiak/qgis-mcp — GPLv2+.
"""

import os

# Pasta do pacote do plugin — onde vivem metadata.txt e icons/.
PLUGIN_DIR = os.path.dirname(os.path.abspath(__file__))

# Prefixo das chaves em QgsSettings de tudo que o plugin persiste.
SETTINGS_PREFIX = "claudia_qgis"

# Comunidade agrônomo10X (OagronomIA). O endereço pode ser trocado na caixa
# "Avançado" da janela de conexão (ambiente de desenvolvimento da equipe).
DEFAULT_BASE_URL = "https://comunidade.agronomos.ia.br"
PAGINA_CONECTOR = "/solucoes/mcp/claudia-qgis"
REPO_URL = "https://github.com/guilherme-iaparaagronomos/claudia-qgis"
UPSTREAM_URL = "https://github.com/nkarasiak/qgis-mcp"

LOG_TAG = "ClaudIA QGIS"

# Um resultado maior que isso não sobe: a comunidade recusa acima de 8 MB e um
# render de mapa de 3000×3000 em base64 chega perto disso.
MAX_RESULT_BYTES = 7 * 1024 * 1024

_plugin_version = None


def plugin_version():
    """Versão deste plugin, lida do metadata.txt (o arquivo que o QGIS lê).

    Em cache: ``diagnose`` e o poll pedem a cada chamada, e ela não muda sem
    recarregar o plugin.
    """
    global _plugin_version
    if _plugin_version is None:
        import configparser

        config = configparser.ConfigParser()
        config.read(os.path.join(PLUGIN_DIR, "metadata.txt"), encoding="utf-8")
        _plugin_version = config.get("general", "version", fallback="unknown")
    return _plugin_version


def user_agent():
    return f"ClaudIA-QGIS/{plugin_version()}"
