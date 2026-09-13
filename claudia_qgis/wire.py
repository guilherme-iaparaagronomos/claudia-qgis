"""Utilitários sem ``qgis`` compartilhados pelos handlers.

No projeto original este módulo tinha o enquadramento do socket local; na
ClaudIA QGIS o transporte é o :mod:`community` (HTTPS), e só sobrou o que os
handlers importam.

Modificado por OagronomIA (2026-09-13) a partir de nkarasiak/qgis-mcp — GPLv2+.
"""

from __future__ import annotations


def zip_strict(*iterables):
    """``zip(*iterables, strict=True)`` que também funciona no Python 3.9.

    O argumento ``strict`` chegou no 3.10, e o QGIS 3.28 (mínimo do plugin)
    ainda traz o 3.9. As entradas são materializadas para comparar o tamanho
    antes; todo call site passa sequências curtas e já realizadas.
    """
    columns = [list(it) for it in iterables]
    if len({len(c) for c in columns}) > 1:
        raise ValueError(
            "zip_strict() argument lengths differ: " + ", ".join(str(len(c)) for c in columns)
        )
    return zip(*columns)
