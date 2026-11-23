import json
import unicodedata
import webbrowser
from datetime import datetime, time
from functools import lru_cache
from pathlib import Path

from utils.formatacao import formatar_horario

BASE_DIR = Path(__file__).resolve().parent.parent
CAMINHO_LOCAIS = BASE_DIR / "data" / "locais.json"


# ---------- leitura dos dados ----------


@lru_cache(maxsize=1)
def _ler_arquivo() -> dict:
    """Lê o JSON uma única vez; as chamadas seguintes reaproveitam o resultado."""
    with open(CAMINHO_LOCAIS, encoding="utf-8") as arquivo:
        return json.load(arquivo)


def carregar_locais() -> list[dict]:
    return _ler_arquivo()["locais"]


def carregar_categorias() -> dict:
    return _ler_arquivo()["categorias"]


FILTRO_QUALQUER = "qualquer"


def carregar_recursos_acessibilidade() -> dict:
    return _ler_arquivo().get("recursos_acessibilidade", {})


# ---------- aberto ou fechado ----------


def esta_aberto(local: dict, agora: datetime | None = None) -> bool | None:
    """True/False conforme o horário; None se o local não tem horário cadastrado.
    O parâmetro 'agora' existe para poder testar com uma data/hora qualquer."""
    if not local.get("abre") or not local.get("fecha"):
        return None
    agora = agora or datetime.now()
    if agora.weekday() not in local["dias_semana"]:
        return False
    abre = time.fromisoformat(local["abre"])
    fecha = time.fromisoformat(local["fecha"])
    return abre <= agora.time() < fecha


# ---------- busca ----------


def normalizar(texto: str) -> str:
    """Minúsculas e sem acento: 'Salão' -> 'salao'."""
    decomposto = unicodedata.normalize("NFD", texto)
    sem_acento = "".join(c for c in decomposto if unicodedata.category(c) != "Mn")
    return sem_acento.casefold().strip()


def ponto_corresponde(ponto: dict, busca: str) -> bool:
    """O ponto-chave bate com a busca pelo nome, pela categoria ou por um sinônimo (ex.: 'wc')."""
    busca = normalizar(busca)
    if not busca:
        return False
    sinonimos = carregar_categorias().get(ponto["categoria"], {}).get("sinonimos", [])
    termos = [ponto["nome"], ponto["categoria"], *sinonimos]
    return any(busca in normalizar(termo) for termo in termos)


def filtrar_locais(busca: str, acessibilidade: str = "todos") -> list[dict]:
    busca = normalizar(busca)
    locais = carregar_locais()

    if acessibilidade == "elevador":
        locais = [l for l in locais if l.get("elevador")]
    elif acessibilidade == "vagas":
        locais = [l for l in locais if l.get("vagas_exclusivas")]

    if not busca:
        return locais
    return [
        l
        for l in locais
        if busca in normalizar(l["nome"])
        or any(ponto_corresponde(p, busca) for p in l["pontos_chave"])
    ]


# ---------- acessibilidade ----------


def _recursos_do_local(local: dict) -> list[dict]:
    catalogo = carregar_recursos_acessibilidade()
    return [
        item
        for item in local.get("acessibilidade", [])
        if item.get("recurso") in catalogo
    ]


def local_acessivel(local: dict) -> bool:
    return bool(_recursos_do_local(local))


def possui_recurso(local: dict, recurso: str = "") -> bool:
    if not recurso:
        return True
    itens = _recursos_do_local(local)
    if recurso == FILTRO_QUALQUER:
        return bool(itens)
    return any(item["recurso"] == recurso for item in itens)


def listar_acessibilidade(local: dict, recurso: str = "") -> list[dict]:
    """Cada item devolvido tem: texto, destaque (é o recurso filtrado) e indisponivel."""
    catalogo = carregar_recursos_acessibilidade()
    resultado = []
    for item in _recursos_do_local(local):
        texto = catalogo[item["recurso"]]["nome"]
        if item.get("onde"):
            texto += f": {item['onde']}"
        indisponivel = bool(item.get("indisponivel"))
        if indisponivel:
            texto += " · Indisponível no momento"
        resultado.append(
            {
                "texto": texto,
                "destaque": item["recurso"] == recurso,
                "indisponivel": indisponivel,
            }
        )
    return resultado


def opcoes_filtro_acessibilidade() -> list[tuple[str, str]]:
    opcoes = [("Todos os locais", ""), ("Somente locais acessíveis", FILTRO_QUALQUER)]
    for chave, info in carregar_recursos_acessibilidade().items():
        opcoes.append((f"Com {info['nome'].lower()}", chave))
    return opcoes


# ---------- pontos-chave para exibir ----------


def agrupar_pontos(pontos: list[dict], busca: str = "") -> list[dict]:
    """Junta pontos de mesmo nome (ex.: 4 banheiros viram uma linha só).
    Cada item devolvido tem: nome, texto, link (None se não houver) e destaque (bateu com a busca).
    """
    grupos: dict[str, list[dict]] = {}
    for ponto in pontos:
        grupos.setdefault(ponto["nome"], []).append(ponto)

    resultado = []
    for nome, itens in grupos.items():
        destaque = bool(busca) and any(ponto_corresponde(p, busca) for p in itens)
        if len(itens) > 1:
            andares = " · ".join(p["andar"] or "—" for p in itens)
            texto = f"{nome} ({len(itens)}): {andares}"
            link = None
        else:
            p = itens[0]
            texto = nome
            if p["andar"]:
                texto += f": {p['andar']}"
            if p.get("abre") and p.get("fecha"):
                texto += f" · {formatar_horario(p['abre'], p['fecha'])}"
            link = p.get("link_maps")
        resultado.append(
            {"nome": nome, "texto": texto, "link": link, "destaque": destaque}
        )
    return resultado


# ---------- abrir o Google Maps ----------


def abrir_no_navegador(link: str | None) -> bool:
    """Abre o link no navegador padrão. Devolve False se não deu certo."""
    if not link:
        return False
    try:
        return webbrowser.open(link)
    except Exception:
        return False
