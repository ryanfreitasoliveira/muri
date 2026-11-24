from textual import on
from textual.app import App, ComposeResult
from textual.containers import Vertical, Horizontal, VerticalScroll
from textual.widgets import Header, Footer, Button, Label,LoadingIndicator

from interface.menu_cadastro import Muri_Cadastro
from interface.menu_login import TelaLogin
from interface.tela_forum import TelaForum
from models.usuario import Cadastro


class Muri_app(App):
    TITLE = "Muri.app"
    BINDINGS = [
        ("q", "quit", "Sair"),
        ("t", "change_theme", "Mudar Tema"),
    ]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Usuário da sessão. Login/cadastro preenchem; "Sair da conta" limpa.
        self.usuario_logado: Cadastro | None = None

    def compose(self) -> ComposeResult:
        yield Header(show_clock=False)
        with VerticalScroll():
            with Vertical(id="form_container"):
                yield Label("Olá!! Seja bem-vindo ao Muri", id="label_titulo")
                yield Label("O forum de discussão da UFRPE", id="label_subtitulo")
                yield Label("Faça seu login ou cadastre-se", id="label_subtitulo2")

            with Horizontal(id="buttons_container"):
                yield Button("Login", variant="primary", id="btn_login")
                yield Button("Cadastro", variant="primary", id="btn_cadastro")
        yield Footer()

    def action_change_theme(self) -> None:
        self.theme = "textual-dark" if self.theme == "textual-light" else "textual-light"

    @on(Button.Pressed, "#btn_cadastro")
    def abrir_cadastro(self) -> None:
        self.push_screen(Muri_Cadastro(), self.entrar_no_forum)

    @on(Button.Pressed, "#btn_login")
    def abrir_login(self) -> None:
        self.push_screen(TelaLogin(), self.entrar_no_forum)

    def entrar_no_forum(self, usuario: Cadastro | None) -> None:
        """Callback único: roda quando cadastro OU login terminam com sucesso.
        Se o usuário apertou ESC (voltar), chega None e nada acontece."""
        if usuario is None:
            return
        self.usuario_logado = usuario
        self.push_screen(TelaForum(usuario))


if __name__ == "__main__":
    Muri_app().run()
