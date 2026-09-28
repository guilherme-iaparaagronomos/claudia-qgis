"""Checagem PURA do i18n (sem QGIS): paridade de chaves, placeholders iguais
em pt e en, nenhum texto vazio, e o `t()` preenchendo campos nos dois idiomas.

    python tests/i18n_check.py
"""

import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from claudia_qgis import i18n  # noqa: E402

en, pt = i18n._EN, i18n._PT
assert set(en) == set(pt), f"chaves diferentes: {set(en) ^ set(pt)}"
campos = re.compile(r"\{(\w+)\}")
for k in en:
    assert en[k].strip() and pt[k].strip(), f"texto vazio em {k}"
    assert set(campos.findall(en[k])) == set(campos.findall(pt[k])), f"placeholders diferentes em {k}"
    assert not (k.startswith(("menu.", "estado.")) and en[k] == pt[k] and "ClaudIA QGIS" not in en[k]), f"en igual ao pt em {k}"
assert i18n.t("menu.conectar", lang=i18n.EN) == "Connect to the community…"
assert i18n.t("menu.conectar", lang=i18n.PT) == "Conectar à comunidade…"
assert i18n.t("upd.disponivel", lang=i18n.EN, versao="0.4.2", atual="0.4.1") == "Plugin version 0.4.2 available (you are on 0.4.1)."
assert i18n.t("chave.inexistente", lang=i18n.EN) == "chave.inexistente"
assert i18n.t("estado.tooltip", lang=i18n.PT) == "ClaudIA QGIS — {texto}"  # sem campos: devolve cru
print(f"ok  i18n: {len(en)} chaves, paridade pt/en, placeholders iguais, t() nos dois idiomas")
