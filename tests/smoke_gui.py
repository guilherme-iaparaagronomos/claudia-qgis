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
# (0.4.5) a linha dos pedidos está nos DOIS menus: o do botão e Complementos → ClaudIA QGIS
_no_menu_complementos = [c.args[1] for c in iface.addPluginToMenu.call_args_list]
assert plugin.plano_action in _no_menu_complementos, "a linha dos pedidos não entrou no menu Complementos"
assert _no_menu_complementos.index(plugin.plano_action) == 1, "logo abaixo de 'ClaudIA · CONECTADO'"
assert plugin.plano_action in plugin.tool_button.menu().actions()
assert "ClaudIA" in plugin.status_label.text()
for estado in ESTADOS:
    plugin._mostrar_estado(estado, "detalhe de teste")
    assert plugin.action.text() == _estado_textos(estado)[1], (estado, plugin.action.text())
    assert "ClaudIA QGIS" in plugin.status_label.text()
    assert not plugin.action.icon().isNull()
    print("  ok ", estado, "→", plugin.action.text(), "|", plugin.tool_button.styleSheet()[:48])
plugin._estado_mudou("conectado", "x")
assert plugin.action.text() == "ClaudIA · CONECTADO"
# (P18) sem acesso: rótulo próprio, UM aviso na barra com o botão dos planos, e o botão abre /planos
from claudia_qgis import plugin as _mod_plugin  # noqa: E402

_abertos = []
_mod_plugin.QDesktopServices.openUrl = lambda url: _abertos.append(url.toString())
iface.messageBar.reset_mock()
plugin._estado_mudou("sem_acesso", "a comunidade respondeu: sem acesso à ClaudIA QGIS")
assert plugin.action.text() == "ClaudIA · sem acesso", plugin.action.text()
assert "não inclui a ClaudIA QGIS" in plugin.status_label.text(), plugin.status_label.text()
assert iface.messageBar.return_value.pushWidget.call_count == 1
plugin._estado_mudou("sem_acesso", "de novo")  # o worker não repete, mas a barra também não
assert iface.messageBar.return_value.pushWidget.call_count == 1
plugin._abrir_planos()
assert _abertos == ["https://comunidade.agronomos.ia.br/planos"], _abertos
plugin._estado_mudou("conectado", "x")
assert plugin.action.text() == "ClaudIA · CONECTADO"
print("  ok  sem acesso: rótulo, 1 aviso com o botão, /planos; volta a conectado")
plugin._estado_mudou("sem_rede", "HTTP 429")
assert "sem conexão" in plugin.action.text()

# (0.4.4) teste por pedidos: o que a comunidade manda aparece no menu, na barra de status e na barra de avisos
plugin._estado_mudou("conectado", "x")
assert not plugin.plano_action.isVisible(), "sem plano informado, a linha do menu fica escondida"
iface.messageBar.reset_mock()
_fim = "2026-11-19T17:00:00+00:00"
plugin._plano_mudou({"tipo": "pedidos", "total": 7, "usados": 3, "restantes": 4, "ate": _fim})
assert plugin.plano_action.isVisible()
assert plugin.plano_action.text() == "Teste grátis: 4 de 7 pedidos restantes · até 19/11", plugin.plano_action.text()
assert "4 de 7 pedidos grátis restantes" in plugin.status_label.text(), plugin.status_label.text()
assert iface.messageBar.return_value.pushInfo.call_count == 0, "com 4 sobrando, nada de aviso"
plugin._plano_mudou({"tipo": "pedidos", "total": 7, "usados": 5, "restantes": 2, "ate": _fim})
plugin._plano_mudou({"tipo": "pedidos", "total": 7, "usados": 5, "restantes": 2, "ate": _fim})
assert iface.messageBar.return_value.pushInfo.call_count == 1, "2 sobrando: um aviso só"
plugin._plano_mudou({"tipo": "pedidos", "total": 7, "usados": 7, "restantes": 0, "ate": _fim})
assert iface.messageBar.return_value.pushWidget.call_count == 1, "0 sobrando: barra com o botão dos planos"
assert "0 de 7 pedidos grátis restantes" in plugin.status_label.text()
plugin._plano_mudou({"tipo": "ilimitado"})
assert plugin.plano_action.text() == "Pedidos ilimitados — a ClaudIA QGIS está no seu plano", plugin.plano_action.text()
assert "pedidos ilimitados" in plugin.status_label.text()
plugin._plano_mudou({"tipo": "dias", "ate": "2026-10-23T02:30:00+00:00"})
assert plugin.plano_action.text() == "Teste grátis até 22/10", plugin.plano_action.text()  # 23h30 de 22/10 em Brasília
plugin._mostrar_estado("conectado", "<b>x</b>")
assert "&lt;b&gt;x&lt;/b&gt;" in plugin.status_label.text(), "o detalhe entra escapado no rótulo HTML"
plugin._plano_mudou({"tipo": "pedidos", "total": 7, "usados": 6, "restantes": 1, "ate": _fim})
i18n.idioma = lambda: i18n.EN
plugin._aplicar_idioma()
assert plugin.plano_action.text() == "Free trial: 1 of 7 requests left · until 11/19", plugin.plano_action.text()
assert "1 of 7 free requests left" in plugin.status_label.text(), plugin.status_label.text()
i18n.idioma = lambda: i18n.PT
plugin._aplicar_idioma()
plugin._desconectar()
assert not plugin.plano_action.isVisible(), "desconectou: a linha do plano some"
print("  ok  pedidos: menu, barra de status, aviso nos 2 últimos, botão no zero, ilimitado, dias, en, desconectar")
plugin._estado_mudou("sem_rede", "HTTP 429")

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
_plano = plugin.plano_action
plugin.unload()
assert plugin.status_label is None and plugin.action is None
assert any(c.args[1] is _plano for c in iface.removePluginMenu.call_args_list), "a linha dos pedidos sai do menu Complementos no unload"
print("\nTUDO OK")
app.exitQgis()
