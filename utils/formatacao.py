# utils/formatacao.py
from datetime import datetime

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