# models/resposta.py
from dataclasses import dataclass, field
from datetime import datetime
from models.usuario import Cadastro
import uuid

@dataclass
class Resposta:
    topico_id: str
    autor: Cadastro
    conteudo: str
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    data_criacao: datetime = field(default_factory=datetime.now)
