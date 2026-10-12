"""Ponto de entrada do plugin ClaudIA QGIS: botão na barra, menu, janela de
conexão e a ponte entre a comunidade (thread de rede) e o executor (thread
principal do QGIS).

Modificado por OagronomIA (2026-09-13) a partir de nkarasiak/qgis-mcp — GPLv2+.
"""

import contextlib
import functools
import os

from qgis.core import Qgis, QgsMessageLog, QgsProject, QgsSettings
from qgis.PyQt.QtCore import QSize, Qt, QThread, QTimer, QUrl
from qgis.PyQt.QtGui import QColor, QDesktopServices, QIcon, QPainter, QPen
from qgis.PyQt.QtWidgets import (
    QAction,
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMenu,
    QPushButton,
    QToolButton,
    QVBoxLayout,
)

from . import i18n, updater
from .community import ComunidadeWorker
from .i18n import t
from .compat import (
    MSG_CRITICAL,
    MSG_INFO,
    MSG_WARNING,
    PAINTER_ANTIALIAS,
    TOOLBUTTON_MENU_POPUP,
)
from .constants import (
    DEFAULT_BASE_URL,
    LOG_TAG,
    PAGINA_CONECTOR,
    REPO_URL,
    RELEASES_URL,
    SETTINGS_PREFIX,
    UPSTREAM_URL,
    plugin_version,
    versao_tupla,
)
from .server import ClaudiaExecutor

MENU = "ClaudIA QGIS"

# Qt5 e Qt6 nomeiam os enums de jeitos diferentes; o compat.py cobre os que o
# projeto original usa, estes são só do plugin.
_ECHO_PASSWORD = getattr(getattr(QLineEdit, "EchoMode", QLineEdit), "Password")
_ECHO_NORMAL = getattr(getattr(QLineEdit, "EchoMode", QLineEdit), "Normal")
_ROLE_ACCEPT = getattr(getattr(QDialogButtonBox, "ButtonRole", QDialogButtonBox), "AcceptRole")
_ROLE_REJECT = getattr(getattr(QDialogButtonBox, "ButtonRole", QDialogButtonBox), "RejectRole")
_QUEUED = getattr(getattr(Qt, "ConnectionType", Qt), "QueuedConnection")
_ALIGN_RIGHT = getattr(getattr(Qt, "AlignmentFlag", Qt), "AlignRight")
_TEXT_BESIDE_ICON = getattr(getattr(Qt, "ToolButtonStyle", Qt), "ToolButtonTextBesideIcon")

# Estado da conexão → (cor, negrito); rótulo e texto vêm do i18n (estado.<nome>.rotulo/texto)
ESTADOS = {
    "parado": ("#9E9E9E", False),
    "conectando": ("#F9A825", False),
    "conectado": ("#52C937", True),
    "sem_rede": ("#F9A825", False),
    "token_invalido": ("#D32F2F", True),
}
_COR_TEXTO = {"#52C937": "#1B7F2A", "#F9A825": "#8A5A00", "#D32F2F": "#B71C1C", "#9E9E9E": "#616161"}


def _estado_textos(estado):
    """(cor, rótulo do botão, texto da barra de status, negrito) no idioma em vigor."""
    nome = estado if estado in ESTADOS else "parado"
    cor, negrito = ESTADOS[nome]
    return cor, t(f"estado.{nome}.rotulo"), t(f"estado.{nome}.texto"), negrito


def _cfg(chave, padrao=None, tipo=None):
    s = QgsSettings()
    if tipo is not None:
        return s.value(f"{SETTINGS_PREFIX}/{chave}", padrao, type=tipo)
    return s.value(f"{SETTINGS_PREFIX}/{chave}", padrao)


def _set_cfg(chave, valor):
    QgsSettings().setValue(f"{SETTINGS_PREFIX}/{chave}", valor)


def _normalizar_base(texto):
    """Qualquer URL do site vira só esquema + host[:porta].

    O fundador colou a URL da PÁGINA do conector no campo (13/09) e o plugin
    passou a chamar …/solucoes/mcp/claudia-qgis/api/qgis/poll. Caminho,
    query e barra final saem; sem esquema assume https.
    """
    from urllib.parse import urlsplit

    t = (texto or "").strip()
    if not t:
        return DEFAULT_BASE_URL
    if not t.startswith(("https://", "http://")):
        t = "https://" + t
    p = urlsplit(t)
    return f"{p.scheme}://{p.netloc}" if p.netloc else DEFAULT_BASE_URL


def _base_url():
    return _normalizar_base(_cfg("base_url", DEFAULT_BASE_URL) or DEFAULT_BASE_URL)


def _pagina_conector():
    return _base_url() + PAGINA_CONECTOR


class ConectarDialog(QDialog):
    """Token da comunidade + opções. Salva em QgsSettings e devolve accept()."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(t("conectar.titulo"))
        self.setMinimumWidth(540)
        layout = QVBoxLayout(self)

        intro = QLabel(t("conectar.intro"))
        intro.setWordWrap(True)
        layout.addWidget(intro)

        abrir = QPushButton(t("conectar.abrir_pagina"))
        abrir.clicked.connect(lambda: QDesktopServices.openUrl(QUrl(_pagina_conector())))
        layout.addWidget(abrir)

        form = QFormLayout()
        self.token = QLineEdit()
        self.token.setPlaceholderText("cq_…")
        self.token.setEchoMode(_ECHO_PASSWORD)
        self.token.setText(_cfg("token", "") or "")
        self.token.textEdited.connect(lambda _t: self.token.setStyleSheet(""))
        form.addRow(t("conectar.token"), self.token)
        mostrar = QCheckBox(t("conectar.exibir_codigo"))
        mostrar.toggled.connect(lambda on: self.token.setEchoMode(_ECHO_NORMAL if on else _ECHO_PASSWORD))
        form.addRow("", mostrar)
        self.autostart = QCheckBox(t("conectar.autostart"))
        self.autostart.setChecked(bool(_cfg("autostart", False, bool)))
        form.addRow("", self.autostart)
        # (0.4.2) idioma da interface: automático (segue o QGIS) ou um dos quatro (12/10: es e fr)
        self.idioma = QComboBox()
        for valor, chave in (
            (i18n.AUTO, "conectar.idioma.auto"),
            (i18n.PT, "conectar.idioma.pt"),
            (i18n.EN, "conectar.idioma.en"),
            (i18n.ES, "conectar.idioma.es"),
            (i18n.FR, "conectar.idioma.fr"),
        ):
            self.idioma.addItem(t(chave), valor)
        self.idioma.setCurrentIndex(max(0, self.idioma.findData(i18n.idioma_configurado())))
        form.addRow(t("conectar.idioma"), self.idioma)
        layout.addLayout(form)

        avancado = QGroupBox(t("conectar.avancado"))
        avancado.setCheckable(True)
        avancado.setChecked(_base_url() != DEFAULT_BASE_URL)
        av_layout = QFormLayout(avancado)
        self.base_url = QLineEdit(_base_url())
        av_layout.addRow(t("conectar.endereco"), self.base_url)
        dica = QLabel(t("conectar.endereco_dica"))
        dica.setStyleSheet("color: gray")
        av_layout.addRow("", dica)
        # (12/10) o endereço da comunidade só serve para a equipe testar: some da janela, a menos que o
        # endereço salvo não seja o oficial (quem salvou um errado consegue corrigir) ou que a variável
        # CLAUDIA_QGIS_TESTES esteja ligada
        avancado.setVisible(_base_url() != DEFAULT_BASE_URL or bool(os.environ.get("CLAUDIA_QGIS_TESTES")))
        layout.addWidget(avancado)
        self._avancado = avancado

        privacidade = QLabel(t("conectar.privacidade"))
        privacidade.setWordWrap(True)
        layout.addWidget(privacidade)

        botoes = QDialogButtonBox()
        salvar = botoes.addButton(t("conectar.salvar"), _ROLE_ACCEPT)
        botoes.addButton(t("conectar.cancelar"), _ROLE_REJECT)
        salvar.setDefault(True)
        botoes.accepted.connect(self._salvar)
        botoes.rejected.connect(self.reject)
        layout.addWidget(botoes)

    def _salvar(self):
        token = self.token.text().strip()
        if not token.startswith("cq_") or len(token) < 20:
            self.token.setFocus()
            self.token.setStyleSheet("border: 1px solid #D32F2F")
            return
        base = DEFAULT_BASE_URL
        if self._avancado.isChecked():
            base = _normalizar_base(self.base_url.text())
            self.base_url.setText(base)
        _set_cfg("token", token)
        _set_cfg("base_url", base)
        _set_cfg("autostart", self.autostart.isChecked())
        i18n.definir_idioma(str(self.idioma.currentData() or i18n.AUTO))
        self.accept()


class ClaudiaQgisPlugin:
    """Plugin ClaudIA QGIS — comunidade agrônomo10X (OagronomIA)."""

    def __init__(self, iface):
        self.iface = iface
        self.executor = None
        self.worker = None
        self.thread = None
        self.action = None
        self.conectar_action = None
        self.pagina_action = None
        self.sobre_action = None
        self.tool_button = None
        self.status_label = None
        self._toolbar_action = None
        self._estado = "parado"
        self._detalhe = ""
        self._timer_info = None
        self._avisou_conexao = False
        self._avisou_rede = False
        self.atualizar_action = None
        self._versao_oferecida = None
        self._atualizando = False
        # (0.4.1) threads que não pararam a tempo ficam aqui até terminar (nunca destruir QThread rodando)
        self._threads_zumbis = []

    # --------------------------------------------------------------- ícones
    def _icone_base(self):
        return QIcon(os.path.join(os.path.dirname(__file__), "icons", "icon.png"))

    def _icone_estado(self, cor):
        """Ícone da ClaudIA com ANEL na cor do estado e um ponto no canto."""
        pixmap = self._icone_base().pixmap(QSize(64, 64))
        tamanho = pixmap.width()
        painter = QPainter(pixmap)
        painter.setRenderHint(PAINTER_ANTIALIAS)
        anel = QPen(QColor(cor))
        anel.setWidth(max(4, tamanho // 12))
        painter.setPen(anel)
        painter.setBrush(QColor(0, 0, 0, 0))
        m = anel.width() // 2 + 1
        painter.drawEllipse(m, m, tamanho - 2 * m, tamanho - 2 * m)
        d = int(tamanho * 0.34)
        painter.setBrush(QColor(cor))
        borda = QPen(QColor("white"))
        borda.setWidth(max(2, tamanho // 24))
        painter.setPen(borda)
        painter.drawEllipse(tamanho - d - 1, tamanho - d - 1, d, d)
        painter.end()
        return QIcon(pixmap)

    def _mostrar_estado(self, estado, detalhe=""):
        """Um lugar só para refletir o estado: ícone, rótulo, cor, tooltip e barra de status."""
        cor, rotulo, texto, negrito = _estado_textos(estado)
        if self.action:
            self.action.setIcon(self._icone_base() if estado == "parado" else self._icone_estado(cor))
            self.action.setText(rotulo)
            self.action.setToolTip(t("estado.tooltip", texto=texto) + (f" · {detalhe}" if detalhe else ""))
        if self.tool_button:
            peso = "bold" if negrito else "normal"
            self.tool_button.setStyleSheet(
                f"QToolButton {{ color: {_COR_TEXTO.get(cor, cor)}; font-weight: {peso}; padding: 2px 6px; }}"
            )
        if self.status_label:
            self.status_label.setText(
                f'<span style="color:{cor}; font-size:14px;">●</span> '
                f'<b style="color:{_COR_TEXTO.get(cor, cor)};">ClaudIA QGIS</b>: {texto}'
                + (f" <span style='color:#757575'>· {detalhe}</span>" if detalhe else "")
            )

    # ------------------------------------------------------------------ gui
    def initGui(self):
        toolbar = self.iface.pluginToolBar()

        self.action = QAction(self._icone_base(), "ClaudIA QGIS", self.iface.mainWindow())
        self.action.setCheckable(True)
        self.action.setToolTip(t("menu.tooltip"))
        self.action.triggered.connect(self._alternar)

        self.conectar_action = QAction(t("menu.conectar"), self.iface.mainWindow())
        self.conectar_action.triggered.connect(self._abrir_dialogo)
        self.pagina_action = QAction(t("menu.pagina"), self.iface.mainWindow())
        self.pagina_action.triggered.connect(lambda: QDesktopServices.openUrl(QUrl(_pagina_conector())))
        self.atualizar_action = QAction(t("menu.atualizar"), self.iface.mainWindow())
        self.atualizar_action.triggered.connect(self._verificar_atualizacao)
        self.sobre_action = QAction(t("menu.sobre"), self.iface.mainWindow())
        self.sobre_action.triggered.connect(self._sobre)

        menu = QMenu()
        menu.addAction(self.conectar_action)
        menu.addAction(self.pagina_action)
        menu.addSeparator()
        menu.addAction(self.atualizar_action)
        menu.addAction(self.sobre_action)

        self.tool_button = QToolButton()
        self.tool_button.setDefaultAction(self.action)
        self.tool_button.setMenu(menu)
        self.tool_button.setPopupMode(TOOLBUTTON_MENU_POPUP)
        self.tool_button.setToolButtonStyle(_TEXT_BESIDE_ICON)
        self._toolbar_action = toolbar.addWidget(self.tool_button)

        # indicador permanente no rodapé do QGIS (o ícone sozinho era discreto demais — fundador, 13/09)
        self.status_label = QLabel()
        self.status_label.setContentsMargins(6, 0, 6, 0)
        with contextlib.suppress(Exception):
            self.iface.mainWindow().statusBar().addPermanentWidget(self.status_label)
        self._mostrar_estado("parado")

        self.iface.addPluginToMenu(MENU, self.action)
        self.iface.addPluginToMenu(MENU, self.conectar_action)
        self.iface.addPluginToMenu(MENU, self.pagina_action)
        self.iface.addPluginToMenu(MENU, self.atualizar_action)
        self.iface.addPluginToMenu(MENU, self.sobre_action)
        for sub in self.iface.pluginMenu().actions():
            if sub.text() == MENU and sub.menu():
                sub.setIcon(self._icone_base())
                break

        if _cfg("reconectar_apos_update", False, bool):
            # a versão anterior se atualizou e pediu para voltar conectada
            _set_cfg("reconectar_apos_update", False)
            with contextlib.suppress(Exception):
                self.iface.messageBar().pushSuccess(LOG_TAG, t("msg.atualizado", versao=plugin_version()))
            if _cfg("token", ""):
                self.action.setChecked(True)
                self._conectar()
        elif _cfg("autostart", False, bool) and _cfg("token", ""):
            self.action.setChecked(True)
            self._conectar()

        QTimer.singleShot(1200, self._boas_vindas)

    def unload(self):
        self._desconectar()
        # (0.15.0) os checkpoints do projeto vivem numa pasta temporária do executor
        if self.executor:
            with contextlib.suppress(Exception):
                self.executor.limpar_checkpoints()
        if self.action:
            with contextlib.suppress(Exception):
                self.action.triggered.disconnect(self._alternar)
            self.iface.removePluginMenu(MENU, self.action)
            self.action = None
        for a in (self.conectar_action, self.pagina_action, self.atualizar_action, self.sobre_action):
            if a:
                self.iface.removePluginMenu(MENU, a)
        self.conectar_action = self.pagina_action = self.atualizar_action = self.sobre_action = None
        if self._toolbar_action:
            self.iface.pluginToolBar().removeAction(self._toolbar_action)
            self._toolbar_action = None
        if self.status_label:
            with contextlib.suppress(Exception):
                self.iface.mainWindow().statusBar().removeWidget(self.status_label)
            self.status_label.deleteLater()
            self.status_label = None

    # ------------------------------------------------------------- diálogos
    def _boas_vindas(self):
        if not _cfg("first_run", True, bool):
            return
        _set_cfg("first_run", False)
        dlg = QDialog(self.iface.mainWindow())
        dlg.setWindowTitle(t("boasvindas.titulo"))
        dlg.setMinimumWidth(480)
        layout = QVBoxLayout(dlg)
        corpo = QLabel(t("boasvindas.corpo", repo=REPO_URL))
        corpo.setWordWrap(True)
        corpo.setOpenExternalLinks(True)
        layout.addWidget(corpo)
        botoes = QHBoxLayout()
        abrir = QPushButton(t("boasvindas.abrir"))
        abrir.clicked.connect(lambda: QDesktopServices.openUrl(QUrl(_pagina_conector())))
        conectar = QPushButton(t("boasvindas.conectar"))
        conectar.setDefault(True)
        conectar.clicked.connect(dlg.accept)
        conectar.clicked.connect(self._abrir_dialogo)
        fechar = QPushButton(t("boasvindas.depois"))
        fechar.clicked.connect(dlg.reject)
        botoes.addWidget(abrir)
        botoes.addStretch()
        botoes.addWidget(fechar)
        botoes.addWidget(conectar)
        layout.addLayout(botoes)
        dlg.exec()

    def _sobre(self):
        dlg = QDialog(self.iface.mainWindow())
        dlg.setWindowTitle(t("sobre.titulo"))
        layout = QVBoxLayout(dlg)
        n = self.executor.comunidade["comandos_executados"] if self.executor else 0
        texto = QLabel(
            t(
                "sobre.corpo",
                versao=plugin_version(),
                repo=REPO_URL,
                upstream=UPSTREAM_URL,
                estado=_estado_textos(self._estado)[2],
                detalhe=self._detalhe,
                n=n,
            )
        )
        texto.setWordWrap(True)
        texto.setOpenExternalLinks(True)
        layout.addWidget(texto)
        ok = QPushButton(t("sobre.fechar"))
        ok.clicked.connect(dlg.accept)
        layout.addWidget(ok, alignment=_ALIGN_RIGHT)
        dlg.exec()

    def _abrir_dialogo(self):
        dlg = ConectarDialog(self.iface.mainWindow())
        if dlg.exec():
            self._aplicar_idioma()
            self._desconectar()
            self.action.setChecked(True)
            self._conectar()

    def _aplicar_idioma(self):
        """(0.4.2) Retraduz o que fica na tela: menu, tooltip e barra de status.

        As janelas nascem traduzidas a cada abertura; o worker recebe o idioma ao
        (re)conectar.
        """
        for acao, chave in (
            (self.conectar_action, "menu.conectar"),
            (self.pagina_action, "menu.pagina"),
            (self.atualizar_action, "menu.atualizar"),
            (self.sobre_action, "menu.sobre"),
        ):
            if acao:
                acao.setText(t(chave))
        self._mostrar_estado(self._estado, self._detalhe)

    # ------------------------------------------------------------- conexão
    def _alternar(self, ligado):
        if ligado:
            if not _cfg("token", ""):
                self.action.setChecked(False)
                self._abrir_dialogo()
                return
            self._conectar()
        else:
            self._desconectar()

    def _info_projeto(self):
        projeto = QgsProject.instance()
        nome = projeto.baseName() or (os.path.basename(projeto.fileName()) if projeto.fileName() else None)
        return {"qgis_versao": Qgis.version(), "plugin_versao": plugin_version(), "projeto": nome or None}

    def _conectar(self):
        token = _cfg("token", "")
        base = _base_url()
        if self.executor is None:
            self.executor = ClaudiaExecutor(iface=self.iface)
        self.executor.ligar_log()
        self.executor.comunidade.update({"base_url": base, "estado": "conectando", "conectado": False})

        self.worker = ComunidadeWorker(base, token, self._info_projeto(), idioma=i18n.idioma())
        self.thread = QThread()
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.comando_recebido.connect(self._executar_comando, _QUEUED)
        self.worker.estado_mudou.connect(self._estado_mudou, _QUEUED)
        self.worker.versao_disponivel.connect(self._oferecer_atualizacao, _QUEUED)
        self.thread.start()

        # nome do projeto aberto acompanha o poll (aparece na página da comunidade)
        self._timer_info = QTimer()
        self._timer_info.setInterval(30_000)
        self._timer_info.timeout.connect(self._atualizar_info)
        self._timer_info.start()
        projeto = QgsProject.instance()
        with contextlib.suppress(Exception):
            projeto.readProject.connect(self._atualizar_info)
            projeto.projectSaved.connect(self._atualizar_info)
            projeto.cleared.connect(self._atualizar_info)

        self._mostrar_estado("conectando", base)
        QgsMessageLog.logMessage(t("msg.conectando_log", base=base), LOG_TAG, MSG_INFO)

    def _desconectar(self):
        if self._timer_info:
            self._timer_info.stop()
            self._timer_info = None
        projeto = QgsProject.instance()
        for sinal in (projeto.readProject, projeto.projectSaved, projeto.cleared):
            with contextlib.suppress(Exception):
                sinal.disconnect(self._atualizar_info)
        if self.worker:
            self.worker.parar()
        if self.thread:
            self.thread.quit()
            if not self.thread.wait(5000):
                # (0.4.1) NUNCA soltar a última referência de um QThread ainda rodando:
                # o Qt aborta o processo ("QThread: Destroyed while thread is still
                # running") e o QGIS fecha sem aviso. A thread fica estacionada até
                # terminar sozinha (o poll vence em até 45 s) e aí se apaga.
                zumbi = self.thread
                self._threads_zumbis.append(zumbi)
                with contextlib.suppress(Exception):
                    zumbi.finished.connect(zumbi.deleteLater)
                    zumbi.finished.connect(lambda z=zumbi: z in self._threads_zumbis and self._threads_zumbis.remove(z))
                QgsMessageLog.logMessage(t("msg.worker_demorou"), LOG_TAG, MSG_INFO)
            self.thread = None
        self.worker = None
        if self.executor:
            self.executor.desligar_log()
            self.executor.comunidade.update({"conectado": False, "estado": "parado"})
        if self.action:
            self.action.setChecked(False)
        self._mostrar_estado("parado")
        self._estado, self._detalhe = "parado", ""
        self._avisou_conexao = False
        self._avisou_rede = False

    def _atualizar_info(self, *_args):
        if self.worker:
            self.worker.atualizar_info(**self._info_projeto())

    # -------------------------------------------------- ponte comunidade→QGIS
    def _executar_comando(self, comando):
        """Thread principal: executa e devolve ao worker (que sobe o resultado)."""
        worker = self.worker
        if worker is None or self.executor is None:
            return
        envelope = self.executor.executar({"type": comando.get("type"), "params": comando.get("params") or {}})
        worker.entregar_resultado(comando.get("id"), envelope)
        n = self.executor.comunidade["comandos_executados"]
        self._mostrar_estado("conectado", t("estado.comandos", n=n, tipo=comando.get("type")))

    # ------------------------------------------------------------ atualização
    def _oferecer_atualizacao(self, info):
        """Barra 'Versão X disponível — Atualizar agora' (uma vez por versão)."""
        versao = str(info.get("versao") or "")
        if not versao or not info.get("zip_url") or self._versao_oferecida == versao or self._atualizando:
            return
        self._versao_oferecida = versao
        try:
            barra = self.iface.messageBar()
            w = barra.createMessage(LOG_TAG, t("upd.disponivel", versao=versao, atual=plugin_version()))
            botao = QPushButton(t("upd.botao"))
            botao.clicked.connect(functools.partial(self._atualizar, dict(info)))
            w.layout().addWidget(botao)
            barra.pushWidget(w, MSG_INFO)
        except Exception as e:  # sem barra (headless) — fica no log
            QgsMessageLog.logMessage(t("upd.disponivel_log", versao=versao, url=info.get("url") or RELEASES_URL, erro=e), LOG_TAG, MSG_INFO)

    def _verificar_atualizacao(self):
        """Menu 'Atualizar o plugin…': consulta a comunidade agora."""
        try:
            info = updater.consultar_ultima(_base_url())
        except Exception as e:
            with contextlib.suppress(Exception):
                self.iface.messageBar().pushWarning(LOG_TAG, t("upd.consulta_falhou", erro=e))
            return
        versao = str(info.get("versao") or "")
        if versao and info.get("zip_url") and versao_tupla(versao) > versao_tupla(plugin_version()):
            self._versao_oferecida = None
            self._oferecer_atualizacao(info)
        else:
            with contextlib.suppress(Exception):
                self.iface.messageBar().pushInfo(LOG_TAG, t("upd.ja_atual", versao=plugin_version()))

    def _atualizar(self, info):
        """Baixa o ZIP da release, valida, desconecta e troca o plugin (recarrega sozinho)."""
        if self._atualizando:
            return
        self._atualizando = True
        versao = str(info.get("versao") or "?")
        try:
            with contextlib.suppress(Exception):
                self.iface.messageBar().pushInfo(LOG_TAG, t("upd.baixando", versao=versao))
            caminho = updater.baixar_zip(str(info["zip_url"]))
            updater.validar_zip(caminho)
        except Exception as e:
            self._atualizando = False
            QgsMessageLog.logMessage(t("upd.falhou_log", erro=repr(e)), LOG_TAG, MSG_CRITICAL)
            with contextlib.suppress(Exception):
                self.iface.messageBar().pushCritical(LOG_TAG, t("upd.baixar_falhou", erro=e, url=info.get("url") or RELEASES_URL))
            return
        # a versão nova volta conectada com o mesmo token
        _set_cfg("reconectar_apos_update", bool(_cfg("token", "")))
        self._desconectar()
        # fora deste objeto: o unloadPlugin vai descarregar o plugin atual
        QTimer.singleShot(0, functools.partial(updater.instalar_e_recarregar_seguro, caminho, self.iface))

    def _estado_mudou(self, estado, detalhe):
        self._estado, self._detalhe = estado, detalhe
        if self.executor:
            self.executor.comunidade.update({"estado": estado, "detalhe": detalhe, "conectado": estado == "conectado"})
        if not self.action:
            return
        if estado == "conectado":
            self._mostrar_estado("conectado")
            if not self._avisou_conexao:
                self._avisou_conexao = True
                with contextlib.suppress(Exception):
                    self.iface.messageBar().pushSuccess(LOG_TAG, t("msg.conectado"))
        elif estado == "sem_rede":
            self._mostrar_estado("sem_rede", detalhe)
            QgsMessageLog.logMessage(detalhe, LOG_TAG, MSG_WARNING)
            # Uma vez por tentativa de conexão: só no log ninguém vê (13/09 —
            # o plugin apontava para o endereço errado e parecia "conectado").
            if not self._avisou_rede:
                self._avisou_rede = True
                with contextlib.suppress(Exception):
                    self.iface.messageBar().pushWarning(LOG_TAG, t("msg.sem_rede", detalhe=detalhe))
        elif estado == "token_invalido":
            self._mostrar_estado("token_invalido")
            QgsMessageLog.logMessage(detalhe, LOG_TAG, MSG_CRITICAL)
            with contextlib.suppress(Exception):
                self.iface.messageBar().pushCritical(LOG_TAG, t("msg.token_recusado"))
            self._desconectar()
            self._mostrar_estado("token_invalido")


def classFactory(iface):
    return ClaudiaQgisPlugin(iface)
