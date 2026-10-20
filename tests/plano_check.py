"""Cliente da comunidade × campo `plano` do poll, sem QGIS aberto (teste por pedidos, 20/10/2026).

Sobe um servidor HTTP local que imita o /api/qgis/poll e confere o que o worker emite em `plano_mudou`:
* o mesmo plano repetido em vários polls → UM sinal só;
* pedido contado (restantes muda)       → sinal de novo, com os números;
* conta assinou (tipo "ilimitado")      → sinal com tipo ilimitado;
* lixo do servidor (tipo desconhecido, número que é bool, data enorme) → nada de sinal / campo limpo.

    "C:/Program Files/QGIS 3.40.14/bin/python-qgis-ltr.bat" tests/plano_check.py
"""

import json
import os
import sys
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)

from qgis.PyQt.QtCore import Qt  # noqa: E402

from claudia_qgis import community  # noqa: E402

_DIRETO = getattr(getattr(Qt, "ConnectionType", Qt), "DirectConnection")

PLANO = {"valor": None}  # o teste troca o plano enquanto o worker roda


class Falso(BaseHTTPRequestHandler):
    def log_message(self, *_a):
        pass

    def do_POST(self):
        self.rfile.read(int(self.headers.get("Content-Length") or 0))
        time.sleep(0.05)
        corpo = {"comando": None}
        if PLANO["valor"] is not None:
            corpo["plano"] = PLANO["valor"]
        dados = json.dumps(corpo).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(dados)))
        self.end_headers()
        self.wfile.write(dados)


class Servidor(ThreadingHTTPServer):
    def handle_error(self, *_a):
        pass


srv = Servidor(("127.0.0.1", 0), Falso)
threading.Thread(target=srv.serve_forever, daemon=True).start()
base = f"http://127.0.0.1:{srv.server_address[1]}"

w = community.ComunidadeWorker(base, "cq_teste", {"plugin_versao": "0.4.4"}, idioma="pt")
planos = []
w.plano_mudou.connect(lambda p: planos.append(p), _DIRETO)
t = threading.Thread(target=w.run, daemon=True)
t.start()


def passo(plano, espera=0.5):
    PLANO["valor"] = plano
    time.sleep(espera)


passo(None)
assert planos == [], ("sem campo plano, nada de sinal", planos)

passo({"tipo": "pedidos", "total": 7, "usados": 2, "restantes": 5, "ate": "2026-11-19T17:00:00+00:00"})
assert len(planos) == 1, planos
assert planos[0] == {"tipo": "pedidos", "total": 7, "usados": 2, "restantes": 5, "ate": "2026-11-19T17:00:00+00:00"}, planos[0]
print("  ok  plano de pedidos → 1 sinal com os números, mesmo com vários polls")

passo({"tipo": "pedidos", "total": 7, "usados": 3, "restantes": 4, "ate": "2026-11-19T17:00:00+00:00"})
assert len(planos) == 2 and planos[-1]["restantes"] == 4, planos
print("  ok  pedido contado → novo sinal")

passo({"tipo": "misterioso", "total": 1})
passo({"tipo": "pedidos", "total": True, "restantes": "4", "ate": "x" * 500})
assert len(planos) == 3, planos
assert planos[-1] == {"tipo": "pedidos", "ate": "x" * 40}, ("bool e texto não entram como número; data cortada", planos[-1])
print("  ok  tipo desconhecido ignorado; número que é bool/texto descartado; data cortada em 40")

passo({"tipo": "ilimitado"})
assert planos[-1] == {"tipo": "ilimitado"}, planos
print("  ok  assinou → tipo ilimitado")

w.parar()
t.join(5)
assert not t.is_alive(), "o worker não parou"
srv.shutdown()
print("ok  cliente da comunidade: plano do teste por pedidos")
