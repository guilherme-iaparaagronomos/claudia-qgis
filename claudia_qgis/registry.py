"""Registro dos handlers que a comunidade pode chamar.

Só stdlib, sem importar ``qgis`` — como :mod:`errors`. Precisa continuar
compatível com Python 3.9 (QGIS 3.28 traz essa versão).

``@command`` marca um método como chamável pelo canal e é coletado na
importação. O despacho resolve ``getattr(self, cmd_type)`` DEPOIS de conferir
a pertinência ao conjunto: sem isso, um comando poderia nomear qualquer
atributo do executor. Só os métodos decorados são alcançáveis.

Modificado por OagronomIA (2026-09-13) a partir de nkarasiak/qgis-mcp — GPLv2+.
"""

COMMANDS = set()


def command(fn):
    """Marca um método do executor como alcançável pelo canal da comunidade."""
    COMMANDS.add(fn.__name__)
    return fn


# Comandos recusados dentro de um ``batch``: exigem confirmação individual da
# IA do usuário e não podem passar escondidos numa lista. O mesmo conjunto é
# aplicado no servidor MCP da comunidade; aqui é a segunda trava.
BATCH_BLOCKED_COMMANDS = frozenset(
    {
        "execute_code",
        "remove_layer",
        "delete_features",
        "set_setting",
        "reload_plugin",
    }
)
