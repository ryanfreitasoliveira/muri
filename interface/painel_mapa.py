# interface/painel_mapa.py — conteúdo da aba "Mapa"
from textual import on
from textual.app import ComposeResult
from textual.containers import Vertical, VerticalScroll
from textual.widgets import Input, Label

from features.mapa import filtrar_locais
from interface.item_local import ItemLocal

INTERVALO_STATUS = 60  # segundos entre cada recálculo de "aberto/fechado agora"


class PainelMapa(VerticalScroll):
    DEFAULT_CSS = """
    PainelMapa { padding: 1 2; }
    PainelMapa .titulo-secao { text-style: bold; color: $primary; margin-bottom: 1; }
    PainelMapa #lista-locais { height: auto; }
    """

    def compose(self) -> ComposeResult:
        yield Label("Mapa do campus", classes="titulo-secao")
        yield Input(placeholder="Buscar local ou ponto-chave (ex.: banheiro, sebrae, dc)", id="busca-mapa")
        yield Vertical(id="lista-locais")

    def on_mount(self) -> None:
        self.carregar_locais("")
        # mantém o "aberto/fechado agora" em dia se o app ficar aberto
        self.set_interval(INTERVALO_STATUS, self.atualizar_status)

    @on(Input.Changed, "#busca-mapa")
    def ao_buscar(self, event: Input.Changed) -> None:
        self.carregar_locais(event.value)

    def carregar_locais(self, busca: str) -> None:
        """Refaz a lista de colapsáveis conforme a busca (mesmo padrão do carregar_topicos do fórum)."""
        busca = busca.strip()
        lista = self.query_one("#lista-locais", Vertical)
        lista.remove_children()
        locais = filtrar_locais(busca)
        if not locais:
            lista.mount(Label("Nenhum local encontrado."))
            return
        # com busca, os colapsáveis já abrem para mostrar o ponto que bateu
        for local in locais:
            lista.mount(ItemLocal(local, busca=busca, expandido=bool(busca)))

    def atualizar_status(self) -> None:
        for item in self.query(ItemLocal):
            item.atualizar_status()
