# Changelog — ClaudIA QGIS

Changes waiting for the next version go under **Unreleased** (branch `proxima`). When a version is
published, that section gets the version number and is copied into the `changelog` of
`claudia_qgis/metadata.txt` (the text the QGIS plugin portal shows).

As mudanças que esperam a próxima versão ficam em **Unreleased** (ramo `proxima`). No dia de
publicar, a seção ganha o número da versão e vai para o `changelog` do `metadata.txt`.

## Unreleased

Nothing yet.

### Planned for the next version (not built yet) / Previsto para a próxima versão (ainda não feito)

- "Your AI is not connected yet" notice. Pasting the token only connects QGIS to the community: the
  AI (Claude, ChatGPT or another MCP-compatible AI) still has to be connected to the ClaudIA QGIS
  connector, and many people stop before that step. When the community tells the plugin that the
  account has no AI connected yet, the plugin should say so right after it connects: a message in
  the message bar and a line in the menu, with the connector address ready to copy and a button that
  opens the video tutorial at the minute that shows this step (1:04, the same in the four videos).
  The notice goes away by itself once the AI is connected. It depends on the community answering
  that in the polling reply (a new field), so the two changes ship together. Texts in English,
  Portuguese, Spanish and French. Asked by the founder on 2026-11-11, together with the reminder
  e-mail the community sends one hour and one day after the token is generated.
- Aviso "a sua IA ainda não está conectada". Colar o token só liga o QGIS à comunidade: falta
  conectar a IA ao conector da ClaudIA QGIS, e muita gente para antes desse passo. Quando a
  comunidade avisar que a conta ainda não tem IA conectada, o plugin mostra isso logo depois de
  conectar (barra de mensagens e uma linha no menu), com o endereço do conector pronto para copiar
  e um botão que abre o tutorial em vídeo no minuto desse passo (1:04, igual nos quatro vídeos). O
  aviso some sozinho quando a IA conecta. Depende de a comunidade informar isso na resposta da
  consulta periódica (campo novo): as duas mudanças saem juntas. Pedido do fundador em 11/11/2026,
  junto com o e-mail de lembrete que a comunidade manda 1 hora e 1 dia depois do token.

## 0.4.7

Released on 2026-11-17, ahead of the community plans by usage.

- Plans by usage. The community now tells the plugin two new account states, and the plugin shows
  them in the toolbar button, the status bar and the menu (ClaudIA button and Plugins → ClaudIA
  QGIS):
  - Free plan: the requests used today, for example "3 of 7 requests today". The menu line adds
    that they come back at midnight (Brasília time). When the day's requests run out, the message
    bar says so once, with the "See the plans" button. No notice before that: the number is always
    in sight.
  - Subscription: the monthly usage as a percentage, for example "monthly usage: 34%", with the
    renewal date in the menu. The message bar warns once when it passes 80% and once, with the
    "See the plans" button, when it runs out.
- The plugin never shows points or internal units: only requests per day and the percentage of
  the month, the same the member sees on the community site.
- Nothing changes with a community server that does not send the new states (free trial by
  requests, trial by days and "unlimited requests" keep working), and a state this version does
  not know is ignored.
- Command handlers updated to nkarasiak/qgis-mcp v0.15.3 (released 2026-11-11), two fixes to Processing
  models:
  - A step parameter written as `"FORMULA": "=$area"` built a model that failed at run time with
    `Parser error with formula expression ""`. On expression parameters (FORMULA, EXPRESSION) the
    `=expression` now goes through as text and QGIS evaluates it per feature; elsewhere it is still
    evaluated once per run.
  - `run_model` silently dropped the declared output names, so the result went to a temporary layer.
    It now maps each key to the model parameter it names (`FancyOut` → `fancyout` or `s1:FancyOut`)
    and refuses a key the model does not have, listing the valid ones.
  The headless smoke test builds a model with `=$area`, runs it into a declared output and removes it.
- Texts in English, Portuguese, Spanish and French. No tool added or removed.

## 0.4.6

- Video tutorial on how to connect, one per language (English, Portuguese, Spanish and French): in
  the plugin description, in the menu (ClaudIA button and Plugins → ClaudIA QGIS → "Video tutorial:
  how to connect", which opens the video in the interface language) and as a button in the welcome
  window.
- Safer "Update now" (security checkup #10, second half): the plugin only downloads a ZIP published
  in the releases of the ClaudIA QGIS repository on GitHub (`…/claudia-qgis/releases/download/<tag>/
  <file>.zip`) and follows redirects only to GitHub's download servers (github.com,
  release-assets.githubusercontent.com, objects.githubusercontent.com), over https, without a user
  or password in the address. The community server already applied the same rule to what it
  announces (lib/qgis/release-segura.ts).

## 0.4.5

- The free-requests line also shows in the Plugins menu (Plugins → ClaudIA QGIS), right below the
  connection status. In 0.4.4 it was only in the toolbar button menu. Includes 0.4.4 below, which
  never reached the QGIS plugin portal.

## 0.4.4

- New "no access" state. When the community refuses the connection because the account no longer
  has ClaudIA QGIS (free trial ended, plan without it, payment overdue), the toolbar button shows
  "ClaudIA · no access" in orange instead of "no connection", and the message bar explains it with
  a "See the plans" button. The plugin keeps checking once a minute and reconnects on its own, with
  the same token, as soon as the access comes back. A 403 page in HTML (a network filter on the
  way) is still treated as a connection problem. Texts in English, Portuguese, Spanish and French.
- Free trial by requests. When the community counts the free trial in requests (a request is
  what you ask your AI, however many tools it uses), the toolbar button and the status bar show
  "N of T free requests left", the menu shows the requests left and until when, the message bar
  warns when 2 or fewer are left and, at zero, explains it with a "See the plans" button. With a
  plan that includes ClaudIA QGIS the menu says "Unlimited requests"; the older trials by days show
  "Free trial until dd/mm". The plugin only shows what the community sends — nothing is counted on
  the user's machine. Texts in English, Portuguese, Spanish and French.
- nkarasiak/qgis-mcp v0.15.2 reviewed: its changes are in the socket transport (port selection,
  port clash message), which this plugin does not use. No handler changed; nothing to port.

## 0.4.3

interface in English, Portuguese, Spanish and French — the plugin follows the QGIS language (any other language shows English) and the language selector has the four. Command handlers updated to nkarasiak/qgis-mcp v0.15.1 — PostGIS tables added by name (add_layer_from_connection) now load with their geometry instead of as plain attribute tables. New plugin description: each language starts with its flag and name, with the three connection steps; the welcome window shows the connector address; the "Advanced" section (community address) only appears for test setups. No change to the tools.

## 0.4.2

interface in English or Brazilian Portuguese — the plugin follows the QGIS language (any language other than Portuguese shows English) and the connection window has a language selector (Automatic / Português / English). Plugin description and this changelog now in English. No change to the tools.

## 0.4.1

fix: "Update now" (and disconnect) could close QGIS without warning — on Windows, closing the socket from another thread does not wake the long-poll in progress; the thread outlived the wait timeout and was destroyed while still running. The socket is now shut down and the thread is never destroyed alive. No change to the tools.

## 0.4.0

handlers updated to nkarasiak/qgis-mcp v0.15.0 — background processing jobs (start_processing_job, get_processing_job, cancel_processing_job: no time cap and QGIS does not freeze), project checkpoints (create_checkpoint, list_checkpoints, restore_checkpoint) and export_session (a Python script that replays the session); partial results or failures no longer pass as success (Processing reason, dropped features in warnings); load_project no longer hangs on an unavailable layer; crs in identify_features, sample_raster_values and add_features; ellipsoid in Processing; inline QML in apply_style_qml. Includes 0.3.0 below, which never reached the portal.

## 0.3.0

handlers updated to nkarasiak/qgis-mcp v0.14.1 — attribute converter with dates, fixes in features, processing, connections and system, unresolved enums no longer crash the plugin (compat), and supportsQt6 declared: Qt6 builds of QGIS 3.x load the plugin again. execute_sql accepts limit.

## 0.2.3

plugin portal security scan (Bandit) cleared: the updater downloads through http.client over http/https only (no file: or custom schemes), following the GitHub redirect; empty try/except blocks became contextlib.suppress with the right exception.

## 0.2.2

metadata homepage points to the public repository (the connector page in the community requires login; the portal reviewer needs an open link). No code change.

## 0.2.1

the "Community address" field accepts any URL of the site (including the connector page) and keeps only the domain.

## 0.2.0

self-update — the community announces the latest version on every command poll; when there is a new one, an "Update now" bar appears (and the menu gains "Update the plugin…"): the plugin downloads the release ZIP, swaps the files and reloads itself, reconnecting afterwards. Connection state visible on the toolbar button ("ClaudIA · CONNECTED"), on the icon and in the status bar; warning when the community does not respond.

## 0.1.0

first version — connection to the agrônomo10X community by HTTPS long-poll (plugin token generated on the community page), 120 commands inherited from QGIS MCP 0.14.0 by Nicolas Karasiak, interface in Portuguese, no local server and no MCP client configuration.
