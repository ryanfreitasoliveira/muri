from textual import on
from textual.containers import Horizontal
from textual.widgets import Button, Collapsible, Label, Markdown

from features.mapa import abrir_no_navegador, agrupar_pontos, esta_aberto
from utils.formatacao import formatar_dias, formatar_horario


class BotaoLink(Button):
    """Botão que guarda o link (e o nome do alvo) que ele aplica no label do ItemLocal.
    Mesmo padrão do BotaoResponder, do fórum."""

    def __init__(self, texto: str, link: str, alvo: str, **kwargs):
        super().__init__(texto, **kwargs)
        self.link = link
        self.alvo = alvo


def titulo_local(local: dict) -> str:
    aberto = esta_aberto(local)
    if aberto is None:
        return local["nome"]
    status = "🟢 Aberto agora" if aberto else "🔴 Fechado agora"
    return f"{local['nome']}  ·  {status}"


def markdown_local(local: dict) -> str:
    linhas = [
        f"**Endereço:** {local['endereco']}",
        f"**Funcionamento:** {formatar_dias(local['dias_semana'])}, "
        f"{formatar_horario(local['abre'], local['fecha'])}",
    ]
    andares = local.get("andares_alem_do_terreo")
    if andares is not None:
        linhas.append(f"**Andares:** térreo + {andares}")
    return "\n\n".join(linhas)


def texto_link(alvo: str, link: str) -> str:
    return f"Link ({alvo}): {link}"


class ItemLocal(Collapsible):
    """Colapsável de um local. Título = nome + aberto/fechado agora."""

    DEFAULT_CSS = """
    ItemLocal Horizontal { height: auto; align: left middle; }
    ItemLocal .nome-local { width: auto; text-style: bold; }
    ItemLocal .texto-ponto { width: 1fr; }
    ItemLocal .destacado { color: $warning; text-style: bold; }
    ItemLocal .rotulo-pontos { margin-top: 1; text-style: bold; }
    ItemLocal .btn-link { min-width: 8; height: 1; border: none; }
    ItemLocal .link-local { width: 1fr; margin-top: 1; color: $text-muted; }
    ItemLocal .btn-abrir { margin-top: 1; }
    """

    def __init__(self, local: dict, busca: str = "", expandido: bool = False):
        # 1) monta os filhos (como o TopicoItem faz no fórum)
        linha_nome = Horizontal(
            Label(local["nome"], markup=False, classes="nome-local"),
            BotaoLink("prédio", local["link_maps"], local["nome"], classes="btn-link"),
        )
        filhos = [linha_nome, Markdown(markdown_local(local))]

        grupos = agrupar_pontos(local["pontos_chave"], busca)
        if grupos:
            filhos.append(Label("Pontos-chave:", classes="rotulo-pontos"))
            for grupo in grupos:
                classes = (
                    "texto-ponto destacado" if grupo["destaque"] else "texto-ponto"
                )
                linha = [Label(f"• {grupo['texto']}", markup=False, classes=classes)]
                if grupo["link"]:
                    linha.append(
                        BotaoLink(
                            "mapa", grupo["link"], grupo["nome"], classes="btn-link"
                        )
                    )
                filhos.append(Horizontal(*linha))

        label_link = Label(
            texto_link(local["nome"], local["link_maps"]),
            markup=False,
            classes="link-local",
        )
        filhos.append(label_link)
        filhos.append(
            Button("Abrir no navegador", variant="primary", classes="btn-abrir")
        )

        # 2) cria o colapsável
        super().__init__(*filhos, title=titulo_local(local), collapsed=not expandido)

        # 3) guarda o estado (depois do super().__init__, como no fórum)
        self.local = local
        self.link_atual = local["link_maps"]
        self.label_link = label_link

    def atualizar_status(self) -> None:
        """Recalcula 'aberto/fechado agora' e atualiza o título."""
        self.title = titulo_local(self.local)

    @on(Button.Pressed, ".btn-link")
    def escolher_link(self, event: Button.Pressed) -> None:
        event.stop()
        botao = event.button
        self.link_atual = botao.link
        self.label_link.update(texto_link(botao.alvo, botao.link))

    @on(Button.Pressed, ".btn-abrir")
    def abrir_link(self, event: Button.Pressed) -> None:
        event.stop()
        if not abrir_no_navegador(self.link_atual):
            self.notify("Não foi possível abrir o navegador.", severity="error")
