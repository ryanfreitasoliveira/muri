from textual import on
from textual.app import ComposeResult
from textual.screen import ModalScreen, Screen
from textual.containers import VerticalScroll, Horizontal, Vertical
from textual.widgets import (
    Label, Button, TabbedContent, TabPane, Markdown, Collapsible,
    Input, TextArea, Checkbox, Header, Footer,
)

from features.forum import (
    TAGS_DISPONIVEIS, validar_titulo, validar_resposta, usuario_cadastrado,
    criar_topico, responder_topico, listar_topicos, listar_respostas, abrir_topico,
)
from features.perfil import PainelPerfil
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
                id="aviso-exclusao", markup=False,
            )
            with Horizontal():
                yield Button("Sim, excluir conta", variant="error", id="confirmar-exclusao")
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

    def __init__(self, selecionadas: list[str] | None = None, titulo: str = "Selecione as tags"):
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
        escolhidas = [tag for tag in TAGS_DISPONIVEIS if self.query_one(f"#tag-{tag}", Checkbox).value]
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
            yield Label("Você pode usar Markdown: # título, **negrito**, listas e links.")
            yield Label("", id="erro")
            with Horizontal():
                yield Button("Criar", variant="primary", id="criar")
                yield Button("Cancelar", id="cancelar")

    @on(Button.Pressed, "#escolher-tags")
    def abrir_seletor_tags(self) -> None:
        self.app.push_screen(SeletorTagsModal(self.tags_escolhidas, "Tags do tópico"), self.atualizar_tags)

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
        self.dismiss({
            "titulo": titulo,
            "tags": self.tags_escolhidas,
            "mensagem": self.query_one("#mensagem", TextArea).text,
            "anexo": self.query_one("#anexo", Input).value,
        })


class BotaoResponder(Button):
    def __init__(self, topico_id):
        super().__init__("Adicionar comentário", variant="primary", classes="responder")
        self.topico_id = str(topico_id)


def montar_titulo_topico(topico):
    autor = topico.autor.username if topico.autor else "desconhecido"

    visualizacoes = getattr(topico, "visualizacoes", 0)
    total_comentarios = len(listar_respostas(topico.id))

    return (
        f"{autor} | {topico.titulo}"
        f"    👁 {visualizacoes}"
        f"    💬 {total_comentarios}"
    )


class TopicoItem(Collapsible):
    """Colapsável do tópico com estatísticas e comentários."""

    def __init__(self, topico):
        caixa = VerticalScroll(classes="respostas")

        comentarios = Collapsible(
            caixa,
            title="Comentarios:",
            collapsed=True,
        )

        with_botoes = Horizontal(
            comentarios,
            BotaoResponder(topico.id),
            classes="linha-comentarios",
        )

                
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
            with_botoes,
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
                    yield Input(placeholder="Buscar tópicos, dúvidas, editais...", id="busca")
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

    @on(TabbedContent.TabActivated)
    def ao_trocar_aba(self) -> None:
        # Ao abrir "Meus dados", recarrega os números (o usuário pode ter postado agora).
        if self.query_one(TabbedContent).active == "aba-perfil":
            self.query_one(PainelPerfil).atualizar()

    @on(Button.Pressed, "#btn_sair")
    def sair_da_conta(self) -> None:
        self.app.usuario_logado = None
        self.app.pop_screen()  # volta para o menu inicial (login/cadastro)

    @on(Button.Pressed, "#btn_excluir_conta")
    def solicitar_exclusao_conta(self) -> None:
        self.app.push_screen(ConfirmarExclusaoContaModal(), self.ao_confirmar_exclusao_conta)

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
        self.app.push_screen(SeletorTagsModal(self.tags_filtro, "Filtrar por tags"), self.aplicar_filtro_tags)

    def aplicar_filtro_tags(self, tags: list[str] | None) -> None:
        if tags is None:
            return
        self.tags_filtro = tags
        texto = "Filtros: " + (", ".join(tags) if tags else "nenhum")
        self.query_one("#filtros-ativos", Label).update(texto)
        self.carregar_topicos()

    def carregar_topicos(self) -> None:
        lista = self.query_one("#lista_topicos", VerticalScroll)
        lista.remove_children()
        for topico in listar_topicos():
            autor = topico.autor.username if topico.autor else "desconhecido"
            campos = " ".join([topico.titulo, topico.mensagem or "", autor, " ".join(topico.tags)]).casefold()
            if self.texto_busca and self.texto_busca not in campos:
                continue
            if self.tags_filtro and not set(self.tags_filtro).intersection(topico.tags):
                continue
            lista.mount(TopicoItem(topico))

    def carregar_respostas(self, item: TopicoItem) -> None:
        caixa = item.caixa_respostas
        caixa.remove_children()
        respostas = listar_respostas(item.topico.id)
        if not respostas:
            caixa.mount(Label("Nenhum comentário ainda."))
            return
        for resposta in respostas:
            autor = resposta.autor.username if resposta.autor else "desconhecido"
            with_box = Horizontal(
                Label(autor, classes="autor-comentario"),
                Markdown(resposta.conteudo or "*(comentário vazio)*"),
                classes="comentario",
            )
            caixa.mount(with_box)

    def achar_item(self, topico_id):
        for item in self.query(TopicoItem):
            if str(item.topico.id) == str(topico_id):
                return item
        return None

    @on(Collapsible.Expanded)
    def ao_expandir(self, event: Collapsible.Expanded):
        item = event.collapsible

        if not isinstance(item, TopicoItem):
            return

        topico_aberto, erro = abrir_topico(item.topico.id)

        if erro:
            self.notify(erro, severity="error")
            return

        # Atualiza os dados do tópico com os valores do banco.
        item.topico = topico_aberto

        # Atualiza o título com a visualização mais recente
        # e a quantidade atual de comentários.
        item.title = montar_titulo_topico(item.topico)

        self.carregar_respostas(item)

    @on(Button.Pressed, ".responder")
    def abrir_novo_comentario(self, event: Button.Pressed) -> None:
        if not usuario_cadastrado(self.usuario_logado):
            self.notify("Cadastre-se para comentar", severity="warning")
            return
        topico_id = event.button.topico_id
        self.app.push_screen(NovaRespostaModal(), lambda texto: self.ao_fechar_resposta(texto, topico_id))

    def ao_fechar_resposta(self, texto, topico_id) -> None:
        if texto is None:
            return
        _, erro = responder_topico(self.usuario_logado, topico_id, texto)
        if erro:
            self.notify(erro, severity="error")
            return
        item = self.achar_item(topico_id)
        if item:
            item.title = montar_titulo_topico(item.topico)
            self.carregar_respostas(item)
            item.colapsavel_comentarios.collapsed = False
        self.notify("Comentário adicionado!")

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
            self.usuario_logado, dados["titulo"], dados["tags"],
            dados["mensagem"], dados["anexo"],
        )
        if erro:
            self.notify(erro, severity="error")
            return
        self.notify("Tópico criado!")
        self.carregar_topicos()
