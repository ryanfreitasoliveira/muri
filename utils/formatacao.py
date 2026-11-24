from datetime import datetime

NOMES_DIAS = ["segunda", "terça", "quarta", "quinta", "sexta", "sábado", "domingo"]


def formatar_data_relativa(data: datetime) -> str:
    """Vira 'há 2h', 'há 3d' — pro RF004 mostrar quando foi a última atividade do tópico."""
    diferenca = datetime.now() - data
    if diferenca.days > 0:
        return f"há {diferenca.days}d"
    horas = diferenca.seconds // 3600
    if horas > 0:
        return f"há {horas}h"
    return f"há {diferenca.seconds // 60}min"


def truncar_texto(texto: str, limite: int = 100) -> str:
    """Corta a mensagem do tópico pra caber no preview da listagem."""
    if len(texto) <= limite:
        return texto
    return texto[:limite].rstrip() + "..."


def formatar_hora(hhmm: str) -> str:
    """'08:00' -> '8h' | '21:50' -> '21h50'"""
    horas, minutos = hhmm.split(":")
    return f"{int(horas)}h" if minutos == "00" else f"{int(horas)}h{minutos}"


def formatar_horario(abre: str, fecha: str) -> str:
    """('08:00', '17:00') -> '8h às 17h'"""
    return f"{formatar_hora(abre)} às {formatar_hora(fecha)}"


def formatar_dias(dias: list[int]) -> str:
    """[0,1,2,3,4] -> 'segunda a sexta' (0 = segunda, como em datetime.weekday())"""
    if not dias:
        return ""
    if len(dias) > 2 and dias == list(range(dias[0], dias[-1] + 1)):
        return f"{NOMES_DIAS[dias[0]]} a {NOMES_DIAS[dias[-1]]}"
    return ", ".join(NOMES_DIAS[d] for d in dias)
