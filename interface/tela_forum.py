from textual import on
from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.screen import ModalScreen, Screen
from textual.widgets import (
    Button,
    Checkbox,
    Collapsible,
    Footer,
    Header,
    Input,
    Label,
    Markdown,
    TabbedContent,
    TabPane,
    TextArea,
)

from data.armazenamento import deletar_usuario
from features.forum import (
    TAGS_DISPONIVEIS,
    abrir_topico,
    criar_topico,
    excluir_resposta,
    excluir_topico,
    listar_respostas,
    listar_topicos,
    responder_topico,
    usuario_cadastrado,
    validar_resposta,
    validar_titulo,
)
from interface.agenda import AbaCalendario
from interface.painel_mapa import PainelMapa
from interface.tela_perfil import PainelPerfil
from features.gamificacao import icone_badge_ativa, verificar_gamificacao
from interface.painel_mapa import PainelMapa
from interface.tela_perfil import PainelPerfil

SEM_TAGS = "Nenhuma tag selecionada"
AVISO_EXCLUSAO_CONTA = (
    "Esta ação é permanente. Sua conta, seus tópicos e os comentários "
    "associados serão excluídos. Não será possível desfazer."
)


# ---------- funções auxiliares ----------


def autor_com_badge(item) -> str:
    if not item.autor:
        return "desconhecido"
    return f"{item.autor.username} {icone_badge_ativa(item.autor.email)}".strip()


def montar_titulo_topico(topico) -> str:
    total_comentarios = len(listar_respostas(topico.id))
    return (
        f"{autor_com_badge(topico)} | {topico.titulo}"
        f"    👁 {topico.visualizacoes}    💬 {total_comentarios}"
    )


def texto_tags(topico) -> str:
    if not topico.tags:
        return "Sem tags"
    return "Tags: " + ", ".join(topico.tags)


# ---------- modais ----------


class ConfirmarModal(ModalScreen[bool]):
    CSS = """
    ConfirmarModal { align: center middle; }
    #caixa-confirmar { width: 62; height: auto; padding: 1 2; border: thick $error; background: $surface; }
    #texto-confirmar { height: auto; margin-bottom: 1; }
    """

    def __init__(
        self, mensagem: str, titulo: str = "", rotulo_confirmar: str = "Excluir"
    ):
        super().__init__()
        self.mensagem = mensagem
        self.titulo = titulo
        self.rotulo_confirmar = rotulo_confirmar

    def compose(self) -> ComposeResult:
        with Vertical(id="caixa-confirmar"):
            if self.titulo:
                yield Label(self.titulo)
            yield Label(self.mensagem, id="texto-confirmar", markup=False)
            with Horizontal():
                yield Button(self.rotulo_confirmar, variant="error", id="confirmar-sim")
                yield Button("Cancelar", id="confirmar-nao")

    @on(Button.Pressed, "#confirmar-sim")
    def confirmar(self) -> None:
        self.dismiss(True)

    @on(Button.Pressed, "#confirmar-nao")
    def cancelar(self) -> None:
        self.dismiss(False)


class SeletorTagsModal(ModalScreen[list[str] | None]):
    """Seleção de várias tags, usada na criação de tópico e no filtro."""

    CSS = """
    SeletorTagsModal { align: center middle; }
    #caixa-tags { width: 50; height: auto; max-height: 85%; padding: 1 2; border: thick $primary; background: $surface; }
    #opcoes-tags { height: auto; max-height: 20; }
    """

    def __init__(
        self, selecionadas: list[str] | None = None, titulo: str = "Selecione as tags"
    ):
        super().__init__()
        self.selecionadas = set(selecionadas or [])
        self.titulo = titulo

    def compose(self) -> ComposeResult:
        with Vertical(id="caixa-tags"):
            yield Label(self.titulo)
            with VerticalScroll(id="opcoes-tags"):
                for tag in TAGS_DISPONIVEIS:
                    yield Checkbox(tag, value=tag in self.selecionadas, id=f"tag-{tag}")
            with Horizontal():
                yield Button("Confirmar", variant="primary", id="confirmar-tags")
                yield Button("Cancelar", id="cancelar-tags")

    @on(Button.Pressed, "#confirmar-tags")
    def confirmar(self) -> None:
        escolhidas = [
            tag
            for tag in TAGS_DISPONIVEIS
            if self.query_one(f"#tag-{tag}", Checkbox).value
        ]
        self.dismiss(escolhidas)

    @on(Button.Pressed, "#cancelar-tags")
    def cancelar(self) -> None:
        self.dismiss(None)


class NovoTopicoModal(ModalScreen[dict | None]):
    CSS = """
    NovoTopicoModal { align: center middle; }
    #caixa { width: 65; height: auto; max-height: 90%; padding: 1 2; border: thick $primary; background: $surface; }
    #erro { color: $error; }
    #tags-escolhidas { height: auto; color: $text-muted; }
    """

    def __init__(self):
        super().__init__()
        self.tags_escolhidas: list[str] = []

    def compose(self) -> ComposeResult:
        with Vertical(id="caixa"):
            yield Label("Novo tópico")
            yield Input(placeholder="Título", id="titulo")
            with Horizontal():
                yield Button("Escolher tags", id="escolher-tags")
                yield Label(SEM_TAGS, id="tags-escolhidas")
            yield TextArea(id="mensagem", language=None)
            yield Input(placeholder="Caminho do anexo (opcional)", id="anexo")
            yield Label(
                "Você pode usar Markdown: # título, **negrito**, listas e links."
            )
            yield Label("", id="erro")
            with Horizontal():
                yield Button("Criar", variant="primary", id="criar")
                yield Button("Cancelar", id="cancelar")

    @on(Button.Pressed, "#escolher-tags")
    def abrir_seletor_tags(self) -> None:
        self.app.push_screen(
            SeletorTagsModal(self.tags_escolhidas, "Tags do tópico"),
            self.atualizar_tags,
        )

    def atualizar_tags(self, tags: list[str] | None) -> None:
        if tags is None:
            return
        self.tags_escolhidas = tags
        self.query_one("#tags-escolhidas", Label).update(", ".join(tags) or SEM_TAGS)

    @on(Button.Pressed, "#cancelar")
    def cancelar(self) -> None:
        self.dismiss(None)

    @on(Button.Pressed, "#criar")
    def criar(self) -> None:
        titulo = self.query_one("#titulo", Input).value
        erro = validar_titulo(titulo)
        if erro:
            self.query_one("#erro", Label).update(erro)
            return
        self.dismiss(
            {
                "titulo": titulo,
                "tags": self.tags_escolhidas,
                "mensagem": self.query_one("#mensagem", TextArea).text,
                "anexo": self.query_one("#anexo", Input).value,
            }
        )


class NovaRespostaModal(ModalScreen[str | None]):
    CSS = """
    NovaRespostaModal { align: center middle; }
    #caixa { width: 60; height: auto; padding: 1 2; border: thick $primary; background: $surface; }
    #erro { color: $error; }
    """

    def compose(self) -> ComposeResult:
        with Vertical(id="caixa"):
            yield Label("Novo comentário")
            yield TextArea(id="conteudo")
            yield Label("", id="erro")
            with Horizontal():
                yield Button("Enviar", variant="primary", id="enviar")
                yield Button("Cancelar", id="cancelar")

    @on(Button.Pressed, "#cancelar")
    def cancelar(self) -> None:
        self.dismiss(None)

    @on(Button.Pressed, "#enviar")
    def enviar(self) -> None:
        texto = self.query_one("#conteudo", TextArea).text
        erro = validar_resposta(texto)
        if erro:
            self.query_one("#erro", Label).update(erro)
            return
        self.dismiss(texto)


# ---------- botões e itens da lista ----------


class BotaoResponder(Button):
    def __init__(self, topico_id):
        super().__init__("Adicionar comentário", variant="primary", classes="responder")
        self.topico_id = str(topico_id)


class BotaoExcluirTopico(Button):
    def __init__(self, topico_id):
        super().__init__("Excluir tópico", variant="error", classes="excluir-topico")
        self.topico_id = str(topico_id)


class BotaoExcluirComentario(Button):
    def __init__(self, resposta_id, topico_id):
        super().__init__("Excluir", variant="error", classes="excluir-comentario")
        self.resposta_id = str(resposta_id)
        self.topico_id = str(topico_id)


class TopicoItem(Collapsible):
    """Colapsável do tópico, com estatísticas, comentários e ações."""

    def __init__(self, topico, pode_excluir: bool = False):
        caixa_respostas = VerticalScroll(classes="respostas")
        comentarios = Collapsible(caixa_respostas, title="Comentários:", collapsed=True)

        acoes = [comentarios, BotaoResponder(topico.id)]
        if pode_excluir:
            acoes.append(BotaoExcluirTopico(topico.id))

        super().__init__(
            Label(texto_tags(topico), markup=False, classes="tags-topico"),
            Label(
                topico.mensagem or "(sem mensagem)",
                markup=False,
                classes="texto-topico",
            ),
            Horizontal(*acoes, classes="linha-comentarios"),
            title=montar_titulo_topico(topico),
            collapsed=True,
        )
        self.topico = topico
        self.caixa_respostas = caixa_respostas
        self.colapsavel_comentarios = comentarios


# ---------- tela principal ----------


class TelaForum(Screen):
    """Tela principal, aberta depois do login/cadastro. Recebe o usuário logado."""

    TITLE = "Muri.app"
    CSS = """
    TelaForum Input { width: 1fr; margin: 0 1; }
    TelaForum .pesquisa { height: 5; align: center middle; }
    TelaForum Button { margin: 0 1; }
    TelaForum TopicoItem { margin: 0 2; }
    TelaForum .tags-topico { color: $text-muted; margin: 0 1 1 2; }
    TelaForum .respostas { height: auto; max-height: 15; width: 1fr; margin: 0 1; }
    TelaForum .comentario { height: auto; margin: 0 0 1 0; }
    TelaForum .comentario Markdown { width: 1fr; }
    TelaForum .excluir-comentario { min-width: 10; }
    TelaForum .autor-comentario { width: 20; color: $primary; text-style: bold; }
    TelaForum #lista_topicos { height: 1fr; }
    TelaForum CollapsibleTitle { background: transparent; }
    TelaForum CollapsibleTitle:hover { background: transparent; }
    TelaForum .texto-topico { margin-bottom: 2; }
    TelaForum .linha-comentarios { height: auto; min-height: 3; align: left middle; }
    TelaForum .linha-comentarios Collapsible { height: auto; min-height: 3; margin: 0; padding: 0; }
    TelaForum .linha-comentarios CollapsibleTitle { height: 3; padding: 0 1; }
    """

    def __init__(self, usuario):
        super().__init__()
        self.usuario_logado = usuario
        self.texto_busca = ""
        self.tags_filtro: list[str] = []

    def compose(self) -> ComposeResult:
        yield Header(show_clock=False)
        with TabbedContent(initial="aba-forum"):
            with TabPane("Fórum", id="aba-forum"):
                with Horizontal(classes="pesquisa"):
                    yield Input(
                        placeholder="Buscar tópicos, dúvidas, editais...", id="busca"
                    )
                    yield Button("Filtrar tags", id="filtrar-tags")
                    yield Button("Novo tópico", variant="primary", id="novo_topico")
                yield Label("", id="filtros-ativos")
                yield VerticalScroll(id="lista_topicos")
            with TabPane("Meus dados", id="aba-perfil"):
                yield PainelPerfil(self.usuario_logado)
            with TabPane("Mapa", id="aba-mapa"):
                yield PainelMapa()
            with TabPane("Agenda", id="aba-agenda"):
                yield AbaCalendario(self.usuario_logado)
        yield Footer()

    def on_mount(self) -> None:
        self.carregar_topicos()
        self.conferir_gamificacao()

    def conferir_gamificacao(self) -> None:
        for aviso in verificar_gamificacao(self.usuario_logado):
            self.notify(aviso, title="Gamificação")

    # ----- abas e conta -----

    @on(TabbedContent.TabActivated)
    def ao_trocar_aba(self) -> None:
        aba = self.query_one(TabbedContent).active
        if aba == "aba-perfil":
            self.conferir_gamificacao()
            self.query_one(PainelPerfil).atualizar()
        elif aba == "aba-forum":
            self.carregar_topicos()

    @on(PainelPerfil.PerfilAtualizado)
    def ao_atualizar_perfil(self, event: PainelPerfil.PerfilAtualizado) -> None:
        self.usuario_logado = event.usuario
        self.app.usuario_logado = event.usuario
        self.query_one(AbaCalendario).usuario = event.usuario
        self.query_one(AbaCalendario).recarregar_tarefas()

    @on(Button.Pressed, "#btn_sair")
    def sair_da_conta(self) -> None:
        self.app.usuario_logado = None
        self.app.pop_screen()

    @on(Button.Pressed, "#btn_excluir_conta")
    def pedir_exclusao_conta(self) -> None:
        self.app.push_screen(
            ConfirmarModal(
                AVISO_EXCLUSAO_CONTA,
                titulo="Excluir conta?",
                rotulo_confirmar="Sim, excluir conta",
            ),
            self.ao_confirmar_exclusao_conta,
        )

    def ao_confirmar_exclusao_conta(self, confirmou: bool) -> None:
        if not confirmou:
            return
        try:
            excluida = deletar_usuario(self.usuario_logado.email)
        except Exception as erro:
            self.notify(f"Não foi possível excluir a conta: {erro}", severity="error")
            return
        if not excluida:
            self.notify("A conta não foi encontrada.", severity="error")
            return
        self.app.usuario_logado = None
        self.app.pop_screen()
        self.notify("Conta excluída com sucesso.")

    # ----- busca e filtro -----

    @on(Input.Changed, "#busca")
    def ao_pesquisar(self, event: Input.Changed) -> None:
        self.texto_busca = event.value.strip().casefold()
        self.carregar_topicos()

    @on(Button.Pressed, "#filtrar-tags")
    def abrir_filtro_tags(self) -> None:
        self.app.push_screen(
            SeletorTagsModal(self.tags_filtro, "Filtrar por tags"),
            self.aplicar_filtro_tags,
        )

    def aplicar_filtro_tags(self, tags: list[str] | None) -> None:
        if tags is None:
            return
        self.tags_filtro = tags
        self.query_one("#filtros-ativos", Label).update(
            "Filtros: " + (", ".join(tags) or "nenhum")
        )
        self.carregar_topicos()

    def topico_passa_nos_filtros(self, topico) -> bool:
        if self.tags_filtro and not set(self.tags_filtro) & set(topico.tags):
            return False
        if not self.texto_busca:
            return True
        campos = " ".join(
            [
                topico.titulo,
                topico.mensagem or "",
                autor_com_badge(topico),
                " ".join(topico.tags),
            ]
        ).casefold()
        return self.texto_busca in campos

    # ----- listagem de tópicos e comentários -----

    def carregar_topicos(self) -> None:
        lista = self.query_one("#lista_topicos", VerticalScroll)
        lista.remove_children()
        email = self.usuario_logado.email
        for topico in listar_topicos():
            if not self.topico_passa_nos_filtros(topico):
                continue
            pode_excluir = bool(topico.autor and topico.autor.email == email)
            lista.mount(TopicoItem(topico, pode_excluir))

    def carregar_respostas(self, item: TopicoItem) -> None:
        caixa = item.caixa_respostas
        caixa.remove_children()

        respostas = listar_respostas(item.topico.id)
        if not respostas:
            caixa.mount(Label("Nenhum comentário ainda."))
            return

        email = self.usuario_logado.email
        for resposta in respostas:
            partes = [
                Label(
                    autor_com_badge(resposta),
                    classes="autor-comentario",
                    markup=False,
                ),
                Markdown(resposta.conteudo or "*(comentário vazio)*"),
            ]
            if resposta.autor and resposta.autor.email == email:
                partes.append(BotaoExcluirComentario(resposta.id, item.topico.id))
            caixa.mount(Horizontal(*partes, classes="comentario"))

    def achar_item(self, topico_id) -> TopicoItem | None:
        for item in self.query(TopicoItem):
            if str(item.topico.id) == str(topico_id):
                return item
        return None

    def atualizar_item(self, topico_id) -> TopicoItem | None:
        item = self.achar_item(topico_id)
        if item:
            item.title = montar_titulo_topico(item.topico)
            self.carregar_respostas(item)
        return item

    @on(Collapsible.Expanded)
    def ao_expandir(self, event: Collapsible.Expanded) -> None:
        item = event.collapsible
        if not isinstance(item, TopicoItem):
            return
        topico, erro = abrir_topico(item.topico.id)
        if erro:
            self.notify(erro, severity="error")
            return
        item.topico = topico
        item.title = montar_titulo_topico(topico)
        self.carregar_respostas(item)

    # ----- novo tópico -----

    @on(Button.Pressed, "#novo_topico")
    def abrir_novo_topico(self) -> None:
        if not usuario_cadastrado(self.usuario_logado):
            self.notify("Cadastre-se para criar um tópico", severity="warning")
            return
        self.app.push_screen(NovoTopicoModal(), self.ao_fechar_novo_topico)

    def ao_fechar_novo_topico(self, dados: dict | None) -> None:
        if dados is None:
            return
        _, erro = criar_topico(
            self.usuario_logado,
            dados["titulo"],
            dados["tags"],
            dados["mensagem"],
            dados["anexo"],
        )
        if erro:
            self.notify(erro, severity="error")
            return
        self.notify("Tópico criado!")
        self.carregar_topicos()
        self.conferir_gamificacao()

    # ----- novo comentário -----

    @on(Button.Pressed, ".responder")
    def abrir_novo_comentario(self, event: Button.Pressed) -> None:
        if not usuario_cadastrado(self.usuario_logado):
            self.notify("Cadastre-se para comentar", severity="warning")
            return
        topico_id = event.button.topico_id
        self.app.push_screen(
            NovaRespostaModal(),
            lambda texto: self.ao_fechar_novo_comentario(texto, topico_id),
        )

    def ao_fechar_novo_comentario(self, texto: str | None, topico_id) -> None:
        if texto is None:
            return
        _, erro = responder_topico(self.usuario_logado, topico_id, texto)
        if erro:
            self.notify(erro, severity="error")
            return
        item = self.atualizar_item(topico_id)
        if item:
            item.colapsavel_comentarios.collapsed = False
        self.notify("Comentário adicionado!")
        self.conferir_gamificacao()

    # ----- exclusão de tópico -----

    @on(Button.Pressed, ".excluir-topico")
    def pedir_exclusao_topico(self, event: Button.Pressed) -> None:
        event.stop()
        topico_id = event.button.topico_id
        self.app.push_screen(
            ConfirmarModal(
                "Excluir este tópico? Os comentários dele também serão apagados."
            ),
            lambda confirmou: self.ao_confirmar_exclusao_topico(confirmou, topico_id),
        )

    def ao_confirmar_exclusao_topico(self, confirmou: bool, topico_id) -> None:
        if not confirmou:
            return
        _, erro = excluir_topico(self.usuario_logado, topico_id)
        if erro:
            self.notify(erro, severity="error")
            return
        self.notify("Tópico excluído.")
        self.carregar_topicos()

    # ----- exclusão de comentário -----

    @on(Button.Pressed, ".excluir-comentario")
    def pedir_exclusao_comentario(self, event: Button.Pressed) -> None:
        event.stop()
        resposta_id = event.button.resposta_id
        topico_id = event.button.topico_id
        self.app.push_screen(
            ConfirmarModal("Excluir este comentário?"),
            lambda confirmou: self.ao_confirmar_exclusao_comentario(
                confirmou, resposta_id, topico_id
            ),
        )

    def ao_confirmar_exclusao_comentario(
        self, confirmou: bool, resposta_id, topico_id
    ) -> None:
        if not confirmou:
            return
        _, erro = excluir_resposta(self.usuario_logado, resposta_id)
        if erro:
            self.notify(erro, severity="error")
            return
        self.notify("Comentário excluído.")
        self.atualizar_item(topico_id)
