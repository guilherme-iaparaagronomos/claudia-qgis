"""Textos da interface do plugin em INGLÊS (base) e PORTUGUÊS DO BRASIL.

Por que um dicionário e não o ``.qm`` do Qt: a instalação padrão do QGIS no
Windows não traz ``lrelease``/``pylupdate``, e são ~60 textos — um módulo
Python é o suficiente e não exige etapa de build. O que vai para a IA do
usuário (envelopes de resultado, mensagens de erro dos handlers) NÃO passa
por aqui: fica em português por desenho, a IA traduz sozinha.

Idioma: ``claudia_qgis/idioma`` em QgsSettings (``auto`` | ``en`` | ``pt_BR``).
Em ``auto`` vale o idioma do QGIS (``locale/userLocale`` quando o usuário
sobrescreve, senão o do sistema): ``pt*`` → português, qualquer outro →
inglês. Assim quem roda o QGIS em francês ou espanhol vê inglês, e o
brasileiro com QGIS em inglês pode forçar o português na janela de conexão.

Modificado por OagronomIA (2026-09-28) — GPLv2+.
"""

from __future__ import annotations

from .constants import SETTINGS_PREFIX

AUTO = "auto"
EN = "en"
PT = "pt_BR"
IDIOMAS = (AUTO, PT, EN)

_EN = {
    # estados (rótulo no botão, texto na barra de status)
    "estado.parado.rotulo": "ClaudIA QGIS",
    "estado.parado.texto": "disconnected — click the ClaudIA button to connect",
    "estado.conectando.rotulo": "ClaudIA · connecting…",
    "estado.conectando.texto": "connecting to the community…",
    "estado.conectado.rotulo": "ClaudIA · CONNECTED",
    "estado.conectado.texto": "connected to the community — your AI can now operate this QGIS",
    "estado.sem_rede.rotulo": "ClaudIA · no connection",
    "estado.sem_rede.texto": "no connection to the community (retrying)",
    "estado.token_invalido.rotulo": "ClaudIA · token rejected",
    "estado.token_invalido.texto": "token rejected — generate a new one in the community",
    "estado.tooltip": "ClaudIA QGIS — {texto}",
    "estado.comandos": "{n} command(s) · last: {tipo}",
    # menu / botão
    "menu.tooltip": "ClaudIA QGIS — click to connect to the community",
    "menu.conectar": "Connect to the community…",
    "menu.pagina": "My page in the community",
    "menu.atualizar": "Update the plugin…",
    "menu.sobre": "About ClaudIA QGIS",
    # janela de conexão
    "conectar.titulo": "ClaudIA QGIS — Connect to the community",
    "conectar.intro": (
        "<p>Generate a <b>plugin token</b> on your agrônomo10X community page and paste it "
        "below. The token identifies YOUR QGIS: your AI (Claude, ChatGPT…) talks to the "
        "community, and the community talks to this QGIS.</p>"
    ),
    "conectar.abrir_pagina": "Open my community page to generate the token",
    "conectar.token": "Plugin token:",
    "conectar.exibir_codigo": "Show the token",
    "conectar.autostart": "Connect automatically when QGIS opens",
    "conectar.idioma": "Plugin language:",
    "conectar.idioma.auto": "Automatic (follows QGIS)",
    "conectar.idioma.pt": "Português (Brasil)",
    "conectar.idioma.en": "English",
    "conectar.avancado": "Advanced",
    "conectar.endereco": "Community address:",
    "conectar.endereco_dica": "Only change this if the community team asks you to (test environment).",
    "conectar.privacidade": (
        "<small>What the plugin sends to the community: the QGIS version, the name of the open "
        "project and the results of the commands YOUR AI requests (layer data, map images). "
        "Nothing leaves without a command from you. Revoke the token on your page at any time.</small>"
    ),
    "conectar.salvar": "Save and connect",
    "conectar.cancelar": "Cancel",
    # boas-vindas
    "boasvindas.titulo": "ClaudIA QGIS installed",
    "boasvindas.corpo": (
        "<h2>ClaudIA QGIS</h2>"
        "<p>Your AI (Claude, ChatGPT…) can now see and operate this QGIS through the "
        "<b>agrônomo10X</b> community.</p>"
        "<p><b>Three steps:</b></p>"
        "<ol>"
        "<li>Open your <b>ClaudIA QGIS</b> page in the community (button below) and generate the "
        "<b>connection token</b>.</li>"
        "<li>Here, click the ClaudIA button on the toolbar → <b>Connect to the community…</b> and paste the token.</li>"
        "<li>In your AI, add the connector <b>https://comunidade.agronomos.ia.br/api/mcp/qgis</b>, "
        "sign in with your community account and ask: <i>“list the layers in my project”</i>.</li>"
        "</ol>"
        "<p><small>Free software (GPLv2+), derived from QGIS MCP by Nicolas Karasiak. "
        "Source code: <a href='{repo}'>{repo}</a></small></p>"
    ),
    "boasvindas.abrir": "Open the community",
    "boasvindas.conectar": "Connect now",
    "boasvindas.depois": "Later",
    # sobre
    "sobre.titulo": "About ClaudIA QGIS",
    "sobre.corpo": (
        "<h3>ClaudIA QGIS {versao}</h3>"
        "<p>Plugin of the <b>agrônomo10X</b> community (OagronomIA): your AI operates QGIS.</p>"
        "<p>Site: <a href='https://www.agronomos.ia.br'>www.agronomos.ia.br</a></p>"
        "<p>Source code and license (GPLv2+): <a href='{repo}'>{repo}</a></p>"
        "<p>Derived from <b>QGIS MCP</b> by Nicolas Karasiak (GPLv2+): "
        "<a href='{upstream}'>{upstream}</a>. The handlers that run the commands inside QGIS "
        "are his work; ClaudIA QGIS replaces the local socket server with the community connection.</p>"
        "<p>State: <b>{estado}</b> {detalhe} · {n} command(s) this session</p>"
    ),
    "sobre.fechar": "Close",
    # mensagens
    "msg.atualizado": "Plugin updated to version {versao}.",
    "msg.conectando_log": "Connecting to the community at {base}",
    "msg.worker_demorou": "The worker took too long to stop; it finishes in the background.",
    "msg.conectado": "Connected to the community. Ask your AI: “list the layers in my project”.",
    "msg.sem_rede": (
        "Could not reach the community ({detalhe}). I will keep trying; "
        "check the address in Connect to the community… → Advanced."
    ),
    "msg.token_recusado": (
        "Token rejected by the community. Generate a new token on your page and paste it in "
        "Connect to the community…"
    ),
    # atualização
    "upd.disponivel": "Plugin version {versao} available (you are on {atual}).",
    "upd.botao": "Update now",
    "upd.disponivel_log": "Version {versao} available at {url} ({erro})",
    "upd.consulta_falhou": "Could not check the latest version: {erro}",
    "upd.ja_atual": "You are already on the latest version ({versao}).",
    "upd.baixando": "Downloading version {versao}…",
    "upd.falhou_log": "Update failed: {erro}",
    "upd.baixar_falhou": "Could not download the update: {erro}. Download it at {url}.",
    "upd.instalar_falhou": "The update failed ({erro}). Install it from the ZIP in Plugins → Install from ZIP.",
    "upd.so_https": "updates are only downloaded over https",
    "upd.zip_grande": "ZIP larger than expected — aborted",
    "upd.zip_invalido": "the ZIP does not contain the claudia_qgis plugin",
    "upd.http": "HTTP {status} while fetching {onde}",
    "upd.redirecionamentos": "too many redirects",
    # cliente da comunidade (worker)
    "worker.conectando": "connecting to the community…",
    "worker.token_recusado": "token rejected by the community (revoked or wrong)",
    "worker.tentando": "{erro} — retrying in {segundos} s",
    "worker.conectado": "connected to the community",
    "worker.token_resultado": "token rejected while sending the result",
    "worker.envio_falhou": "could not send the result: {erro}",
    "worker.desconectado": "disconnected",
    "worker.html": "HTML page (network block/WAF?)",
    "worker.http": "HTTP {status} at {caminho}: {trecho}",
    "worker.nao_json": "response is not JSON at {caminho}: {erro}",
}

_PT = {
    "estado.parado.rotulo": "ClaudIA QGIS",
    "estado.parado.texto": "desconectado — clique no botão da ClaudIA para conectar",
    "estado.conectando.rotulo": "ClaudIA · conectando…",
    "estado.conectando.texto": "conectando à comunidade…",
    "estado.conectado.rotulo": "ClaudIA · CONECTADO",
    "estado.conectado.texto": "conectado à comunidade — a sua IA já pode operar este QGIS",
    "estado.sem_rede.rotulo": "ClaudIA · sem conexão",
    "estado.sem_rede.texto": "sem conexão com a comunidade (tentando de novo)",
    "estado.token_invalido.rotulo": "ClaudIA · token recusado",
    "estado.token_invalido.texto": "token recusado — gere outro na comunidade",
    "estado.tooltip": "ClaudIA QGIS — {texto}",
    "estado.comandos": "{n} comando(s) · último: {tipo}",
    "menu.tooltip": "ClaudIA QGIS — clique para conectar à comunidade",
    "menu.conectar": "Conectar à comunidade…",
    "menu.pagina": "Minha página na comunidade",
    "menu.atualizar": "Atualizar o plugin…",
    "menu.sobre": "Sobre a ClaudIA QGIS",
    "conectar.titulo": "ClaudIA QGIS — Conectar à comunidade",
    "conectar.intro": (
        "<p>Gere um <b>token do plugin</b> na sua página da comunidade agrônomo10X "
        "e cole abaixo. O token identifica o SEU QGIS: a sua IA (Claude, ChatGPT…) "
        "conversa com a comunidade, e a comunidade fala com este QGIS.</p>"
    ),
    "conectar.abrir_pagina": "Abrir minha página na comunidade para gerar o token",
    "conectar.token": "Token do plugin:",
    "conectar.exibir_codigo": "Mostrar o token",
    "conectar.autostart": "Conectar sozinho quando o QGIS abrir",
    "conectar.idioma": "Idioma do plugin:",
    "conectar.idioma.auto": "Automático (segue o QGIS)",
    "conectar.idioma.pt": "Português (Brasil)",
    "conectar.idioma.en": "English",
    "conectar.avancado": "Avançado",
    "conectar.endereco": "Endereço da comunidade:",
    "conectar.endereco_dica": "Só mude se a equipe da comunidade pedir (ambiente de testes).",
    "conectar.privacidade": (
        "<small>O que o plugin envia à comunidade: a versão do QGIS, o nome do projeto aberto e o "
        "resultado dos comandos que a SUA IA pedir (dados das camadas, imagens do mapa). "
        "Nada sai sem um comando seu. Revogue o token na sua página a qualquer momento.</small>"
    ),
    "conectar.salvar": "Salvar e conectar",
    "conectar.cancelar": "Cancelar",
    "boasvindas.titulo": "ClaudIA QGIS instalada",
    "boasvindas.corpo": (
        "<h2>ClaudIA QGIS</h2>"
        "<p>A sua IA (Claude, ChatGPT…) passa a enxergar e operar este QGIS pela "
        "comunidade <b>agrônomo10X</b>.</p>"
        "<p><b>Três passos:</b></p>"
        "<ol>"
        "<li>Abra a sua página da <b>ClaudIA QGIS</b> na comunidade (botão abaixo) e gere o "
        "<b>token de conexão</b>.</li>"
        "<li>Aqui, clique no botão da ClaudIA na barra → <b>Conectar à comunidade…</b> e cole o token.</li>"
        "<li>Na sua IA, adicione o conector <b>https://comunidade.agronomos.ia.br/api/mcp/qgis</b>, "
        "entre com a sua conta da comunidade e peça: <i>“lista as camadas do meu projeto”</i>.</li>"
        "</ol>"
        "<p><small>Software livre (GPLv2+), derivado do QGIS MCP de Nicolas Karasiak. "
        "Código-fonte: <a href='{repo}'>{repo}</a></small></p>"
    ),
    "boasvindas.abrir": "Abrir a comunidade",
    "boasvindas.conectar": "Conectar agora",
    "boasvindas.depois": "Depois",
    "sobre.titulo": "Sobre a ClaudIA QGIS",
    "sobre.corpo": (
        "<h3>ClaudIA QGIS {versao}</h3>"
        "<p>Plugin da comunidade <b>agrônomo10X</b> (OagronomIA): a sua IA opera o QGIS.</p>"
        "<p>Site: <a href='https://www.agronomos.ia.br'>www.agronomos.ia.br</a></p>"
        "<p>Código-fonte e licença (GPLv2+): <a href='{repo}'>{repo}</a></p>"
        "<p>Derivado de <b>QGIS MCP</b>, de Nicolas Karasiak (GPLv2+): "
        "<a href='{upstream}'>{upstream}</a>. Os handlers que executam os comandos "
        "no QGIS são o trabalho dele; a ClaudIA QGIS troca o servidor local por uma conexão "
        "com a comunidade.</p>"
        "<p>Estado: <b>{estado}</b> {detalhe} · {n} comando(s) nesta sessão</p>"
    ),
    "sobre.fechar": "Fechar",
    "msg.atualizado": "Plugin atualizado para a versão {versao}.",
    "msg.conectando_log": "Conectando à comunidade em {base}",
    "msg.worker_demorou": "O worker demorou a parar; termina em segundo plano.",
    "msg.conectado": "Conectado à comunidade. Peça à sua IA: “lista as camadas do meu projeto”.",
    "msg.sem_rede": (
        "Não consegui falar com a comunidade ({detalhe}). Vou continuar tentando; "
        "confira o endereço em Conectar à comunidade… → Avançado."
    ),
    "msg.token_recusado": (
        "Token recusado pela comunidade. Gere um token novo na sua página e cole em "
        "Conectar à comunidade…"
    ),
    "upd.disponivel": "Versão {versao} do plugin disponível (você está na {atual}).",
    "upd.botao": "Atualizar agora",
    "upd.disponivel_log": "Versão {versao} disponível em {url} ({erro})",
    "upd.consulta_falhou": "Não consegui consultar a versão mais recente: {erro}",
    "upd.ja_atual": "Você já está na versão mais recente ({versao}).",
    "upd.baixando": "Baixando a versão {versao}…",
    "upd.falhou_log": "Atualização falhou: {erro}",
    "upd.baixar_falhou": "Não consegui baixar a atualização: {erro}. Baixe em {url}.",
    "upd.instalar_falhou": "A atualização falhou ({erro}). Instale pelo ZIP em Complementos → Instalar a partir de um ZIP.",
    "upd.so_https": "só baixo atualização por https",
    "upd.zip_grande": "ZIP maior que o esperado — abortei",
    "upd.zip_invalido": "o ZIP não contém o plugin claudia_qgis",
    "upd.http": "HTTP {status} ao buscar {onde}",
    "upd.redirecionamentos": "redirecionamentos demais",
    "worker.conectando": "conectando à comunidade…",
    "worker.token_recusado": "token recusado pela comunidade (revogado ou errado)",
    "worker.tentando": "{erro} — tentando de novo em {segundos} s",
    "worker.conectado": "conectado à comunidade",
    "worker.token_resultado": "token recusado ao enviar o resultado",
    "worker.envio_falhou": "não consegui enviar o resultado: {erro}",
    "worker.desconectado": "desconectado",
    "worker.html": "página HTML (bloqueio de rede/WAF?)",
    "worker.http": "HTTP {status} em {caminho}: {trecho}",
    "worker.nao_json": "resposta não é JSON em {caminho}: {erro}",
}

DICIONARIOS = {EN: _EN, PT: _PT}
# paridade das chaves é conferida em tests/i18n_check.py (sem assert aqui: Bandit B101)


def idioma_configurado() -> str:
    """O que está salvo: ``auto`` (padrão), ``en`` ou ``pt_BR``."""
    try:
        from qgis.core import QgsSettings

        valor = str(QgsSettings().value(f"{SETTINGS_PREFIX}/idioma", AUTO) or AUTO)
    except Exception:
        valor = AUTO
    return valor if valor in IDIOMAS else AUTO


def definir_idioma(valor: str) -> None:
    from qgis.core import QgsSettings

    QgsSettings().setValue(f"{SETTINGS_PREFIX}/idioma", valor if valor in IDIOMAS else AUTO)


def idioma_do_qgis() -> str:
    """Idioma efetivo do QGIS: o sobrescrito nas opções, senão o do sistema."""
    try:
        from qgis.core import QgsSettings
        from qgis.PyQt.QtCore import QLocale

        s = QgsSettings()
        if s.value("locale/overrideFlag", False, type=bool):
            nome = str(s.value("locale/userLocale", "") or "")
        else:
            nome = QLocale.system().name()
    except Exception:
        nome = ""
    return PT if nome.lower().startswith("pt") else EN


def idioma() -> str:
    """Idioma em vigor para os textos: a escolha do usuário ou, em auto, o do QGIS."""
    escolhido = idioma_configurado()
    return escolhido if escolhido in (EN, PT) else idioma_do_qgis()


def t(chave: str, lang: str | None = None, **campos) -> str:
    """Texto no idioma em vigor (ou em ``lang``), com ``{campos}`` preenchidos.

    Chave desconhecida devolve a própria chave — nunca lança na interface.
    """
    d = DICIONARIOS.get(lang or idioma(), _EN)
    texto = d.get(chave) or _EN.get(chave) or chave
    if campos:
        try:
            return texto.format(**campos)
        except (KeyError, IndexError, ValueError):
            return texto
    return texto
