# interface/agenda.py — aba "Agenda": tarefas por dia, salvas no banco
from datetime import date

from textual import on
from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Button, Input, Label, ListItem, ListView

from features.agenda import (
    adicionar_tarefa, buscar_tarefas, deslocar_dia, formatar_dia, interpretar_dia,
    remover_tarefa, tarefas_do_dia,
)


class TarefaItem(ListItem):
    """Item da lista; guarda o id da tarefa no banco."""
    def __init__(self, tarefa, mostrar_dia: bool = False) -> None:
        super().__init__()
        self.tarefa = tarefa
        self.mostrar_dia = mostrar_dia

    def compose(self) -> ComposeResult:
        texto = self.tarefa.texto
        if self.mostrar_dia:  # nos resultados de busca, mostra de qual dia é a tarefa
            texto = f"{formatar_dia(self.tarefa.dia)} — {texto}"
        yield Label(texto, markup=False)


class AbaCalendario(Vertical):
    """Aba de agenda: o usuário escolhe um dia e gerencia as tarefas dele."""

    DEFAULT_CSS = """
    AbaCalendario #painel-calendario { padding: 1 2; height: 100%; }
    AbaCalendario #sidebar-cal { width: 40%; background: $panel; padding: 1 2; border-right: heavy $accent; }
    AbaCalendario #main-cal { padding: 1 2; width: 60%; }
    AbaCalendario .titulo { text-style: bold; color: $accent; margin-bottom: 1; }
    AbaCalendario #navegacao-dia { height: 3; margin-bottom: 1; }
    AbaCalendario #navegacao-dia Button { min-width: 6; margin-right: 1; }
    AbaCalendario #label-dia { text-style: bold; margin-bottom: 1; }
    AbaCalendario #input-tarefa-cal, AbaCalendario #input-ir-dia { margin-bottom: 1; }
    AbaCalendario #input-busca-tarefa { margin-bottom: 1; }
    AbaCalendario #msg-cal { color: $error; height: auto; margin-bottom: 1; }
    AbaCalendario #sidebar-cal Button.acao { width: 100%; margin-bottom: 1; }
    AbaCalendario #lista-tarefas-cal { height: 1fr; border: solid $primary; background: $boost; }
    """

    def __init__(self, usuario, **kwargs):
        super().__init__(**kwargs)
        self.usuario = usuario
        self.dia = date.today()
        self.termo_busca = ""

    def compose(self) -> ComposeResult:
        with Horizontal(id="painel-calendario"):
            with Vertical(id="sidebar-cal"):
                yield Label("Agenda", classes="titulo")
                with Horizontal(id="navegacao-dia"):
                    yield Button("◀", id="btn-dia-anterior")
                    yield Button("Hoje", id="btn-hoje")
                    yield Button("▶", id="btn-dia-seguinte")
                yield Label("Ir para o dia (dd/mm/aaaa):")
                yield Input(placeholder="ex.: 25/12/2026", id="input-ir-dia")
                yield Label("Nova tarefa neste dia:")
                yield Input(placeholder="Digite a tarefa...", id="input-tarefa-cal")
                yield Button("Adicionar tarefa", id="btn-adicionar-cal", variant="success", classes="acao")
                yield Button("Excluir selecionada", id="btn-remover-cal", variant="error", classes="acao")
                yield Label("", id="msg-cal", markup=False)

            with Vertical(id="main-cal"):
                yield Label("", id="label-dia", classes="titulo", markup=False)
                yield Input(placeholder="Buscar nas tarefas (texto ou dd/mm/aaaa)...", id="input-busca-tarefa")
                yield ListView(id="lista-tarefas-cal")

    def on_mount(self) -> None:
        self.mostrar_dia(self.dia)

    # ---------- navegação entre dias ----------

    def mostrar_dia(self, dia: date) -> None:
        self.dia = dia
        self.recarregar_tarefas()

    @on(Button.Pressed, "#btn-dia-anterior")
    def dia_anterior(self) -> None:
        self.mostrar_dia(deslocar_dia(self.dia, -1))

    @on(Button.Pressed, "#btn-dia-seguinte")
    def dia_seguinte(self) -> None:
        self.mostrar_dia(deslocar_dia(self.dia, 1))

    @on(Button.Pressed, "#btn-hoje")
    def ir_para_hoje(self) -> None:
        self.mostrar_dia(date.today())

    @on(Input.Submitted, "#input-ir-dia")
    def ir_para_dia(self, event: Input.Submitted) -> None:
        dia, erro = interpretar_dia(event.value)
        if erro:
            self.query_one("#msg-cal", Label).update(erro)
            return
        self.query_one("#msg-cal", Label).update("")
        event.input.value = ""
        self.mostrar_dia(dia)

    # ---------- tarefas (salvas no banco) ----------

    def recarregar_tarefas(self) -> None:
        """Mostra as tarefas do dia escolhido ou, havendo busca ativa, os resultados."""
        lista = self.query_one("#lista-tarefas-cal", ListView)
        titulo = self.query_one("#label-dia", Label)
        lista.clear()
        if self.termo_busca:
            achadas = buscar_tarefas(self.usuario, self.termo_busca)
            titulo.update(f"Busca por '{self.termo_busca}': {len(achadas)} resultado(s)")
            itens = [TarefaItem(t, mostrar_dia=True) for t in achadas]
        else:
            sufixo = " (hoje)" if self.dia == date.today() else ""
            titulo.update(f"Tarefas de {formatar_dia(self.dia)}{sufixo}")
            itens = [TarefaItem(t) for t in tarefas_do_dia(self.usuario, self.dia)]
        if itens:
            lista.extend(itens)

    @on(Input.Changed, "#input-busca-tarefa")
    def ao_buscar(self, event: Input.Changed) -> None:
        self.termo_busca = event.value.strip()
        self.recarregar_tarefas()

    @on(ListView.Selected, "#lista-tarefas-cal")
    def abrir_dia_do_resultado(self, event: ListView.Selected) -> None:
        """Enter num resultado da busca leva para o dia daquela tarefa."""
        item = event.item
        if self.termo_busca and isinstance(item, TarefaItem):
            self.termo_busca = ""
            self.query_one("#input-busca-tarefa", Input).value = ""
            self.mostrar_dia(item.tarefa.dia)

    @on(Input.Submitted, "#input-tarefa-cal")
    @on(Button.Pressed, "#btn-adicionar-cal")
    def adicionar(self) -> None:
        campo = self.query_one("#input-tarefa-cal", Input)
        msg = self.query_one("#msg-cal", Label)
        _, erro = adicionar_tarefa(self.usuario, self.dia, campo.value)
        if erro:
            msg.update(erro)
            return
        msg.update("")
        campo.value = ""
        campo.focus()
        self.recarregar_tarefas()

    @on(Button.Pressed, "#btn-remover-cal")
    def remover(self) -> None:
        lista = self.query_one("#lista-tarefas-cal", ListView)
        item = lista.highlighted_child
        if isinstance(item, TarefaItem):
            remover_tarefa(self.usuario, item.tarefa.id)
            self.recarregar_tarefas()
