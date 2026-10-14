from textual import on
from textual.app import ComposeResult
from textual.containers import Vertical, VerticalScroll
from textual.screen import Screen
from textual.widgets import Header, Footer, Button, Label, Input

from features.autenticacao import cadastrar_usuario


class Muri_Cadastro(Screen):
    TITLE = "Muri.app"
    BINDINGS = [("escape", "app.pop_screen", "Voltar")]

    def compose(self) -> ComposeResult:
        yield Header(show_clock=False)
        with VerticalScroll():
            with Vertical(id="form_container"):
                yield Label("Faça o seu cadastro aqui:", id="label_titulo")

            with Vertical(id="inputs_container"):
                yield Input(placeholder="Insira seu nome", id="input_nome")
                yield Input(placeholder="Insira seu sobrenome", id="input_sobrenome")
                yield Input(placeholder="Insira o seu e-mail", id="input_email")
                yield Input(placeholder="Insira seu username", id="input_username")
                yield Input(placeholder="Insira sua senha", password=True, id="input_senha")
                yield Button("Cadastrar", variant="primary", id="btn_enviar")
                yield Label("", id="label_status")
        yield Footer()

    @on(Input.Submitted, "#input_senha")
    @on(Button.Pressed, "#btn_enviar")
    def processar_cadastro(self) -> None:
        # 1. Lê o que o usuário digitou (front-end)
        valor = lambda id_: self.query_one(f"#{id_}", Input).value
        label_status = self.query_one("#label_status", Label)

        # 2. Regras de negócio ficam em features/autenticacao.py
        usuario, erro = cadastrar_usuario(
            valor("input_nome"), valor("input_sobrenome"), valor("input_email"),
            valor("input_username"), valor("input_senha"),
        )
        if erro:
            label_status.styles.color = "red"
            label_status.update(erro)
            return

        # 3. Cadastro ok -> devolve o usuário; o Muri_app abre o fórum
        self.dismiss(usuario)
