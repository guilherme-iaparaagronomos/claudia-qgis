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

import claudia_qgis.i18n as i18n  # noqa: E402
from claudia_qgis.plugin import ESTADOS, ClaudiaQgisPlugin, _estado_textos, _normalizar_base  # noqa: E402

# (0.4.2) idioma determinístico no teste: português primeiro, inglês no fim
i18n.idioma = lambda: i18n.PT

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
    assert plugin.action.text() == _estado_textos(estado)[1], (estado, plugin.action.text())
    assert "ClaudIA QGIS" in plugin.status_label.text()
    assert not plugin.action.icon().isNull()
    print("  ok ", estado, "→", plugin.action.text(), "|", plugin.tool_button.styleSheet()[:48])
plugin._estado_mudou("conectado", "x")
assert plugin.action.text() == "ClaudIA · CONECTADO"
plugin._estado_mudou("sem_rede", "HTTP 429")
assert "sem conexão" in plugin.action.text()

# (0.4.2) troca de idioma em tempo de execução: menu e estado retraduzidos
i18n.idioma = lambda: i18n.EN
plugin._aplicar_idioma()
assert plugin.conectar_action.text() == "Connect to the community…", plugin.conectar_action.text()
assert "no connection" in plugin.action.text(), plugin.action.text()
plugin._estado_mudou("conectado", "x")
assert plugin.action.text() == "ClaudIA · CONNECTED", plugin.action.text()
assert "connected to the community" in plugin.status_label.text()
print("  ok  idioma: pt → en retraduz menu, botão e barra de status")
i18n.idioma = lambda: i18n.PT
plugin._aplicar_idioma()
assert plugin.conectar_action.text() == "Conectar à comunidade…"

# (12/10) espanhol e francês também retraduzem na hora
for lang, esperado in ((i18n.ES, "Conectar con la comunidad…"), (i18n.FR, "Se connecter à la communauté…")):
    i18n.idioma = lambda lang=lang: lang
    plugin._aplicar_idioma()
    assert plugin.conectar_action.text() == esperado, plugin.conectar_action.text()
i18n.idioma = lambda: i18n.PT
plugin._aplicar_idioma()
print("  ok  idioma: es e fr retraduzem menu e botão")

# (12/10) "Automático" = o idioma do QGIS (o da instalação/opções) ou, sem escolha, o do sistema;
# língua fora das quatro → inglês. Mexe nas opções do perfil do QGIS e devolve como estavam.
from qgis.core import QgsSettings  # noqa: E402

_s = QgsSettings()
_antes = {k: _s.value(k) for k in ("locale/overrideFlag", "locale/userLocale")}
try:
    for loc, esperado in (
        ("pt_BR", i18n.PT), ("pt_PT", i18n.PT), ("es_AR", i18n.ES), ("es_ES", i18n.ES), ("fr_CA", i18n.FR),
        ("fr_FR", i18n.FR), ("en_US", i18n.EN), ("de_DE", i18n.EN), ("zh_CN", i18n.EN), ("it_IT", i18n.EN),
    ):
        _s.setValue("locale/overrideFlag", True)
        _s.setValue("locale/userLocale", loc)
        assert i18n.idioma_do_qgis() == esperado, (loc, i18n.idioma_do_qgis())
finally:
    for k, v in _antes.items():
        if v is None:
            _s.remove(k)
        else:
            _s.setValue(k, v)
print("  ok  automático: pt/es/fr pelo idioma do QGIS; alemão, chinês, italiano → inglês")

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
