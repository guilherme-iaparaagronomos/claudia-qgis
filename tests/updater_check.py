"""Trava do "Atualizar agora" (0.4.6, checkup de segurança #10), sem rede.

* o ZIP só vale se for release do nosso repositório (``url_de_release``);
* ``baixar_zip`` recusa o resto ANTES de abrir conexão;
* os redirecionamentos só vão aos servidores de download do GitHub, por https,
  sem usuário/senha e na porta padrão — a conexão falsa abaixo imita o GitHub.

    "C:/Program Files/QGIS 3.40.14/bin/python-qgis-ltr.bat" tests/updater_check.py
"""

import os
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)

from claudia_qgis import updater  # noqa: E402
from claudia_qgis.constants import PREFIXO_RELEASES  # noqa: E402

BOM = PREFIXO_RELEASES + "v0.4.6/claudia_qgis-0.4.6.zip"
falhas = 0


def ok(cond, nome):
    global falhas
    print(("  ok  " if cond else "  FALHOU  ") + nome)
    if not cond:
        falhas += 1


# 1) a regra do endereço (a mesma do servidor, lib/qgis/release-segura.ts)
ok(updater.url_de_release(BOM), "release do nosso repositório vale")
for ruim, nome in (
    ("https://github.com/outra-conta/claudia-qgis/releases/download/v1/claudia_qgis-1.0.zip", "outro dono"),
    ("https://github.com/guilherme-iaparaagronomos/outro-repo/releases/download/v1/x.zip", "outro repositório"),
    (PREFIXO_RELEASES + "../../../outra-conta/repo/releases/download/v1/x.zip", "subida de pasta (..)"),
    (PREFIXO_RELEASES + "./claudia_qgis.zip", "pasta '.'"),
    (PREFIXO_RELEASES + "v1/claudia_qgis.zip?x=1", "com ?"),
    (PREFIXO_RELEASES + "v1/claudia_qgis.zip#a", "com #"),
    (PREFIXO_RELEASES + "v1/claudia_qgis.exe", "não termina em .zip"),
    (PREFIXO_RELEASES + "v1/sub/claudia_qgis.zip", "pasta a mais"),
    (PREFIXO_RELEASES + "v1/cláudia.zip", "letra fora do ASCII"),
    ("https://example.invalid/claudia_qgis-9.9.9.zip", "outro servidor"),
    ("https://github.com.evil.example/guilherme-iaparaagronomos/claudia-qgis/releases/download/v1/x.zip", "github.com como prefixo de outro domínio"),
    (None, "vazio"),
):
    ok(not updater.url_de_release(ruim), f"recusa: {nome}")

# 2) baixar_zip recusa sem nem abrir conexão
ABERTAS = []


class _Resposta:
    def __init__(self, status, location=None, corpo=b""):
        self.status = status
        self._location = location
        self._corpo = corpo

    def getheader(self, nome):
        return self._location if nome.lower() == "location" else None

    def read(self, n=-1):
        corpo, self._corpo = self._corpo, b""
        return corpo


class _ConexaoFalsa:
    """Imita o GitHub: a página da release redireciona para ROTA[host]."""

    ROTA = {}

    def __init__(self, host, port=None, timeout=None, context=None):
        self.host = host
        ABERTAS.append(host)

    def request(self, metodo, caminho, headers=None):
        self.caminho = caminho

    def getresponse(self):
        destino = self.ROTA.get(self.host)
        if destino:
            return _Resposta(302, destino)
        return _Resposta(200, corpo=b"PK\x05\x06" + b"\0" * 18)  # ZIP vazio

    def close(self):
        pass


updater.http.client.HTTPSConnection = _ConexaoFalsa
updater.http.client.HTTPConnection = _ConexaoFalsa


def tenta(url):
    try:
        caminho = updater.baixar_zip(url)
    except ValueError as e:
        return str(e)
    os.remove(caminho)
    return None


ABERTAS.clear()
erro = tenta("https://example.invalid/claudia_qgis-9.9.9.zip")
ok(erro is not None and not ABERTAS, "endereço de fora: recusado sem abrir conexão")

# 3) redirecionamentos
_ConexaoFalsa.ROTA = {"github.com": "https://release-assets.githubusercontent.com/github-production-release-asset/1/abc?sig=x"}
ABERTAS.clear()
ok(tenta(BOM) is None and ABERTAS == ["github.com", "release-assets.githubusercontent.com"], "GitHub → CDN do GitHub: baixa")

_ConexaoFalsa.ROTA = {"github.com": "https://objects.githubusercontent.com/x/y"}
ok(tenta(BOM) is None, "GitHub → CDN antigo (objects.githubusercontent.com): baixa")

for destino, nome in (
    ("https://evil.example/claudia_qgis.zip", "outro domínio"),
    ("http://release-assets.githubusercontent.com/x", "http sem s"),
    ("https://user:senha@release-assets.githubusercontent.com/x", "usuário e senha na URL"),
    ("https://release-assets.githubusercontent.com:8443/x", "outra porta"),
    ("https://release-assets.githubusercontent.com.evil.example/x", "CDN como prefixo de outro domínio"),
    ("file:///C:/Windows/x.zip", "file:"),
):
    _ConexaoFalsa.ROTA = {"github.com": destino}
    ABERTAS.clear()
    erro = tenta(BOM)
    ok(erro is not None and ABERTAS == ["github.com"], f"redirecionamento recusado: {nome}")

print("\nTUDO OK" if not falhas else f"\n{falhas} falha(s)")
sys.exit(1 if falhas else 0)
