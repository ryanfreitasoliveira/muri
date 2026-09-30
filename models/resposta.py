# models/resposta.py
from dataclasses import dataclass, field
from datetime import datetime
from models.usuario import Usuario

@dataclass
class Resposta:
    autor: Usuario
    conteudo: str
    anexos: list = field(default_factory=list)
    data_criacao: datetime = field(default_factory=datetime.now)