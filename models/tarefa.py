# models/tarefa.py — tarefa/evento da agenda de um usuário em um dia
from dataclasses import dataclass, field
from datetime import date
import uuid


@dataclass
class Tarefa:
    usuario_email: str
    dia: date
    texto: str
    id: uuid.UUID = field(default_factory=uuid.uuid4)
