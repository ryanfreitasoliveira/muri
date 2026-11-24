from pathlib import Path
import uuid

def gerar_nome_unico(caminho_original: str) -> str:
    extensao = Path(caminho_original).suffix
    return f"{uuid.uuid4()}{extensao}"