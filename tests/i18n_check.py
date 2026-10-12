"""Checagem PURA do i18n (sem QGIS): paridade de chaves, placeholders iguais
em pt e en, nenhum texto vazio, e o `t()` preenchendo campos nos dois idiomas.

    python tests/i18n_check.py
"""

import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from claudia_qgis import i18n  # noqa: E402

en, pt, es, fr = i18n._EN, i18n._PT, i18n._ES, i18n._FR
campos = re.compile(r"\{(\w+)\}")
for nome, d in (("pt", pt), ("es", es), ("fr", fr)):
    assert set(en) == set(d), f"chaves diferentes en x {nome}: {set(en) ^ set(d)}"
    for k in en:
        assert en[k].strip() and d[k].strip(), f"texto vazio em {nome}:{k}"
        assert set(campos.findall(en[k])) == set(campos.findall(d[k])), f"placeholders diferentes em {nome}:{k}"
        assert not (k.startswith(("menu.", "estado.")) and en[k] == d[k] and "ClaudIA QGIS" not in en[k] and "CONECTADO" not in d[k]), f"en igual ao {nome} em {k}"
# francês: espaço insécable antes de : ; ? ! (nunca espaço comum)
for k, v in fr.items():
    sem_tags = re.sub(r"<[^>]+>|https?://\S+", "", v)
    assert not re.search(r" [:;?!»]", sem_tags), f"espaço comum antes de pontuação no francês: {k}"
assert i18n.t("menu.conectar", lang=i18n.ES) == "Conectar con la comunidad…"
assert i18n.t("menu.conectar", lang=i18n.FR) == "Se connecter à la communauté…"
assert i18n.t("menu.conectar", lang=i18n.EN) == "Connect to the community…"
assert i18n.t("menu.conectar", lang=i18n.PT) == "Conectar à comunidade…"
assert i18n.t("upd.disponivel", lang=i18n.EN, versao="0.4.2", atual="0.4.1") == "Plugin version 0.4.2 available (you are on 0.4.1)."
assert i18n.t("chave.inexistente", lang=i18n.EN) == "chave.inexistente"
assert i18n.t("estado.tooltip", lang=i18n.PT) == "ClaudIA QGIS — {texto}"  # sem campos: devolve cru
print(f"ok  i18n: {len(en)} chaves, paridade en/pt/es/fr, placeholders iguais, t() nas quatro línguas")
