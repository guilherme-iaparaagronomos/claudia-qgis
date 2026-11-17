"""O metadata.txt lido como o PORTAL do QGIS lê (sem QGIS): todos os campos, com a interpolação do configparser.

Um "%" solto no texto (por exemplo "80%" no changelog) passa aqui dentro do plugin, que só lê o campo `version`,
mas o portal lê tudo e recusa o envio: "'%' must be followed by '%' or '('". Aconteceu na 0.4.7 (17/11/2026).

    python tests/metadata_check.py
"""

import configparser
import os
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ARQUIVO = os.path.join(RAIZ, "claudia_qgis", "metadata.txt")


def conferir(caminho=ARQUIVO):
    """Devolve a versão; lança ValueError com o motivo se o portal recusaria o arquivo."""
    with open(caminho, encoding="utf-8") as f:
        texto = f.read()
    if "%" in texto:
        linha = next(i for i, linha in enumerate(texto.splitlines(), 1) if "%" in linha)
        raise ValueError(f'metadata.txt, linha {linha}: tem "%" (o portal do QGIS recusa; escreva "percent")')
    cfg = configparser.ConfigParser()
    cfg.read_string(texto)
    try:
        campos = dict(cfg.items("general"))  # lê TODOS os campos, com interpolação, como o portal
    except configparser.Error as e:
        raise ValueError(f"metadata.txt não passa na leitura completa: {e}") from e
    for obrigatorio in ("name", "description", "about", "version", "qgisminimumversion", "author", "email", "repository"):
        if not campos.get(obrigatorio, "").strip():
            raise ValueError(f"metadata.txt sem o campo obrigatório: {obrigatorio}")
    if not campos.get("changelog", "").lstrip().startswith(campos["version"]):
        raise ValueError("o changelog do metadata não começa pela versão do campo version")
    return campos["version"]


if __name__ == "__main__":
    try:
        versao = conferir()
    except ValueError as e:
        print("FURO", e)
        sys.exit(1)
    print(f"ok  metadata.txt {versao}: leitura completa como o portal, sem '%', campos obrigatórios e changelog da versão")
