"""Fumaça da INTERFACE do plugin sem abrir o QGIS: instancia o plugin com um
``iface`` falso (QMainWindow + QToolBar reais), roda initGui, percorre todos
os estados e descarrega. Pega erro de atributo/enum do Qt antes do teste
manual.

    "C:/Program Files/QGIS 3.40.14/bin/python-qgis-ltr.bat" tests/smoke_gui.py
"""

import os
import sys
from unittest.mock import MagicMock

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from qgis.core import QgsApplication  # noqa: E402
from qgis.PyQt.QtWidgets import QMainWindow, QMenu, QToolBar  # noqa: E402

app = QgsApplication([], True)
app.initQgis()

from claudia_qgis.plugin import ESTADOS, ClaudiaQgisPlugin, _normalizar_base  # noqa: E402

assert _normalizar_base("https://comunidade.agronomos.ia.br/solucoes/mcp/claudia-qgis") == "https://comunidade.agronomos.ia.br"
assert _normalizar_base("comunidade.agronomos.ia.br/") == "https://comunidade.agronomos.ia.br"
assert _normalizar_base("http://dev.agronomos.ia.br:3000/x?y=1") == "http://dev.agronomos.ia.br:3000"
assert _normalizar_base("") == "https://comunidade.agronomos.ia.br"
print("  ok  _normalizar_base reduz URL de página ao domínio")

janela = QMainWindow()
barra = QToolBar(janela)
menu_plugins = QMenu(janela)
iface = MagicMock()
iface.mainWindow.return_value = janela
iface.pluginToolBar.return_value = barra
iface.pluginMenu.return_value = menu_plugins

plugin = ClaudiaQgisPlugin(iface)
plugin.initGui()
assert plugin.action is not None and plugin.tool_button is not None and plugin.status_label is not None
assert "ClaudIA" in plugin.status_label.text()
for estado in ESTADOS:
    plugin._mostrar_estado(estado, "detalhe de teste")
    assert plugin.action.text() == ESTADOS[estado][1], (estado, plugin.action.text())
    assert "ClaudIA QGIS" in plugin.status_label.text()
    assert not plugin.action.icon().isNull()
    print("  ok ", estado, "→", plugin.action.text(), "|", plugin.tool_button.styleSheet()[:48])
plugin._estado_mudou("conectado", "x")
assert plugin.action.text() == "ClaudIA · CONECTADO"
plugin._estado_mudou("sem_rede", "HTTP 429")
assert "sem conexão" in plugin.action.text()

# atualização: oferta uma vez por versão; versão igual/menor não oferece
from claudia_qgis import updater  # noqa: E402
from claudia_qgis.constants import plugin_version, versao_tupla  # noqa: E402

assert versao_tupla("0.2.0") > versao_tupla("0.1.9") and versao_tupla("v1.0") == (1, 0, 0) and versao_tupla("lixo") == (0, 0, 0)
plugin._oferecer_atualizacao({"versao": "9.9.9", "zip_url": "https://example.invalid/claudia_qgis-9.9.9.zip", "url": ""})
assert plugin._versao_oferecida == "9.9.9"
assert iface.messageBar.return_value.pushWidget.called, "barra 'Atualizar agora' não foi empurrada"
print("  ok  oferta de atualização 9.9.9 → barra com botão")
dist = os.path.join(RAIZ, "dist", f"claudia_qgis-{plugin_version()}.zip")
if os.path.exists(dist):
    assert updater.validar_zip(dist) == plugin_version()
    print("  ok  validar_zip do ZIP empacotado →", plugin_version())
try:
    updater.validar_zip(os.path.join(RAIZ, "LICENSE"))
    raise AssertionError("validar_zip aceitou arquivo que não é ZIP")
except Exception as e:
    assert not isinstance(e, AssertionError), e
    print("  ok  validar_zip recusa arquivo que não é o plugin")
assert plugin.atualizar_action is not None
plugin.unload()
assert plugin.status_label is None and plugin.action is None
print("\nTUDO OK")
app.exitQgis()
