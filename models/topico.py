from dataclasses import dataclass, field
from models.usuario import Cadastro
from datetime import datetime
from models.resposta import Resposta
import uuid

@dataclass
class Topico:
    id_: uuid.UUID = field(default_factory=uuid.uuid4)
    titulo: str
    autor: Cadastro
    tags: list = field(default_factory=list)
    mensagem: str = ""
    anexos: list = field(default_factory=list)
    visualizacoes: int = 0
    respostas: list = field(default_factory=list)
    data_criacao: datetime = field(default_factory=datetime.now)

    def incrementar_visualizacao(self):
        self.visualizacoes += 1

    def adicionar_resposta(self, nova_resposta):
        self.respostas.append(nova_resposta)

    def total_respostas(self):
        return len(self.respostas)