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

from claudia_qgis.plugin import ESTADOS, ClaudiaQgisPlugin  # noqa: E402

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
plugin.unload()
assert plugin.status_label is None and plugin.action is None
print("\nTUDO OK")
app.exitQgis()
