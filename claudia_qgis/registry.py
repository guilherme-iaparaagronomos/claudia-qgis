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


# (0.15.0) Comandos que não entram no diário de `export_session`: só leitura
# (não mudam nada) e os de escrituração (batch, checkpoints, jobs — o job
# registra o próprio resultado ao terminar). Mesma lista do upstream.
UNRECORDED_COMMANDS = frozenset(
    {
        # read-only
        "diagnose",
        "evaluate_expression",
        "find_layer",
        "get_3d_screenshot",
        "get_active_layer",
        "get_algorithm_help",
        "get_bookmarks",
        "get_canvas_extent",
        "get_canvas_scale",
        "get_canvas_screenshot",
        "get_edit_status",
        "get_field_statistics",
        "get_layer_crs",
        "get_layer_extent",
        "get_layer_features",
        "get_layer_labeling",
        "get_layer_tree",
        "get_layers",
        "get_layout_info",
        "get_map_themes",
        "get_message_log",
        "get_plugin_info",
        "get_processing_job",
        "get_processing_providers",
        "get_project_info",
        "get_project_variables",
        "get_qgis_info",
        "get_raster_info",
        "get_selection",
        "get_setting",
        "get_unique_values",
        "identify_features",
        "list_checkpoints",
        "list_connection_tables",
        "list_connections",
        "list_layouts",
        "list_plugins",
        "list_processing_algorithms",
        "list_processing_models",
        "ping",
        "sample_raster_values",
        "transform_coordinates",
        "validate_expression",
        # bookkeeping
        "batch",
        "cancel_processing_job",
        "create_checkpoint",
        "export_session",
        "restore_checkpoint",
        "start_processing_job",
        # ClaudIA QGIS: handlers que o plugin expõe fora do servidor original
        "get_layer_info",
        "get_layer_schema",
        "render_map_base64",
    }
)
