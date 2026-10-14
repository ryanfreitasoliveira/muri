# interface/perfil.py — conteúdo da aba "Meus dados"
from textual.app import ComposeResult
from textual.containers import VerticalScroll
from textual.widgets import Button, Label

from models.perfil import resumo_do_usuario


class PainelPerfil(VerticalScroll):
    DEFAULT_CSS = """
    PainelPerfil { padding: 1 2; }
    PainelPerfil .titulo-secao { text-style: bold; color: $primary; margin-bottom: 1; }
    PainelPerfil .campo { height: auto; }
    PainelPerfil #perfil-topicos { height: auto; margin-bottom: 1; }
    """

    def __init__(self, usuario, **kwargs):
        super().__init__(**kwargs)
        self.usuario = usuario

    def compose(self) -> ComposeResult:
        d = resumo_do_usuario(self.usuario)
        yield Label("Meus dados", classes="titulo-secao")
        yield Label(f"Nome: {d['nome_completo']}", classes="campo", markup=False)
        yield Label(f"Username: {d['username']}", classes="campo", markup=False)
        yield Label(f"E-mail: {d['email']}", classes="campo", markup=False)
        yield Label(f"Tipo de conta: {d['tipo']}", classes="campo", markup=False)
        yield Label("")
        yield Label("Minha atividade", classes="titulo-secao")
        yield Label(self._texto_atividade(d), id="perfil-atividade", classes="campo", markup=False)
        yield Label(self._texto_topicos(d), id="perfil-topicos", markup=False)
        yield Button("Sair da conta", id="btn_sair")
        yield Button("Excluir minha conta", variant="error", id="btn_excluir_conta")

    @staticmethod
    def _texto_atividade(d) -> str:
        return f"Tópicos criados: {d['total_topicos']}\nComentários feitos: {d['total_respostas']}"

    @staticmethod
    def _texto_topicos(d) -> str:
        if not d["topicos"]:
            return "Você ainda não criou nenhum tópico."
        linhas = [f"• {titulo}  (👁 {views})" for titulo, views in d["topicos"]]
        return "Meus tópicos:\n" + "\n".join(linhas)

    def atualizar(self) -> None:
        """Recarrega os números (chamado quando o usuário abre a aba)."""
        d = resumo_do_usuario(self.usuario)
        self.query_one("#perfil-atividade", Label).update(self._texto_atividade(d))
        self.query_one("#perfil-topicos", Label).update(self._texto_topicos(d))
