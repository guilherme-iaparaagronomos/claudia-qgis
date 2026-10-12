# ClaudIA QGIS

**A sua IA (Claude, ChatGPT ou qualquer cliente MCP) operando o QGIS aberto no seu computador.**
Plugin da comunidade [agrônomo10X](https://www.agronomos.ia.br) (OagronomIA).

*English below.*

## Como conectar

1. **QGIS 3.28 ou mais novo.** Complementos → Gerenciar e instalar complementos → procure
   **ClaudIA QGIS** (marque "Mostrar também os complementos experimentais").
2. Gere o **token de conexão** na sua página da ClaudIA QGIS:
   <https://comunidade.agronomos.ia.br/solucoes/mcp/claudia-qgis>
3. No QGIS: botão da ClaudIA na barra → **Conectar à comunidade…** → cole o token.
4. Na sua IA, adicione o conector `https://comunidade.agronomos.ia.br/api/mcp/qgis`, entre com a
   sua conta da comunidade e peça: *"lista as camadas do meu projeto"*.

É preciso ter conta na comunidade agrônomo10X (plano Pro; conta nova tem 7 dias grátis, de qualquer país).

## O que o plugin envia

Só a versão do QGIS, o nome do projeto aberto e o resultado dos comandos que a **sua** IA pedir.
Sem porta aberta e sem instalar Python: o plugin fala HTTPS de saída com a comunidade. O token
fica nas configurações do QGIS e pode ser revogado na sua página a qualquer momento.

---

## English

**Your AI (Claude, ChatGPT or any MCP client) operating the QGIS open on your computer.**
A plugin of the [agrônomo10X](https://www.agronomos.ia.br) community (OagronomIA, Brazil).

### How to connect

1. **QGIS 3.28 or newer.** Plugins → Manage and Install Plugins → search for **ClaudIA QGIS**
   (tick "Show also experimental plugins").
2. Generate the **connection token** on your ClaudIA QGIS page:
   <https://comunidade.agronomos.ia.br/solucoes/mcp/claudia-qgis>
3. In QGIS: ClaudIA button on the toolbar → **Connect to the community…** → paste the token.
4. In your AI, add the connector `https://comunidade.agronomos.ia.br/api/mcp/qgis`, sign in with
   your community account and ask: *"list the layers in my project"*.

Requires an agrônomo10X community account (Pro plan; new accounts get 7 days free, from any country).

### What the plugin sends

Only the QGIS version, the name of the open project and the results of the commands **your** AI
requests. No open ports and no Python setup: the plugin makes outgoing HTTPS calls to the
community. The token is stored in the QGIS settings and can be revoked on your page at any time.

---

## Desenvolvimento / Development

```
claudia_qgis/
  plugin.py      # botão, menu, janela de conexão, ponte comunidade → executor
  community.py   # long-poll HTTPS numa thread própria (nunca toca no QGIS)
  server.py      # executor: valida {type, params} e chama o handler na thread principal
  handlers/      # os comandos, um módulo por domínio (herdados do QGIS MCP)
  registry.py    # @command + lista de comandos bloqueados em lote
  i18n.py        # textos da interface (inglês e português)
```

- Teste local: copie `claudia_qgis/` para
  `%APPDATA%\QGIS\QGIS3\profiles\default\python\plugins\claudia_qgis` e ative em Complementos.
- Teste sem interface (Python do QGIS): `python-qgis-ltr.bat tests/smoke_headless.py`
  (com `CLAUDIA_QGIS_TOKEN` e `CLAUDIA_QGIS_URL` no ambiente, também conecta à comunidade).
- Empacotar para o repositório oficial: `python empacota.py` → `dist/claudia_qgis-<versão>.zip`.

## Créditos e licença / Credits and license

ClaudIA QGIS é **software livre, GPLv2 ou posterior** (arquivo `LICENSE`). / Free software, GPLv2+.

É um trabalho derivado de **[QGIS MCP](https://github.com/nkarasiak/qgis-mcp)**, de
**Nicolas Karasiak** (plugin sob GPLv2+). Os handlers que executam os comandos dentro do QGIS
(`claudia_qgis/handlers/`), o executor e a infraestrutura de compatibilidade são o trabalho dele;
a ClaudIA QGIS substitui o servidor local por socket pela conexão com a comunidade e remove o
configurador de clientes MCP. Os arquivos modificados trazem a nota "Modificado por OagronomIA".
Obrigado, Nicolas.

O servidor MCP que a comunidade opera é código próprio da OagronomIA e reproduz as ferramentas do
servidor MCP original (MIT), mais alguns comandos próprios.

Derived from [QGIS MCP](https://github.com/nkarasiak/qgis-mcp) by Nicolas Karasiak: the in-QGIS
command handlers are his work; ClaudIA QGIS replaces the local socket server with the community
connection.
