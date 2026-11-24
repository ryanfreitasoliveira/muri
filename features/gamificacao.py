# features/gamificacao.py — regras de badges e missões
import json
import random
from datetime import date

from data.armazenamento import BASE_DIR, listar_topicos
from data.gamificacao_db import (
    buscar_badge_ativa, buscar_missao_diaria, conceder_badge, concluir_missao_diaria,
    contar_comentarios_do_usuario, contar_topicos_do_usuario,
    contar_topicos_respondidos_distintos, definir_badge_ativa, listar_badges_do_usuario,
    maior_visualizacao_do_usuario, salvar_missao_diaria,
)

with open(BASE_DIR / "data" / "gamificacao.json", encoding="utf-8") as arquivo:
    _CATALOGO = json.load(arquivo)

BADGES = {badge["id"]: badge for badge in _CATALOGO["badges"]}
MISSOES = {missao["id"]: missao for missao in _CATALOGO["missoes"]}
CONQUISTAS = [m for m in _CATALOGO["missoes"] if m["tipo"] == "conquista"]
DIARIAS = [m for m in _CATALOGO["missoes"] if m["tipo"] == "dia"]


# ---------- métricas: "metrica" no JSON -> função que mede o usuário ----------

def _tags_distintas(usuario, desde):
    tags = set()
    for topico in listar_topicos():
        if topico.autor and topico.autor.email == usuario.email:
            tags.update(topico.tags)
    return len(tags)


METRICAS = {
    "topicos_criados": lambda usuario, desde: contar_topicos_do_usuario(usuario.email, desde),
    "comentarios_feitos": lambda usuario, desde: contar_comentarios_do_usuario(usuario.email, desde),
    "topicos_respondidos_distintos":
        lambda usuario, desde: contar_topicos_respondidos_distintos(usuario.email, desde),
    "maior_visualizacao": lambda usuario, desde: maior_visualizacao_do_usuario(usuario.email),
    "tags_distintas": _tags_distintas,
    "conta_universitaria": lambda usuario, desde: 1 if usuario.tipo == "universitario" else 0,
}


def calcular_progresso(usuario, missao, desde=None):
    """Quanto o usuário já fez da missão, limitado à meta (nunca passa de 100%)."""
    atual = METRICAS[missao["metrica"]](usuario, desde)
    return min(atual, missao["meta"])


def _badge_disponivel(badge, usuario):
    """Badges com 'requer_tipo' só existem para aquele tipo de conta."""
    exigido = badge.get("requer_tipo")
    return exigido is None or exigido == usuario.tipo


# ---------- missões de conquista (rendem badge) ----------

def missao_de_conquista_atual(usuario):
    """A primeira missão da lista cuja badge o usuário ainda não tem."""
    conquistadas = set(listar_badges_do_usuario(usuario.email))
    for missao in CONQUISTAS:
        if missao["badge"] in conquistadas:
            continue
        if _badge_disponivel(BADGES[missao["badge"]], usuario):
            return missao
    return None


def atualizar_conquistas(usuario):
    """Concede as badges das missões cumpridas. Devolve os avisos para mostrar."""
    avisos = []
    while True:
        missao = missao_de_conquista_atual(usuario)
        if missao is None or calcular_progresso(usuario, missao) < missao["meta"]:
            return avisos

        badge = BADGES[missao["badge"]]
        if conceder_badge(usuario.email, badge["id"]):
            avisos.append(f"Nova badge: {badge['icone']} {badge['nome']}")
            if buscar_badge_ativa(usuario.email) is None:
                definir_badge_ativa(usuario.email, badge["id"])  # primeira badge já fica em uso


# ---------- missão do dia ----------

def missao_do_dia(usuario):
    """Devolve (missao, data_da_missao, concluida). Sorteia outra quando o dia vira."""
    hoje = date.today().isoformat()
    atual = buscar_missao_diaria(usuario.email)

    if atual is not None and atual[1] == hoje and atual[0] in MISSOES:
        return MISSOES[atual[0]], atual[1], bool(atual[2])

    anterior = atual[0] if atual else None
    opcoes = [m for m in DIARIAS if m["id"] != anterior] or DIARIAS
    escolhida = random.choice(opcoes)
    salvar_missao_diaria(usuario.email, escolhida["id"], hoje)
    return escolhida, hoje, False


def verificar_missao_diaria(usuario):
    missao, data, concluida = missao_do_dia(usuario)
    if concluida:
        return []
    if calcular_progresso(usuario, missao, desde=data) >= missao["meta"]:
        concluir_missao_diaria(usuario.email)
        return [f"Missão do dia concluída: {missao['descricao']}"]
    return []


# ---------- API usada pela interface ----------

def verificar_gamificacao(usuario):
    """Chame depois de qualquer ação do usuário. Devolve lista de avisos (pode ser vazia)."""
    return atualizar_conquistas(usuario) + verificar_missao_diaria(usuario)


def escolher_badge(usuario, badge_id):
    """Devolve mensagem de erro, ou None se deu certo."""
    if badge_id not in listar_badges_do_usuario(usuario.email):
        return "Você ainda não conquistou essa badge."
    definir_badge_ativa(usuario.email, badge_id)
    return None


def icone_badge_ativa(email):
    """Ícone da badge em uso (ou '' se não houver) — exibido ao lado do username."""
    badge = BADGES.get(buscar_badge_ativa(email))
    return badge["icone"] if badge else ""


def resumo_gamificacao(usuario):
    conquistadas = set(listar_badges_do_usuario(usuario.email))
    ativa_id = buscar_badge_ativa(usuario.email)

    badges = [
        {**badge, "conquistada": badge["id"] in conquistadas, "ativa": badge["id"] == ativa_id}
        for badge in _CATALOGO["badges"]
        if badge["id"] in conquistadas or _badge_disponivel(badge, usuario)
    ]

    missao, data, concluida = missao_do_dia(usuario)
    dia = {
        "descricao": missao["descricao"],
        "meta": missao["meta"],
        "progresso": missao["meta"] if concluida else calcular_progresso(usuario, missao, desde=data),
        "concluida": concluida,
    }

    conquista = None
    proxima = missao_de_conquista_atual(usuario)
    if proxima:
        conquista = {
            "descricao": proxima["descricao"],
            "meta": proxima["meta"],
            "progresso": calcular_progresso(usuario, proxima),
            "badge": BADGES[proxima["badge"]]["nome"],
        }

    return {"badge_ativa": BADGES.get(ativa_id), "dia": dia, "conquista": conquista, "badges": badges}
