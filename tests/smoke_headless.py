"""Teste de fumaça SEM interface, com o Python do QGIS (PyQGIS de verdade).

    "C:/Program Files/QGIS 3.40.14/bin/python-qgis-ltr.bat" tests/smoke_headless.py

1) Executor: ping, create_memory_layer, add_features, get_layers,
   get_layer_features, get_field_statistics, execute_sql, batch (com um
   comando bloqueado) — sem iface (handlers de canvas ficam de fora).
2) Se CLAUDIA_QGIS_TOKEN e CLAUDIA_QGIS_URL estiverem no ambiente: conecta à
   comunidade como o plugin faria (worker em QThread + executor na thread
   principal) e fica esperando comandos por CLAUDIA_QGIS_SEGUNDOS (padrão 60),
   para o E2E da comunidade disparar tools/call contra este QGIS.
"""

import json
import os
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)

from qgis.core import QgsApplication  # noqa: E402

app = QgsApplication([], False)
app.initQgis()

# Fora do QGIS de verdade, o módulo `processing` (plugin central) não está no
# sys.path; nem o provedor nativo está registrado. O plugin, dentro do QGIS,
# encontra os dois prontos.
try:
    plugins_qgis = os.path.join(QgsApplication.prefixPath(), "python", "plugins")
    if os.path.isdir(plugins_qgis) and plugins_qgis not in sys.path:
        sys.path.append(plugins_qgis)
    from qgis.analysis import QgsNativeAlgorithms

    QgsApplication.processingRegistry().addProvider(QgsNativeAlgorithms())
    from processing.core.Processing import Processing

    Processing.initialize()
except Exception as e:  # pragma: no cover
    print("(processing indisponível no modo headless:", e, ")")

from claudia_qgis.server import ClaudiaExecutor  # noqa: E402

falhas = 0


def ok(msg):
    print("  ok ", msg)


def furo(msg, detalhe=""):
    global falhas
    falhas += 1
    print("  FURO", msg, detalhe)


ex = ClaudiaExecutor(iface=None)


def run(tipo, **params):
    return ex.executar({"type": tipo, "params": params})


r = run("ping")
ok("ping") if r.get("status") == "success" and r["result"].get("pong") else furo("ping", r)

r = run("create_memory_layer", name="talhoes_smoke", geometry_type="Polygon", crs="EPSG:4326", fields=[{"name": "nome", "type": "string"}, {"name": "area_ha", "type": "double"}])
layer_id = (r.get("result") or {}).get("layer_id") or (r.get("result") or {}).get("id")
ok(f"create_memory_layer → {layer_id}") if r.get("status") == "success" and layer_id else furo("create_memory_layer", r)

r = run(
    "add_features",
    layer_id=layer_id,
    features=[
        {"attributes": {"nome": "T1", "area_ha": 12.5}, "geometry_wkt": "POLYGON((-47.6 -22.7,-47.5 -22.7,-47.5 -22.6,-47.6 -22.6,-47.6 -22.7))"},
        {"attributes": {"nome": "T2", "area_ha": 30.0}, "geometry_wkt": "POLYGON((-47.4 -22.7,-47.3 -22.7,-47.3 -22.6,-47.4 -22.6,-47.4 -22.7))"},
    ],
)
ok("add_features") if r.get("status") == "success" else furo("add_features", r)

r = run("get_layers", limit=10)
nomes = [c.get("name") for c in (r.get("result") or {}).get("layers", [])]
ok(f"get_layers → {nomes}") if "talhoes_smoke" in nomes else furo("get_layers", r)

r = run("get_layer_features", layer_id=layer_id, limit=5)
feats = (r.get("result") or {}).get("features", [])
ok(f"get_layer_features → {len(feats)} feições") if len(feats) == 2 else furo("get_layer_features", r)

r = run("get_field_statistics", layer_id=layer_id, field_name="area_ha")
st = r.get("result") or {}
ok(f"get_field_statistics → soma {st.get('sum')}") if r.get("status") == "success" and abs(float(st.get("sum", 0)) - 42.5) < 1e-6 else furo("get_field_statistics", r)

r = run("execute_sql", query='SELECT nome, area_ha FROM talhoes_smoke WHERE area_ha > 20')
linhas = (r.get("result") or {}).get("rows") or (r.get("result") or {}).get("features") or []
ok(f"execute_sql → {len(linhas)} linha(s)") if r.get("status") == "success" and len(linhas) == 1 else furo("execute_sql", r)

r = run("batch", commands=[{"type": "ping", "params": {}}, {"type": "execute_code", "params": {"code": "1"}}])
res = r.get("result") or []
ok("batch: ping passa, execute_code recusado no lote") if r.get("status") == "success" and len(res) == 2 and res[0]["status"] == "success" and res[1]["status"] == "error" else furo("batch", r)

r = run("get_layer_info", layer_id="nao-existe")
ok("erro legível para camada inexistente") if r.get("status") == "error" and "nao-existe" in r.get("message", "") else furo("get_layer_info erro", r)

r = run("naoexiste")
ok("comando desconhecido recusado") if r.get("status") == "error" else furo("comando desconhecido", r)

r = run("list_processing_algorithms", search="buffer")
algs = (r.get("result") or {}).get("algorithms", [])
ok(f"list_processing_algorithms(buffer) → {len(algs)}") if any("buffer" in (a.get("id") or "") for a in algs) else furo("list_processing_algorithms", r)

r = run("execute_processing", algorithm="native:buffer", parameters={"INPUT": layer_id, "DISTANCE": 0.01, "OUTPUT": "TEMPORARY_OUTPUT"}, load_results=True)
ok("execute_processing native:buffer com load_results") if r.get("status") == "success" and (r.get("result") or {}).get("loaded_layers") else furo("execute_processing", r)

# ------------------------------------------------------------ comunidade
token = os.environ.get("CLAUDIA_QGIS_TOKEN")
base = os.environ.get("CLAUDIA_QGIS_URL")
if token and base:
    from qgis.core import Qgis
    from qgis.PyQt.QtCore import QCoreApplication, QThread, QTimer

    from claudia_qgis.community import ComunidadeWorker
    from claudia_qgis.constants import plugin_version

    segundos = int(os.environ.get("CLAUDIA_QGIS_SEGUNDOS", "60"))
    print(f"\nconectando a {base} por {segundos} s…")
    worker = ComunidadeWorker(base, token, {"qgis_versao": Qgis.version(), "plugin_versao": plugin_version(), "projeto": "smoke-headless"})
    thread = QThread()
    worker.moveToThread(thread)
    thread.started.connect(worker.run)
    executados = []

    def executar(comando):
        env = ex.executar({"type": comando.get("type"), "params": comando.get("params") or {}})
        executados.append(comando.get("type"))
        print("  comando", comando.get("type"), "→", env.get("status"))
        worker.entregar_resultado(comando.get("id"), env)

    def estado(e, d):
        # o plugin faz o mesmo em _estado_mudou: é o que `diagnose` reporta
        ex.comunidade.update({"estado": e, "detalhe": d, "conectado": e == "conectado", "base_url": base})
        print("  estado:", e, "-", d, flush=True)

    worker.comando_recebido.connect(executar)
    worker.estado_mudou.connect(estado)
    thread.start()

    def encerrar():
        worker.parar()
        thread.quit()
        thread.wait(5000)
        QCoreApplication.quit()

    QTimer.singleShot(segundos * 1000, encerrar)
    app.exec()
    print(json.dumps({"executados": executados}))

app.exitQgis()
print("\nTUDO OK" if not falhas else f"\n{falhas} FURO(S)")
sys.exit(1 if falhas else 0)
