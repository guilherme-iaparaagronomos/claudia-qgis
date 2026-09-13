# ClaudIA QGIS

**A sua IA (Claude, ChatGPT ou qualquer cliente MCP) operando o QGIS aberto no seu computador — pela comunidade [agrônomo10X](https://comunidade.agronomos.ia.br) (OagronomIA).**

*English summary at the end.*

## O que é

Um plugin do QGIS que conecta o QGIS da sua máquina à comunidade agrônomo10X. A comunidade
expõe um servidor MCP (`ClaudIA QGIS`) para a sua IA; cada ferramenta que a IA chama vira um
comando que este plugin busca na comunidade, executa no seu QGIS (PyQGIS) e devolve.

```
Sua IA (Claude/ChatGPT) ──MCP/OAuth──▶ comunidade agrônomo10X ◀──HTTPS long-poll── plugin ClaudIA QGIS (no seu QGIS)
```

- **Sem instalar Python, sem porta aberta, sem editar arquivo de configuração de IA**: o plugin
  fala HTTPS de saída com a comunidade, como um navegador.
- **120 ferramentas** para a IA: camadas, atributos, edição, seleção, estilos, rótulos,
  Processing (qualquer algoritmo), estatísticas zonais, calculadora raster, layouts e atlas,
  SQL sobre camadas, conexões de banco, render do mapa, e mais.
- **Você manda**: o token do plugin é gerado na sua página da comunidade e pode ser revogado a
  qualquer momento. Comandos que alteram o projeto exigem confirmação da sua IA.

## Instalação

1. **QGIS ≥ 3.28.** Complementos → Gerenciar e instalar complementos → procure **ClaudIA QGIS**
   (ou instale pelo ZIP em *Instalar a partir de um ZIP*).
2. Na comunidade, abra **Soluções → MCP → ClaudIA QGIS** e clique em *Gerar token para um QGIS*.
3. No QGIS, botão da ClaudIA na barra → **Conectar à comunidade…** → cole o token → *Salvar e conectar*.
   O ponto verde no ícone indica "conectado"; a página da comunidade mostra *conectado agora*.
4. Conecte a ClaudIA QGIS na sua IA (a página explica: é o mesmo login da comunidade) e peça:
   *"lista as camadas do meu projeto"*.

Requer conta na comunidade agrônomo10X com a solução ClaudIA QGIS liberada.

## O que o plugin envia

- A cada busca de comando (a cada ~20 s): versão do QGIS, versão do plugin e o **nome** do projeto aberto.
- Para cada comando que a **sua** IA pedir: o resultado dele (dados das camadas pedidas, imagem do mapa…).

Nada sai sem um comando seu. O token fica nas configurações do QGIS (`QgsSettings`, chave
`claudia_qgis/token`); revogue-o na sua página da comunidade se trocar de máquina.

## Desenvolvimento

```
claudia_qgis/
  plugin.py      # botão, menu, janela de conexão, ponte comunidade → executor
  community.py   # long-poll HTTPS numa thread própria (nunca toca no QGIS)
  server.py      # executor: valida {type, params} e chama o handler na thread principal
  handlers/      # os comandos, um módulo por domínio (herdados do QGIS MCP)
  registry.py    # @command + lista de comandos bloqueados em lote
```

- Teste local: copie `claudia_qgis/` para
  `%APPDATA%\QGIS\QGIS3\profiles\default\python\plugins\claudia_qgis` e ative em Complementos.
- Teste sem interface (Python do QGIS): `python-qgis-ltr.bat tests/smoke_headless.py`
  (com `CLAUDIA_QGIS_TOKEN` e `CLAUDIA_QGIS_URL` no ambiente, também conecta à comunidade).
- Empacotar para o repositório oficial: `python empacota.py` → `dist/claudia_qgis-<versão>.zip`.

## Créditos e licença

ClaudIA QGIS é **software livre, GPLv2 ou posterior** (arquivo `LICENSE`).

É um trabalho derivado de **[QGIS MCP](https://github.com/nkarasiak/qgis-mcp)**, de
**Nicolas Karasiak** (plugin sob GPLv2+). Os handlers que executam os comandos dentro do QGIS
(`claudia_qgis/handlers/`), o executor e a infraestrutura de compatibilidade são o trabalho dele;
a ClaudIA QGIS substitui o servidor local por socket pela conexão com a comunidade, traduz a
interface para o português e remove o configurador de clientes MCP. Os arquivos modificados
trazem a nota "Modificado por OagronomIA (2026-09-13)". Obrigado, Nicolas.

O servidor MCP que a comunidade opera é código próprio da OagronomIA e reproduz, uma a uma, as
118 ferramentas do servidor MCP original (MIT) mais 2 comandos do plugin.

---

## English

**ClaudIA QGIS** lets your AI assistant (Claude, ChatGPT or any MCP client) operate the QGIS
running on your computer through the [agrônomo10X](https://comunidade.agronomos.ia.br) community
(OagronomIA, Brazil). The community hosts the MCP server; this plugin long-polls it over HTTPS,
runs each command in your QGIS with PyQGIS and posts the result back. No Python setup, no open
ports. 120 tools: layers, attributes, editing, styling, Processing, zonal stats, layouts, SQL,
rendering. Requires a community account with ClaudIA QGIS enabled.

Free software, GPLv2+. Derived from [QGIS MCP](https://github.com/nkarasiak/qgis-mcp) by Nicolas
Karasiak: the in-QGIS command handlers are his work; ClaudIA QGIS replaces the local socket server
with the community connection and translates the UI to Portuguese.
