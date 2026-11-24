# features/agenda.py — regras de negócio da agenda (tarefas por dia)
import unicodedata
from datetime import date, datetime, timedelta

from data.armazenamento import (
    deletar_tarefa, inserir_tarefa, listar_tarefas_do_dia, listar_tarefas_do_usuario,
)
from models.tarefa import Tarefa

LIMITE_TEXTO_TAREFA = 200
FORMATO_DATA = "%d/%m/%Y"


def formatar_dia(dia: date) -> str:
    return dia.strftime(FORMATO_DATA)


def interpretar_dia(texto: str):
    """Converte 'dd/mm/aaaa' em date. Retorna (date, None) ou (None, erro)."""
    try:
        return datetime.strptime(texto.strip(), FORMATO_DATA).date(), None
    except ValueError:
        return None, "Data inválida. Use dd/mm/aaaa (ex.: 25/12/2026)."


def deslocar_dia(dia: date, dias: int) -> date:
    try:
        return dia + timedelta(days=dias)
    except OverflowError:
        return dia


def validar_texto_tarefa(texto: str):
    if not texto.strip():
        return "Digite a tarefa."
    if len(texto.strip()) > LIMITE_TEXTO_TAREFA:
        return f"A tarefa pode ter no máximo {LIMITE_TEXTO_TAREFA} caracteres."
    return None


def adicionar_tarefa(usuario, dia: date, texto: str):
    if usuario is None:
        return None, "É preciso estar logado para usar a agenda."
    erro = validar_texto_tarefa(texto)
    if erro:
        return None, erro
    tarefa = Tarefa(usuario_email=usuario.email, dia=dia, texto=texto.strip())
    inserir_tarefa(tarefa)
    return tarefa, None


def tarefas_do_dia(usuario, dia: date):
    return listar_tarefas_do_dia(usuario.email, dia)


def remover_tarefa(usuario, id_tarefa):
    return deletar_tarefa(id_tarefa, usuario.email)


def _normalizar(texto: str) -> str:
    """Minúsculas e sem acentos, para a busca ignorar 'Prova' x 'prova' x 'próva'."""
    sem_acento = unicodedata.normalize("NFD", texto)
    return "".join(c for c in sem_acento if unicodedata.category(c) != "Mn").casefold()


def buscar_tarefas(usuario, termo: str):
    """Procura o termo no texto das tarefas do usuário, em todos os dias."""
    termo = _normalizar(termo.strip())
    if not termo:
        return []
    return [
        t for t in listar_tarefas_do_usuario(usuario.email)
        if termo in _normalizar(t.texto) or termo in formatar_dia(t.dia)
    ]
