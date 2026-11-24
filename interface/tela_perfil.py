from textual import on
from textual.app import ComposeResult
from textual.containers import Grid, Horizontal, Vertical, VerticalScroll
from textual.message import Message
from textual.screen import ModalScreen
from textual.widgets import Button, Input, Label, RadioButton, RadioSet

from features.autenticacao import atualizar_perfil, validar_dados_perfil
from features.gamificacao import escolher_badge, resumo_gamificacao
from features.perfil import resumo_do_usuario
from models.usuario import Cadastro


def montar_barra(progresso: int, meta: int, largura: int = 20) -> str:
    cheios = round(largura * progresso / meta) if meta else 0
    return "█" * cheios + "░" * (largura - cheios) + f"  {progresso}/{meta}"


class ConfirmarSenhaModal(ModalScreen[Cadastro | None]):
    CSS = """
    ConfirmarSenhaModal { align: center middle; }
    #caixa-senha { width: 56; height: auto; padding: 1 2; border: thick $primary; background: $surface; }
    #caixa-senha Horizontal { height: auto; }
    #erro-senha { color: $error; height: auto; }
    """

    def __init__(self, acao):
        super().__init__()
        self.acao = acao

    def compose(self) -> ComposeResult:
        with Vertical(id="caixa-senha"):
            yield Label("Digite sua senha para confirmar as alterações")
            yield Input(placeholder="Sua senha", password=True, id="confirmar-senha")
            yield Label("", id="erro-senha", markup=False)
            with Horizontal():
                yield Button("Confirmar", variant="primary", id="senha-confirmar")
                yield Button("Voltar", id="senha-voltar")

    @on(Input.Submitted, "#confirmar-senha")
    @on(Button.Pressed, "#senha-confirmar")
    def confirmar(self) -> None:
        senha = self.query_one("#confirmar-senha", Input).value
        resultado, erro = self.acao(senha)
        if erro:
            self.query_one("#erro-senha", Label).update(erro)
            return
        self.dismiss(resultado)

    @on(Button.Pressed, "#senha-voltar")
    def voltar(self) -> None:
        self.dismiss(None)


class EditarPerfilModal(ModalScreen[Cadastro | None]):
    CSS = """
    EditarPerfilModal { align: center middle; }
    #caixa-perfil { width: 65; height: auto; max-height: 90%; padding: 1 2; border: thick $primary; background: $surface; }
    #caixa-perfil .rotulo { margin-top: 1; text-style: bold; }
    #caixa-perfil Horizontal { height: auto; }
    #erro { color: $error; height: auto; }
    """

    def __init__(self, usuario):
        super().__init__()
        self.usuario = usuario

    def compose(self) -> ComposeResult:
        with VerticalScroll(id="caixa-perfil"):
            yield Label("Editar dados")
            yield Label("Nome", classes="rotulo")
            yield Input(value=self.usuario.nome, placeholder="Nome", id="edit-nome")
            yield Label("Sobrenome", classes="rotulo")
            yield Input(
                value=self.usuario.sobrenome,
                placeholder="Sobrenome",
                id="edit-sobrenome",
            )
            yield Label("E-mail", classes="rotulo")
            yield Input(value=self.usuario.email, placeholder="E-mail", id="edit-email")
            yield Label("Username", classes="rotulo")
            yield Input(
                value=self.usuario.username, placeholder="Username", id="edit-username"
            )
            yield Label("", id="erro", markup=False)
            with Horizontal():
                yield Button("Salvar", variant="primary", id="salvar-perfil")
                yield Button("Cancelar", id="cancelar-perfil")

    def valor(self, id_: str) -> str:
        return self.query_one(f"#{id_}", Input).value

    @on(Button.Pressed, "#cancelar-perfil")
    def cancelar(self) -> None:
        self.dismiss(None)

    @on(Button.Pressed, "#salvar-perfil")
    def pedir_senha(self) -> None:
        nome = self.valor("edit-nome")
        sobrenome = self.valor("edit-sobrenome")
        email = self.valor("edit-email")
        username = self.valor("edit-username")
        rotulo_erro = self.query_one("#erro", Label)

        erro = validar_dados_perfil(self.usuario, nome, sobrenome, email, username)
        if erro:
            rotulo_erro.update(erro)
            return

        atuais = (
            self.usuario.nome,
            self.usuario.sobrenome,
            self.usuario.email,
            self.usuario.username,
        )
        novos = (
            nome.strip(),
            sobrenome.strip(),
            email.strip().lower(),
            username.strip(),
        )
        if novos == atuais:
            rotulo_erro.update("Nenhuma alteração foi feita.")
            return

        rotulo_erro.update("")
        confirmacao = ConfirmarSenhaModal(
            lambda senha: atualizar_perfil(
                self.usuario, nome, sobrenome, email, username, senha
            )
        )
        self.app.push_screen(confirmacao, self.ao_confirmar_senha)

    def ao_confirmar_senha(self, novo_usuario) -> None:
        if novo_usuario is not None:
            self.dismiss(novo_usuario)


class SeletorBadgeModal(ModalScreen[str | None]):
    CSS = """
    SeletorBadgeModal { align: center middle; }
    #caixa-badges { width: 60; height: auto; max-height: 85%; padding: 1 2; border: thick $primary; background: $surface; }
    #opcoes-badges { height: auto; margin: 1 0; }
    """

    def __init__(self, badges: list[dict], ativa_id: str | None):
        super().__init__()
        self.badges = badges
        self.ativa_id = ativa_id

    def compose(self) -> ComposeResult:
        with Vertical(id="caixa-badges"):
            yield Label("Escolha a badge que aparece ao lado do seu nome")
            with RadioSet(id="opcoes-badges"):
                for badge in self.badges:
                    yield RadioButton(
                        f"{badge['icone']} {badge['nome']}",
                        value=badge["id"] == self.ativa_id,
                        name=badge["id"],
                    )
            with Horizontal():
                yield Button("Confirmar", variant="primary", id="confirmar-badge")
                yield Button("Cancelar", id="cancelar-badge")

    @on(Button.Pressed, "#confirmar-badge")
    def confirmar(self) -> None:
        escolhido = self.query_one(RadioSet).pressed_button
        self.dismiss(escolhido.name if escolhido else None)

    @on(Button.Pressed, "#cancelar-badge")
    def cancelar(self) -> None:
        self.dismiss(None)


class PainelPerfil(VerticalScroll):
    DEFAULT_CSS = """
    PainelPerfil { padding: 1 2; }
    PainelPerfil #perfil-colunas { height: auto; }
    PainelPerfil .coluna { width: 1fr; height: auto; }
    PainelPerfil .painel { height: auto; border: round $primary; padding: 1 2; margin: 0 1 1 0; }
    PainelPerfil .titulo-secao { text-style: bold; color: $primary; margin-bottom: 1; }
    PainelPerfil .rotulo-missao { text-style: bold; color: $warning; margin-top: 1; }
    PainelPerfil .barra { color: $success; }
    PainelPerfil .linha-botoes { height: auto; margin-top: 1; }
    PainelPerfil .linha-badge { height: auto; }
    PainelPerfil .linha-badge Label { width: 1fr; }
    PainelPerfil #grade-badges { grid-size: 2; grid-gutter: 1; height: auto; }
    PainelPerfil .tile { width: 1fr; height: auto; border: round $primary; padding: 0 1; }
    PainelPerfil .tile-bloqueada { border: dashed #808080; color: $text-muted; }
    PainelPerfil .tile-ativa { border: round $warning; }
    """

    class PerfilAtualizado(Message):
        def __init__(self, usuario) -> None:
            super().__init__()
            self.usuario = usuario

    def __init__(self, usuario, **kwargs):
        super().__init__(**kwargs)
        self.usuario = usuario

    def compose(self) -> ComposeResult:
        d = resumo_do_usuario(self.usuario)
        g = d["gamificacao"]
        icone = g["badge_ativa"]["icone"] if g["badge_ativa"] else ""

        with Horizontal(id="perfil-colunas"):
            with Vertical(classes="coluna"):
                with Vertical(classes="painel"):
                    yield Label("Meus dados", classes="titulo-secao")
                    yield Label(f"Nome: {d['nome_completo']}", markup=False)
                    yield Label(f"Username: {d['username']}", markup=False)
                    yield Label(f"E-mail: {d['email']}", markup=False)
                    yield Label(f"Tipo de conta: {d['tipo']}", markup=False)
                    yield Label("Minha atividade", classes="titulo-secao")
                    yield Label(self._texto_atividade(d), markup=False)
                    yield Label(self._texto_topicos(d), markup=False)
                    with Vertical(classes="linha-botoes"):
                        yield Button("Editar dados", id="btn_editar_perfil")
                        yield Button("Sair da conta", id="btn_sair")
                        yield Button(
                            "Excluir minha conta",
                            variant="error",
                            id="btn_excluir_conta",
                        )

                with Vertical(classes="painel"):
                    yield Label("Como os outros veem você", classes="titulo-secao")
                    yield Label(
                        f"{d['username']} {icone}  |  Título do seu tópico".strip(),
                        markup=False,
                    )
                    yield Label(
                        f"{d['username']} {icone}  Seu comentário".strip(), markup=False
                    )
                    yield Label("A badge em uso aparece ao lado do seu username.")

            with Vertical(classes="coluna"):
                with Vertical(classes="painel"):
                    yield Label("Badge em uso", classes="titulo-secao")
                    with Horizontal(classes="linha-badge"):
                        yield Label(
                            self._texto_badge_ativa(g["badge_ativa"]), markup=False
                        )
                        yield Button(
                            "Escolher badge", variant="primary", id="btn_escolher_badge"
                        )

                with Vertical(classes="painel"):
                    yield Label("Missões", classes="titulo-secao")
                    dia = g["dia"]
                    marca = "  ✔ concluída" if dia["concluida"] else ""
                    yield Label("MISSÃO DO DIA" + marca, classes="rotulo-missao")
                    yield Label(dia["descricao"], markup=False)
                    yield Label(
                        montar_barra(dia["progresso"], dia["meta"]), classes="barra"
                    )

                    conquista = g["conquista"]
                    if conquista:
                        yield Label(
                            f"MISSÃO DE CONQUISTA  (recompensa: {conquista['badge']})",
                            classes="rotulo-missao",
                            markup=False,
                        )
                        yield Label(conquista["descricao"], markup=False)
                        yield Label(
                            montar_barra(conquista["progresso"], conquista["meta"]),
                            classes="barra",
                        )
                    else:
                        yield Label(
                            "Você completou todas as missões de conquista!",
                            classes="rotulo-missao",
                        )

                with Vertical(classes="painel"):
                    total = len(g["badges"])
                    ganhas = sum(1 for b in g["badges"] if b["conquistada"])
                    yield Label(f"Conquistas  {ganhas}/{total}", classes="titulo-secao")
                    with Grid(id="grade-badges"):
                        for badge in g["badges"]:
                            classes = "tile"
                            if not badge["conquistada"]:
                                classes += " tile-bloqueada"
                            elif badge["ativa"]:
                                classes += " tile-ativa"
                            yield Label(
                                self._texto_tile(badge), classes=classes, markup=False
                            )

    @staticmethod
    def _texto_atividade(d) -> str:
        return f"Tópicos criados: {d['total_topicos']}\nComentários feitos: {d['total_respostas']}"

    @staticmethod
    def _texto_topicos(d) -> str:
        if not d["topicos"]:
            return "Você ainda não criou nenhum tópico."
        linhas = [f"• {titulo}  (👁 {views})" for _, titulo, views in d["topicos"]]
        return "Meus tópicos:\n" + "\n".join(linhas)

    @staticmethod
    def _texto_badge_ativa(badge) -> str:
        if not badge:
            return "Nenhuma badge em uso.\nCumpra missões para conquistar badges!"
        return f"{badge['icone']} {badge['nome']}\n{badge['descricao']}"

    @staticmethod
    def _texto_tile(badge) -> str:
        if not badge["conquistada"]:
            return f"🔒 {badge['nome']}\n{badge['descricao']}"
        marca = "  ★ em uso" if badge["ativa"] else ""
        return f"{badge['icone']} {badge['nome']}{marca}\n{badge['descricao']}"

    def atualizar(self) -> None:
        self.refresh(recompose=True)

    @on(Button.Pressed, "#btn_editar_perfil")
    def editar_dados(self) -> None:
        self.app.push_screen(EditarPerfilModal(self.usuario), self.ao_fechar_edicao)

    def ao_fechar_edicao(self, novo_usuario) -> None:
        if novo_usuario is None:
            return
        self.usuario = novo_usuario
        self.post_message(self.PerfilAtualizado(novo_usuario))
        self.atualizar()
        self.notify("Dados atualizados!")

    @on(Button.Pressed, "#btn_escolher_badge")
    def abrir_seletor_badge(self) -> None:
        g = resumo_gamificacao(self.usuario)
        conquistadas = [b for b in g["badges"] if b["conquistada"]]
        if not conquistadas:
            self.notify("Você ainda não conquistou nenhuma badge.", severity="warning")
            return
        ativa_id = g["badge_ativa"]["id"] if g["badge_ativa"] else None
        self.app.push_screen(
            SeletorBadgeModal(conquistadas, ativa_id), self.ao_escolher_badge
        )

    def ao_escolher_badge(self, badge_id: str | None) -> None:
        if badge_id is None:
            return
        erro = escolher_badge(self.usuario, badge_id)
        if erro:
            self.notify(erro, severity="error")
            return
        self.notify("Badge atualizada!")
        self.atualizar()
