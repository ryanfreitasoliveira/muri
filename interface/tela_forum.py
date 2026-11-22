from textual import on
from textual.app import ComposeResult
from textual.screen import ModalScreen, Screen
from textual.containers import VerticalScroll, Horizontal, Vertical
from textual.widgets import (
    Label,
    Button,
    TabbedContent,
    TabPane,
    Markdown,
    Collapsible,
    Input,
    TextArea,
    Checkbox,
    Header,
    Footer,
)

from features.forum import (
    TAGS_DISPONIVEIS,
    validar_titulo,
    validar_resposta,
    usuario_cadastrado,
    criar_topico,
    responder_topico,
    listar_topicos,
    listar_respostas,
    abrir_topico,
    excluir_topico,
    excluir_resposta,
)
from features.gamificacao import icone_badge_ativa, verificar_gamificacao
from interface.tela_perfil import PainelPerfil
from data.armazenamento import deletar_usuario


class ConfirmarExclusaoContaModal(ModalScreen[bool]):
    """Confirmação antes de excluir permanentemente a conta."""

    CSS = """
    ConfirmarExclusaoContaModal { align: center middle; }
    #caixa-exclusao { width: 62; height: auto; padding: 1 2; border: thick $error; background: $surface; }
    #aviso-exclusao { height: auto; margin-bottom: 1; }
    """

    def compose(self) -> ComposeResult:
        with Vertical(id="caixa-exclusao"):
            yield Label("Excluir conta?")
            yield Label(
                "Esta ação é permanente. Sua conta, seus tópicos e os comentários "
                "associados serão excluídos. Não será possível desfazer.",
                id="aviso-exclusao",
                markup=False,
            )
            with Horizontal():
                yield Button(
                    "Sim, excluir conta", variant="error", id="confirmar-exclusao"
                )
                yield Button("Cancelar", id="cancelar-exclusao")

    @on(Button.Pressed, "#confirmar-exclusao")
    def confirmar(self) -> None:
        self.dismiss(True)

    @on(Button.Pressed, "#cancelar-exclusao")
    def cancelar(self) -> None:
        self.dismiss(False)


class SeletorTagsModal(ModalScreen[list[str] | None]):
    """Permite selecionar várias tags, tanto na criação quanto no filtro."""

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
                yield Label("Nenhuma tag selecionada", id="tags-escolhidas")
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
        if tags is not None:
            self.tags_escolhidas = tags
            texto = ", ".join(tags) if tags else "Nenhuma tag selecionada"
            self.query_one("#tags-escolhidas", Label).update(texto)

    @on(Button.Pressed, "#cancelar")
    def cancelar(self) -> None:
        self.dismiss(None)

    @on(Button.Pressed, "#criar")
    def confirmar(self) -> None:
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


class ConfirmarModal(ModalScreen[bool]):
    CSS = """
    ConfirmarModal { align: center middle; }
    #caixa-confirmar { width: 60; height: auto; padding: 1 2; border: thick $error; background: $surface; }
    #texto-confirmar { height: auto; margin-bottom: 1; }
    """

    def __init__(self, pergunta: str):
        super().__init__()
        self.pergunta = pergunta

    def compose(self) -> ComposeResult:
        with Vertical(id="caixa-confirmar"):
            yield Label(self.pergunta, id="texto-confirmar", markup=False)
            with Horizontal():
                yield Button("Excluir", variant="error", id="confirmar-sim")
                yield Button("Cancelar", id="confirmar-nao")

    @on(Button.Pressed, "#confirmar-sim")
    def sim(self) -> None:
        self.dismiss(True)

    @on(Button.Pressed, "#confirmar-nao")
    def nao(self) -> None:
        self.dismiss(False)


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


def autor_com_badge(item) -> str:
    if not item.autor:
        return "desconhecido"
    return f"{item.autor.username} {icone_badge_ativa(item.autor.email)}".strip()


def montar_titulo_topico(topico) -> str:
    total_comentarios = len(listar_respostas(topico.id))
    return f"{autor_com_badge(topico)} | {topico.titulo}    👁 {topico.visualizacoes}    💬 {total_comentarios}"


class TopicoItem(Collapsible):
    """Colapsável do tópico com estatísticas e comentários."""

    def __init__(self, topico, pode_excluir: bool = False):
        caixa = VerticalScroll(classes="respostas")
        comentarios = Collapsible(caixa, title="Comentarios:", collapsed=True)
        botoes = [comentarios, BotaoResponder(topico.id)]
        if pode_excluir:
            botoes.append(BotaoExcluirTopico(topico.id))
        linha = Horizontal(*botoes, classes="linha-comentarios")
        tags = Label(
            "Tags: " + ", ".join(topico.tags) if topico.tags else "Sem tags",
            markup=False,
            classes="tags-topico",
        )
        super().__init__(
            tags,
            Label(
                topico.mensagem or "(sem mensagem)",
                markup=False,
                classes="texto-topico",
            ),
            linha,
            title=montar_titulo_topico(topico),
            collapsed=True,
        )
        self.topico = topico
        self.caixa_respostas = caixa
        self.colapsavel_comentarios = comentarios


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


class TelaForum(Screen):
    """Tela principal, aberta DEPOIS do login/cadastro. Recebe o usuário logado."""

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
            with TabPane("Agenda", id="aba-agenda"):
                yield Markdown("# Agenda\n\nÁrea de agenda em desenvolvimento.")
        yield Footer()

    def on_mount(self) -> None:
        self.carregar_topicos()
        self.conferir_gamificacao()

    def conferir_gamificacao(self) -> None:
        for aviso in verificar_gamificacao(self.usuario_logado):
            self.notify(aviso, title="Gamificação")

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

    @on(Button.Pressed, "#btn_sair")
    def sair_da_conta(self) -> None:
        self.app.usuario_logado = None
        self.app.pop_screen()

    @on(Button.Pressed, "#btn_excluir_conta")
    def solicitar_exclusao_conta(self) -> None:
        self.app.push_screen(
            ConfirmarExclusaoContaModal(), self.ao_confirmar_exclusao_conta
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
            "Filtros: " + (", ".join(tags) if tags else "nenhum")
        )
        self.carregar_topicos()

    def carregar_topicos(self) -> None:
        lista = self.query_one("#lista_topicos", VerticalScroll)
        lista.remove_children()
        email = self.usuario_logado.email
        for topico in listar_topicos():
            campos = " ".join(
                [
                    topico.titulo,
                    topico.mensagem or "",
                    autor_com_badge(topico),
                    " ".join(topico.tags),
                ]
            ).casefold()
            if self.texto_busca and self.texto_busca not in campos:
                continue
            if self.tags_filtro and not set(self.tags_filtro).intersection(topico.tags):
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

    def achar_item(self, topico_id):
        for item in self.query(TopicoItem):
            if str(item.topico.id) == str(topico_id):
                return item
        return None

    def atualizar_item(self, topico_id):
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
        topico_aberto, erro = abrir_topico(item.topico.id)
        if erro:
            self.notify(erro, severity="error")
            return
        item.topico = topico_aberto
        item.title = montar_titulo_topico(topico_aberto)
        self.carregar_respostas(item)

    @on(Button.Pressed, ".responder")
    def abrir_novo_comentario(self, event: Button.Pressed) -> None:
        if not usuario_cadastrado(self.usuario_logado):
            self.notify("Cadastre-se para comentar", severity="warning")
            return
        topico_id = event.button.topico_id
        self.app.push_screen(
            NovaRespostaModal(), lambda texto: self.ao_fechar_resposta(texto, topico_id)
        )

    def ao_fechar_resposta(self, texto, topico_id) -> None:
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

    @on(Button.Pressed, ".excluir-topico")
    def pedir_exclusao_topico(self, event: Button.Pressed) -> None:
        event.stop()
        topico_id = event.button.topico_id
        self.app.push_screen(
            ConfirmarModal(
                "Excluir este tópico? Os comentários dele também serão apagados."
            ),
            lambda ok: self.ao_confirmar_exclusao_topico(ok, topico_id),
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

    @on(Button.Pressed, ".excluir-comentario")
    def pedir_exclusao_comentario(self, event: Button.Pressed) -> None:
        event.stop()
        resposta_id = event.button.resposta_id
        topico_id = event.button.topico_id
        self.app.push_screen(
            ConfirmarModal("Excluir este comentário?"),
            lambda ok: self.ao_confirmar_exclusao_comentario(
                ok, resposta_id, topico_id
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

    @on(Button.Pressed, "#novo_topico")
    def abrir_novo_topico(self) -> None:
        if not usuario_cadastrado(self.usuario_logado):
            self.notify("Cadastre-se para criar um tópico", severity="warning")
            return
        self.app.push_screen(NovoTopicoModal(), self.ao_fechar_modal)

    def ao_fechar_modal(self, dados: dict | None) -> None:
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
