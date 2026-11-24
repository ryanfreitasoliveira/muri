from textual import on
from textual.app import ComposeResult
from textual.containers import Vertical, VerticalScroll
from textual.widgets import Input, Label, Select

from features.mapa import filtrar_locais, opcoes_filtro_acessibilidade
from interface.item_local import ItemLocal

INTERVALO_STATUS = 60


class PainelMapa(VerticalScroll):
    DEFAULT_CSS = """
    PainelMapa { padding: 1 2; }
    PainelMapa .titulo-secao { text-style: bold; color: $primary; margin-bottom: 1; }
    PainelMapa .rotulo-filtro { margin-top: 1; text-style: bold; }
    PainelMapa #lista-locais { height: auto; margin-top: 1; }
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.busca = ""
        self.recurso = ""

    def compose(self) -> ComposeResult:
        yield Label("Mapa do campus", classes="titulo-secao")
        yield Input(
            placeholder="Buscar local ou ponto-chave (ex.: banheiro, sebrae, dc)",
            id="busca-mapa",
        )
        yield Label("Acessibilidade", classes="rotulo-filtro")
        yield Select(
            opcoes_filtro_acessibilidade(),
            allow_blank=False,
            value="",
            id="filtro-acessibilidade",
        )
        yield Vertical(id="lista-locais")

    def on_mount(self) -> None:
        self.carregar_locais()
        self.set_interval(INTERVALO_STATUS, self.atualizar_status)

    @on(Input.Changed, "#busca-mapa")
    def ao_buscar(self, event: Input.Changed) -> None:
        self.busca = event.value
        self.carregar_locais()

    @on(Select.Changed, "#filtro-acessibilidade")
    def ao_filtrar_acessibilidade(self, event: Select.Changed) -> None:
        recurso = event.value if isinstance(event.value, str) else ""
        if recurso == self.recurso:
            return
        self.recurso = recurso
        self.carregar_locais()

    def carregar_locais(self) -> None:
        busca = self.busca.strip()
        lista = self.query_one("#lista-locais", Vertical)
        lista.remove_children()
        locais = filtrar_locais(busca, self.recurso)
        if not locais:
            lista.mount(Label("Nenhum local encontrado."))
            return
        expandido = bool(busca or self.recurso)
        for local in locais:
            lista.mount(
                ItemLocal(local, busca=busca, expandido=expandido, recurso=self.recurso)
            )

    def atualizar_status(self) -> None:
        for item in self.query(ItemLocal):
            item.atualizar_status()
