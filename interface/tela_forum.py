from textual import on
from textual.app import App, ComposeResult
from textual.screen import ModalScreen
from textual.containers import VerticalScroll, Horizontal, Vertical
from textual.widgets import (
    Label, Button, TabbedContent, TabPane, Markdown, Collapsible,
    Input, TextArea, Checkbox,
)

from features.forum import (
    TAGS_DISPONIVEIS, validar_titulo, validar_resposta, usuario_cadastrado,
    criar_topico, responder_topico, listar_topicos, listar_respostas, abrir_topico,
)
from models.usuario import Cadastro


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


class TopicoItem(Collapsible):
    """Tópico expansível com autor, conteúdo Markdown, tags e comentários colapsáveis."""
    def __init__(self, topico):
        autor = topico.autor.username if topico.autor else "desconhecido"
        conteudo = Markdown(topico.mensagem or "*(sem descrição)*", id=f"mensagem-{topico.id}")
        tags = Label("  ".join(f"[{tag}]" for tag in topico.tags) if topico.tags else "Sem tags", classes="tags-topico")
        self.caixa_respostas = Vertical(classes="lista-comentarios")
        self.comentarios = Collapsible(self.caixa_respostas, title="Comentarios:", collapsed=True, classes="comentarios")
        controles = Horizontal(self.comentarios, BotaoResponder(topico.id), classes="linha-comentarios")
        super().__init__(conteudo, tags, controles, title=f"{autor}  |  {topico.titulo}", collapsed=True)
        self.topico = topico


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


class MURI(App):
    CSS = """
    Input { width: 1fr; margin: 0 1; }
    .pesquisa { height: 5; align: center middle; }
    Button { margin: 0 1; }
    TopicoItem { margin: 0 2; }
    .tags-topico { color: $text-muted; margin: 0 1 1 2; }
    .linha-comentarios { height: auto; align: left middle; }
    .comentarios { width: 1fr; margin: 0 1; }
    .lista-comentarios { height: auto; padding: 0 1; }
    .comentario { height: auto; margin: 0 0 1 0; }
    .autor-comentario { width: 20; color: $primary; text-style: bold; }
    #lista_topicos { height: 1fr; }
    """

    def __init__(self):
        super().__init__()
        self.usuario_logado = Cadastro(
            email="teste@ufrpe.br", nome="Teste", sobrenome="Provisório",
            username="teste", tipo="universitario",
        )
        self.texto_busca = ""
        self.tags_filtro: list[str] = []

    def compose(self) -> ComposeResult:
        with TabbedContent():
            with TabPane("Perfil"):
                yield Markdown("# Perfil\n\nÁrea de perfil em desenvolvimento.")
            with TabPane("Forum"):
                with Horizontal(classes="pesquisa"):
                    yield Input(placeholder="Buscar tópicos, dúvidas, editais...", id="busca")
                    yield Button("Filtrar tags", id="filtrar-tags")
                    yield Button("Novo tópico", variant="primary", id="novo_topico")
                yield Label("", id="filtros-ativos")
                yield VerticalScroll(id="lista_topicos")
            with TabPane("Agenda"):
                yield Markdown("# Agenda\n\nÁrea de agenda em desenvolvimento.")

    def on_mount(self) -> None:
        self.carregar_topicos()

    @on(Input.Changed, "#busca")
    def ao_pesquisar(self, event: Input.Changed) -> None:
        self.texto_busca = event.value.strip().casefold()
        self.carregar_topicos()

    @on(Button.Pressed, "#filtrar-tags")
    def abrir_filtro_tags(self) -> None:
        self.push_screen(SeletorTagsModal(self.tags_filtro, "Filtrar por tags"), self.aplicar_filtro_tags)

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
    def ao_expandir(self, event: Collapsible.Expanded) -> None:
        item = event.collapsible
        if isinstance(item, TopicoItem):
            abrir_topico(item.topico.id)
            self.carregar_respostas(item)

    @on(Button.Pressed, ".responder")
    def abrir_novo_comentario(self, event: Button.Pressed) -> None:
        if not usuario_cadastrado(self.usuario_logado):
            self.notify("Cadastre-se para comentar", severity="warning")
            return
        topico_id = event.button.topico_id
        self.push_screen(NovaRespostaModal(), lambda texto: self.ao_fechar_resposta(texto, topico_id))

    def ao_fechar_resposta(self, texto, topico_id) -> None:
        if texto is None:
            return
        _, erro = responder_topico(self.usuario_logado, topico_id, texto)
        if erro:
            self.notify(erro, severity="error")
            return
        item = self.achar_item(topico_id)
        if item:
            self.carregar_respostas(item)
            item.comentarios.collapsed = False
        self.notify("Comentário adicionado!")

    @on(Button.Pressed, "#novo_topico")
    def abrir_novo_topico(self) -> None:
        if not usuario_cadastrado(self.usuario_logado):
            self.notify("Cadastre-se para criar um tópico", severity="warning")
            return
        self.push_screen(NovoTopicoModal(), self.ao_fechar_modal)

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
