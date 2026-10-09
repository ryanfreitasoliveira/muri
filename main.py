# main.py, na raiz
from interface.tela_forum import MURI
from data.armazenamento import criar_tabelas, inserir_usuario
from models.usuario import Cadastro

criar_tabelas()
inserir_usuario(
    Cadastro(
        email="teste@ufrpe.br",
        nome="Teste",
        sobrenome="Provisório",
        username="teste",
        tipo="universitario",
    )
)
if __name__ == "__main__":
    MURI().run()
