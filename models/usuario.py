# models/usuario.py — versão provisória, só pra testar
from dataclasses import dataclass

@dataclass
class Cadastro:
    email: str
    nome: str
    sobrenome: str
    username: str
    tipo: str = "visitante"