"""Textos da interface do plugin em INGLÊS (base), PORTUGUÊS DO BRASIL, ESPANHOL e FRANCÊS.

Por que um dicionário e não o ``.qm`` do Qt: a instalação padrão do QGIS no
Windows não traz ``lrelease``/``pylupdate``, e são ~60 textos — um módulo
Python é o suficiente e não exige etapa de build. O que vai para a IA do
usuário (envelopes de resultado, mensagens de erro dos handlers) NÃO passa
por aqui: fica em português por desenho, a IA traduz sozinha.

Idioma: ``claudia_qgis/idioma`` em QgsSettings (``auto`` | ``en`` | ``pt_BR`` |
``es`` | ``fr``). Em ``auto`` vale o idioma do QGIS (``locale/userLocale`` quando o
usuário sobrescreve, senão o do sistema): ``pt*`` → português, ``es*`` → espanhol,
``fr*`` → francês, qualquer outro → inglês (12/10/2026: as quatro línguas do site).
O brasileiro com QGIS em inglês pode forçar o português na janela de conexão.

Modificado por OagronomIA (2026-09-28) — GPLv2+.
"""

from __future__ import annotations

from .constants import SETTINGS_PREFIX

AUTO = "auto"
EN = "en"
PT = "pt_BR"
ES = "es"
FR = "fr"
IDIOMAS = (AUTO, PT, EN, ES, FR)

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
    "conectar.idioma.es": "Español",
    "conectar.idioma.fr": "Français",
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
        "<p>Site: <a href='https://www.agronomos.ia.br/en/'>www.agronomos.ia.br</a></p>"
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
        "check your internet connection."
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
    "conectar.idioma.es": "Español",
    "conectar.idioma.fr": "Français",
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
        "confira a sua conexão com a internet."
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

# (12/10) espanhol e francês: as mesmas chaves (tests/i18n_check.py)
_ES = {
    'estado.parado.rotulo': 'ClaudIA QGIS',
    'estado.parado.texto': 'desconectado — haz clic en el botón de ClaudIA para conectar',
    'estado.conectando.rotulo': 'ClaudIA · conectando…',
    'estado.conectando.texto': 'conectando con la comunidad…',
    'estado.conectado.rotulo': 'ClaudIA · CONECTADO',
    'estado.conectado.texto': 'conectado a la comunidad — tu IA ya puede operar este QGIS',
    'estado.sem_rede.rotulo': 'ClaudIA · sin conexión',
    'estado.sem_rede.texto': 'sin conexión con la comunidad (reintentando)',
    'estado.token_invalido.rotulo': 'ClaudIA · token rechazado',
    'estado.token_invalido.texto': 'token rechazado — genera uno nuevo en la comunidad',
    'estado.tooltip': 'ClaudIA QGIS — {texto}',
    'estado.comandos': '{n} comando(s) · último: {tipo}',
    'menu.tooltip': 'ClaudIA QGIS — haz clic para conectar con la comunidad',
    'menu.conectar': 'Conectar con la comunidad…',
    'menu.pagina': 'Mi página en la comunidad',
    'menu.atualizar': 'Actualizar el complemento…',
    'menu.sobre': 'Acerca de ClaudIA QGIS',
    'conectar.titulo': 'ClaudIA QGIS — Conectar con la comunidad',
    'conectar.intro': '<p>Genera un <b>token del complemento</b> en tu página de la comunidad agrônomo10X y pégalo abajo. El token identifica TU QGIS: tu IA (Claude, ChatGPT…) conversa con la comunidad, y la comunidad habla con este QGIS.</p>',
    'conectar.abrir_pagina': 'Abrir mi página de la comunidad para generar el token',
    'conectar.token': 'Token del complemento:',
    'conectar.exibir_codigo': 'Mostrar el token',
    'conectar.autostart': 'Conectar automáticamente al abrir QGIS',
    'conectar.idioma': 'Idioma del complemento:',
    'conectar.idioma.auto': 'Automático (sigue a QGIS)',
    'conectar.idioma.pt': 'Português (Brasil)',
    'conectar.idioma.en': 'English',
    'conectar.idioma.es': 'Español',
    'conectar.idioma.fr': 'Français',
    'conectar.avancado': 'Avanzado',
    'conectar.endereco': 'Dirección de la comunidad:',
    'conectar.endereco_dica': 'Cámbiala solo si el equipo de la comunidad lo pide (entorno de pruebas).',
    'conectar.privacidade': '<small>Lo que el complemento envía a la comunidad: la versión de QGIS, el nombre del proyecto abierto y el resultado de los comandos que TU IA pida (datos de las capas, imágenes del mapa). Nada sale sin una orden tuya. Revoca el token en tu página cuando quieras.</small>',
    'conectar.salvar': 'Guardar y conectar',
    'conectar.cancelar': 'Cancelar',
    'boasvindas.titulo': 'ClaudIA QGIS instalada',
    'boasvindas.corpo': "<h2>ClaudIA QGIS</h2><p>Tu IA (Claude, ChatGPT…) ahora puede ver y operar este QGIS a través de la comunidad <b>agrônomo10X</b>.</p><p><b>Tres pasos:</b></p><ol><li>Abre tu página de <b>ClaudIA QGIS</b> en la comunidad (botón de abajo) y genera el <b>token de conexión</b>.</li><li>Aquí, haz clic en el botón de ClaudIA en la barra → <b>Conectar con la comunidad…</b> y pega el token.</li><li>En tu IA, agrega el conector <b>https://comunidade.agronomos.ia.br/api/mcp/qgis</b>, entra con tu cuenta de la comunidad y pide: <i>“lista las capas de mi proyecto”</i>.</li></ol><p><small>Software libre (GPLv2+), derivado de QGIS MCP de Nicolas Karasiak. Código fuente: <a href='{repo}'>{repo}</a></small></p>",
    'boasvindas.abrir': 'Abrir la comunidad',
    'boasvindas.conectar': 'Conectar ahora',
    'boasvindas.depois': 'Más tarde',
    'sobre.titulo': 'Acerca de ClaudIA QGIS',
    'sobre.corpo': "<h3>ClaudIA QGIS {versao}</h3><p>Complemento de la comunidad <b>agrônomo10X</b> (OagronomIA): tu IA opera QGIS.</p><p>Sitio: <a href='https://www.agronomos.ia.br/es/'>www.agronomos.ia.br</a></p><p>Código fuente y licencia (GPLv2+): <a href='{repo}'>{repo}</a></p><p>Derivado de <b>QGIS MCP</b>, de Nicolas Karasiak (GPLv2+): <a href='{upstream}'>{upstream}</a>. Los handlers que ejecutan los comandos dentro de QGIS son su trabajo; ClaudIA QGIS sustituye el servidor local por una conexión con la comunidad.</p><p>Estado: <b>{estado}</b> {detalhe} · {n} comando(s) en esta sesión</p>",
    'sobre.fechar': 'Cerrar',
    'msg.atualizado': 'Complemento actualizado a la versión {versao}.',
    'msg.conectando_log': 'Conectando con la comunidad en {base}',
    'msg.worker_demorou': 'La conexión tardó en detenerse; termina en segundo plano.',
    'msg.conectado': 'Conectado a la comunidad. Pídele a tu IA: “lista las capas de mi proyecto”.',
    'msg.sem_rede': 'No pude comunicarme con la comunidad ({detalhe}). Seguiré intentando; revisa tu conexión a internet.',
    'msg.token_recusado': 'Token rechazado por la comunidad. Genera un token nuevo en tu página y pégalo en Conectar con la comunidad…',
    'upd.disponivel': 'Versión {versao} del complemento disponible (tienes la {atual}).',
    'upd.botao': 'Actualizar ahora',
    'upd.disponivel_log': 'Versión {versao} disponible en {url} ({erro})',
    'upd.consulta_falhou': 'No pude consultar la versión más reciente: {erro}',
    'upd.ja_atual': 'Ya tienes la versión más reciente ({versao}).',
    'upd.baixando': 'Descargando la versión {versao}…',
    'upd.falhou_log': 'La actualización falló: {erro}',
    'upd.baixar_falhou': 'No pude descargar la actualización: {erro}. Descárgala en {url}.',
    'upd.instalar_falhou': 'La actualización falló ({erro}). Instálala desde el ZIP en Complementos → Instalar a partir de ZIP.',
    'upd.so_https': 'las actualizaciones solo se descargan por https',
    'upd.zip_grande': 'ZIP más grande de lo esperado — cancelado',
    'upd.zip_invalido': 'el ZIP no contiene el complemento claudia_qgis',
    'upd.http': 'HTTP {status} al buscar {onde}',
    'upd.redirecionamentos': 'demasiadas redirecciones',
    'worker.conectando': 'conectando con la comunidad…',
    'worker.token_recusado': 'token rechazado por la comunidad (revocado o incorrecto)',
    'worker.tentando': '{erro} — reintentando en {segundos} s',
    'worker.conectado': 'conectado a la comunidad',
    'worker.token_resultado': 'token rechazado al enviar el resultado',
    'worker.envio_falhou': 'no pude enviar el resultado: {erro}',
    'worker.desconectado': 'desconectado',
    'worker.html': 'página HTML (¿bloqueo de red/WAF?)',
    'worker.http': 'HTTP {status} en {caminho}: {trecho}',
    'worker.nao_json': 'la respuesta no es JSON en {caminho}: {erro}',
}

_FR = {
    'estado.parado.rotulo': 'ClaudIA QGIS',
    'estado.parado.texto': 'déconnecté — cliquez sur le bouton ClaudIA pour vous connecter',
    'estado.conectando.rotulo': 'ClaudIA · connexion…',
    'estado.conectando.texto': 'connexion à la communauté…',
    'estado.conectado.rotulo': 'ClaudIA · CONNECTÉ',
    'estado.conectado.texto': 'connecté à la communauté — votre IA peut maintenant piloter ce QGIS',
    'estado.sem_rede.rotulo': 'ClaudIA · pas de connexion',
    'estado.sem_rede.texto': 'pas de connexion avec la communauté (nouvelle tentative)',
    'estado.token_invalido.rotulo': 'ClaudIA · jeton refusé',
    'estado.token_invalido.texto': 'jeton refusé — générez-en un nouveau dans la communauté',
    'estado.tooltip': 'ClaudIA QGIS — {texto}',
    'estado.comandos': '{n} commande(s) · dernière\xa0: {tipo}',
    'menu.tooltip': 'ClaudIA QGIS — cliquez pour vous connecter à la communauté',
    'menu.conectar': 'Se connecter à la communauté…',
    'menu.pagina': 'Ma page dans la communauté',
    'menu.atualizar': "Mettre à jour l'extension…",
    'menu.sobre': 'À propos de ClaudIA QGIS',
    'conectar.titulo': 'ClaudIA QGIS — Se connecter à la communauté',
    'conectar.intro': "<p>Générez un <b>jeton de l'extension</b> sur votre page de la communauté agrônomo10X et collez-le ci-dessous. Le jeton identifie VOTRE QGIS\xa0: votre IA (Claude, ChatGPT…) dialogue avec la communauté, et la communauté parle à ce QGIS.</p>",
    'conectar.abrir_pagina': 'Ouvrir ma page de la communauté pour générer le jeton',
    'conectar.token': "Jeton de l'extension\xa0:",
    'conectar.exibir_codigo': 'Afficher le jeton',
    'conectar.autostart': "Se connecter automatiquement à l'ouverture de QGIS",
    'conectar.idioma': "Langue de l'extension\xa0:",
    'conectar.idioma.auto': 'Automatique (suit QGIS)',
    'conectar.idioma.pt': 'Português (Brasil)',
    'conectar.idioma.en': 'English',
    'conectar.idioma.es': 'Español',
    'conectar.idioma.fr': 'Français',
    'conectar.avancado': 'Avancé',
    'conectar.endereco': 'Adresse de la communauté\xa0:',
    'conectar.endereco_dica': "À modifier seulement si l'équipe de la communauté le demande (environnement de test).",
    'conectar.privacidade': "<small>Ce que l'extension envoie à la communauté\xa0: la version de QGIS, le nom du projet ouvert et le résultat des commandes que VOTRE IA demande (données des couches, images de la carte). Rien ne sort sans une commande de votre part. Révoquez le jeton sur votre page à tout moment.</small>",
    'conectar.salvar': 'Enregistrer et connecter',
    'conectar.cancelar': 'Annuler',
    'boasvindas.titulo': 'ClaudIA QGIS installée',
    'boasvindas.corpo': "<h2>ClaudIA QGIS</h2><p>Votre IA (Claude, ChatGPT…) peut maintenant voir et piloter ce QGIS grâce à la communauté <b>agrônomo10X</b>.</p><p><b>Trois étapes\xa0:</b></p><ol><li>Ouvrez votre page <b>ClaudIA QGIS</b> dans la communauté (bouton ci-dessous) et générez le <b>jeton de connexion</b>.</li><li>Ici, cliquez sur le bouton ClaudIA dans la barre d'outils → <b>Se connecter à la communauté…</b> et collez le jeton.</li><li>Dans votre IA, ajoutez le connecteur <b>https://comunidade.agronomos.ia.br/api/mcp/qgis</b>, connectez-vous avec votre compte de la communauté et demandez\xa0: <i>«\xa0liste les couches de mon projet\xa0»</i>.</li></ol><p><small>Logiciel libre (GPLv2+), dérivé de QGIS MCP de Nicolas Karasiak. Code source\xa0: <a href='{repo}'>{repo}</a></small></p>",
    'boasvindas.abrir': 'Ouvrir la communauté',
    'boasvindas.conectar': 'Se connecter maintenant',
    'boasvindas.depois': 'Plus tard',
    'sobre.titulo': 'À propos de ClaudIA QGIS',
    'sobre.corpo': "<h3>ClaudIA QGIS {versao}</h3><p>Extension de la communauté <b>agrônomo10X</b> (OagronomIA)\xa0: votre IA pilote QGIS.</p><p>Site\xa0: <a href='https://www.agronomos.ia.br/fr/'>www.agronomos.ia.br</a></p><p>Code source et licence (GPLv2+)\xa0: <a href='{repo}'>{repo}</a></p><p>Dérivée de <b>QGIS MCP</b>, de Nicolas Karasiak (GPLv2+)\xa0: <a href='{upstream}'>{upstream}</a>. Les handlers qui exécutent les commandes dans QGIS sont son travail\xa0; ClaudIA QGIS remplace le serveur local par une connexion à la communauté.</p><p>État\xa0: <b>{estado}</b> {detalhe} · {n} commande(s) dans cette session</p>",
    'sobre.fechar': 'Fermer',
    'msg.atualizado': 'Extension mise à jour vers la version {versao}.',
    'msg.conectando_log': 'Connexion à la communauté sur {base}',
    'msg.worker_demorou': "La connexion a mis du temps à s'arrêter\xa0; elle se termine en arrière-plan.",
    'msg.conectado': 'Connecté à la communauté. Demandez à votre IA\xa0: «\xa0liste les couches de mon projet\xa0».',
    'msg.sem_rede': "Impossible de joindre la communauté ({detalhe}). Je continue d'essayer\xa0; vérifiez votre connexion Internet.",
    'msg.token_recusado': 'Jeton refusé par la communauté. Générez un nouveau jeton sur votre page et collez-le dans Se connecter à la communauté…',
    'upd.disponivel': "Version {versao} de l'extension disponible (vous avez la {atual}).",
    'upd.botao': 'Mettre à jour',
    'upd.disponivel_log': 'Version {versao} disponible sur {url} ({erro})',
    'upd.consulta_falhou': 'Impossible de vérifier la dernière version\xa0: {erro}',
    'upd.ja_atual': 'Vous avez déjà la dernière version ({versao}).',
    'upd.baixando': 'Téléchargement de la version {versao}…',
    'upd.falhou_log': 'La mise à jour a échoué\xa0: {erro}',
    'upd.baixar_falhou': 'Impossible de télécharger la mise à jour\xa0: {erro}. Téléchargez-la sur {url}.',
    'upd.instalar_falhou': 'La mise à jour a échoué ({erro}). Installez-la depuis le ZIP dans Extensions → Installer depuis un ZIP.',
    'upd.so_https': "les mises à jour ne sont téléchargées qu'en https",
    'upd.zip_grande': 'ZIP plus grand que prévu — annulé',
    'upd.zip_invalido': "le ZIP ne contient pas l'extension claudia_qgis",
    'upd.http': 'HTTP {status} en récupérant {onde}',
    'upd.redirecionamentos': 'trop de redirections',
    'worker.conectando': 'connexion à la communauté…',
    'worker.token_recusado': 'jeton refusé par la communauté (révoqué ou incorrect)',
    'worker.tentando': '{erro} — nouvelle tentative dans {segundos} s',
    'worker.conectado': 'connecté à la communauté',
    'worker.token_resultado': "jeton refusé lors de l'envoi du résultat",
    'worker.envio_falhou': "impossible d'envoyer le résultat\xa0: {erro}",
    'worker.desconectado': 'déconnecté',
    'worker.html': 'page HTML (blocage réseau/WAF\xa0?)',
    'worker.http': 'HTTP {status} sur {caminho}\xa0: {trecho}',
    'worker.nao_json': "la réponse n'est pas du JSON sur {caminho}\xa0: {erro}",
}

DICIONARIOS = {EN: _EN, PT: _PT, ES: _ES, FR: _FR}
# paridade das chaves é conferida em tests/i18n_check.py (sem assert aqui: Bandit B101)


def idioma_configurado() -> str:
    """O que está salvo: ``auto`` (padrão), ``en``, ``pt_BR``, ``es`` ou ``fr``."""
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
    nome = nome.lower()
    if nome.startswith("pt"):
        return PT
    if nome.startswith("es"):
        return ES
    if nome.startswith("fr"):
        return FR
    return EN


def idioma() -> str:
    """Idioma em vigor para os textos: a escolha do usuário ou, em auto, o do QGIS."""
    escolhido = idioma_configurado()
    return escolhido if escolhido in (EN, PT, ES, FR) else idioma_do_qgis()


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
