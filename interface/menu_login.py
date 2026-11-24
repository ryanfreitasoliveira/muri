from textual import on
from textual.app import ComposeResult
from textual.containers import Vertical, VerticalScroll
from textual.screen import Screen
from textual.widgets import Header, Footer, Button, Label, Input

from features.autenticacao import autenticar


class TelaLogin(Screen):
    TITLE = "Muri.app"
    BINDINGS = [("escape", "app.pop_screen", "Voltar")]

    def compose(self) -> ComposeResult:
        yield Header(show_clock=False)
        with VerticalScroll():
            with Vertical():
                yield Label("Faça o seu login aqui", id="Descricao_login")
                yield Input(placeholder="Insira seu username/email", id="Input_un_ou_email")
                yield Input(placeholder="Insira sua senha", password=True, id="Input_senha")
                yield Button("Enviar", variant="primary", id="Button_envio")
                yield Label("", id="Label_resultado")
        yield Footer()

    @on(Input.Submitted, "#Input_senha")
    @on(Button.Pressed, "#Button_envio")
    def processar_login(self) -> None:
        username_ou_email = self.query_one("#Input_un_ou_email", Input).value
        senha = self.query_one("#Input_senha", Input).value
        resultado = self.query_one("#Label_resultado", Label)

        usuario, erro = autenticar(username_ou_email, senha)
        if erro:
            resultado.styles.color = "red"
            resultado.update(erro)
            return

        # Login ok -> devolve o usuário; o Muri_app abre o fórum
        self.dismiss(usuario)
