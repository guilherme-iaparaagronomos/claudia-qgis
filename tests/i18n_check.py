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
# (0.4.7) planos por uso: o que o botão e o menu dizem no plano gratuito e na assinatura
assert i18n.t("plano.dia", lang=i18n.PT, u=3, t=7) == "3 de 7 pedidos hoje"
assert i18n.t("plano.dia", lang=i18n.EN, u=3, t=7) == "3 of 7 requests today"
assert i18n.t("plano.mes", lang=i18n.PT, pct=34) == "uso do mês: 34%"
assert i18n.t("plano.menu_mes", lang=i18n.PT, pct=34, data="01/12") == "Uso do mês: 34% · renova em 01/12"
assert i18n.t("plano.menu_mes", lang=i18n.FR, pct=34, data="01/12") == "Utilisation du mois\xa0: 34\xa0% · renouvellement le 01/12"
for _lang in (i18n.PT, i18n.EN, i18n.ES, i18n.FR):
    for _chave in ("plano.dia", "plano.mes", "plano.mes_curto", "plano.menu_dia", "plano.menu_mes", "msg.dia_acabou", "msg.mes_aviso", "msg.mes_acabou"):
        _texto = i18n.t(_chave, lang=_lang, u=3, t=7, pct=34, data="01/12")
        assert "{" not in _texto and not re.search(r"ponto|point|token|cr[eé]dit", _texto, re.I), (_lang, _chave, _texto)
assert i18n.t("estado.tooltip", lang=i18n.PT) == "ClaudIA QGIS — {texto}"  # sem campos: devolve cru
print(f"ok  i18n: {len(en)} chaves, paridade en/pt/es/fr, placeholders iguais, t() nas quatro línguas")
