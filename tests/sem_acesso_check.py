"""Cliente da comunidade × respostas do servidor, sem QGIS aberto (P18, 19/10/2026).

Sobe um servidor HTTP local que imita o /api/qgis/poll e confere o que o worker emite:
* 403 em texto puro (sem acesso)  → "sem_acesso" UMA vez, e segue conferindo;
* acesso volta (200)              → "conectado" sozinho, sem novo token;
* 403 em HTML (WAF/proxy)         → "sem_rede", como antes;
* 401                             → "token_invalido" e o worker para.

    "C:/Program Files/QGIS 3.40.14/bin/python-qgis-ltr.bat" tests/sem_acesso_check.py
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

# sem laço de eventos do Qt neste teste: o sinal da thread de rede chega por ligação direta
_DIRETO = getattr(getattr(Qt, "ConnectionType", Qt), "DirectConnection")

RESPOSTA = {"modo": "sem_acesso"}  # o teste troca o modo enquanto o worker roda
PEDIDOS = []


class Falso(BaseHTTPRequestHandler):
    def log_message(self, *_a):  # silêncio no console
        pass

    def do_POST(self):
        self.rfile.read(int(self.headers.get("Content-Length") or 0))
        PEDIDOS.append(RESPOSTA["modo"])
        modo = RESPOSTA["modo"]
        if modo == "sem_acesso":
            corpo, status, tipo = "ClaudIA QGIS sem acesso (teste acabou ou plano sem a QGIS).".encode(), 403, "text/plain; charset=utf-8"
        elif modo == "waf":
            corpo, status, tipo = b"<!DOCTYPE html><html><body>Security Checkpoint</body></html>", 403, "text/html"
        elif modo == "token":
            corpo, status, tipo = b'{"error":"token inv\\u00e1lido"}', 401, "application/json"
        else:
            time.sleep(0.05)
            corpo, status, tipo = json.dumps({"comando": None}).encode(), 200, "application/json"
        self.send_response(status)
        self.send_header("Content-Type", tipo)
        self.send_header("Content-Length", str(len(corpo)))
        self.end_headers()
        self.wfile.write(corpo)


class Servidor(ThreadingHTTPServer):
    def handle_error(self, *_a):  # o worker fecha a conexão ao parar; não é falha do teste
        pass


srv = Servidor(("127.0.0.1", 0), Falso)
threading.Thread(target=srv.serve_forever, daemon=True).start()
base = f"http://127.0.0.1:{srv.server_address[1]}"

assert community.ESPERA_SEM_ACESSO_S == 60, "a conferência sem acesso é de minuto em minuto"
community.ESPERA_SEM_ACESSO_S = 0.2  # o teste não espera um minuto por rodada
community.BACKOFF_INICIAL_S = 0.1
community.BACKOFF_MAX_S = 0.2


def rodar(modo_inicial, passos):
    """Roda o worker numa thread; `passos` = [(segundos, novo_modo)]. Devolve os estados emitidos."""
    RESPOSTA["modo"] = modo_inicial
    PEDIDOS.clear()
    w = community.ComunidadeWorker(base, "cq_teste", {"plugin_versao": "0.4.4"}, idioma="pt")
    estados = []
    w.estado_mudou.connect(lambda e, d: estados.append(e), _DIRETO)
    t = threading.Thread(target=w.run, daemon=True)
    t.start()
    for espera, modo in passos:
        time.sleep(espera)
        RESPOSTA["modo"] = modo
    time.sleep(0.6)
    w.parar()
    t.join(5)
    assert not t.is_alive(), "o worker não parou"
    return estados


e = rodar("sem_acesso", [(1.2, "ok")])
assert e.count("sem_acesso") == 1, e
assert PEDIDOS.count("sem_acesso") >= 3, ("seguiu conferindo", PEDIDOS)
assert "conectado" in e and e.index("conectado") > e.index("sem_acesso"), e
assert "sem_rede" not in e and "token_invalido" not in e, e
print(f"  ok  403 de texto → sem_acesso 1x em {PEDIDOS.count('sem_acesso')} conferências; acesso volta → conectado")

e = rodar("waf", [])
assert "sem_rede" in e and "sem_acesso" not in e, e
print("  ok  403 em HTML (proteção de rede) → sem_rede, como antes")

e = rodar("token", [])
assert e[-2:] == ["token_invalido", "parado"], e
print("  ok  401 → token_invalido e o worker para")

srv.shutdown()
print("ok  cliente da comunidade: sem acesso, volta sozinho, WAF e token recusado")
