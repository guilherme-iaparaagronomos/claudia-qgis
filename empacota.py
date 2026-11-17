"""Gera o ZIP do plugin para o repositório oficial do QGIS (plugins.qgis.org).

Regras do repositório: o ZIP tem a pasta do pacote na raiz (claudia_qgis/…),
com metadata.txt, __init__.py e LICENSE dentro; nada de __pycache__.

    python empacota.py   →   dist/claudia_qgis-<versão>.zip
"""

import configparser
import os
import zipfile

RAIZ = os.path.dirname(os.path.abspath(__file__))
PACOTE = os.path.join(RAIZ, "claudia_qgis")


def versao():
    cfg = configparser.ConfigParser()
    cfg.read(os.path.join(PACOTE, "metadata.txt"), encoding="utf-8")
    return cfg.get("general", "version")


def conferir_metadata():
    """O portal do QGIS lê o metadata inteiro e recusa o envio se ele não passar (tests/metadata_check.py)."""
    import sys

    sys.path.insert(0, os.path.join(RAIZ, "tests"))
    import metadata_check

    metadata_check.conferir()


def main():
    conferir_metadata()
    os.makedirs(os.path.join(RAIZ, "dist"), exist_ok=True)
    destino = os.path.join(RAIZ, "dist", f"claudia_qgis-{versao()}.zip")
    with zipfile.ZipFile(destino, "w", zipfile.ZIP_DEFLATED) as z:
        for pasta, subpastas, arquivos in os.walk(PACOTE):
            subpastas[:] = [d for d in subpastas if d != "__pycache__"]
            for nome in arquivos:
                if nome.endswith((".pyc", ".pyo")):
                    continue
                caminho = os.path.join(pasta, nome)
                z.write(caminho, os.path.relpath(caminho, RAIZ))
    print(destino, f"({os.path.getsize(destino) / 1024:.0f} KB)")


if __name__ == "__main__":
    main()
