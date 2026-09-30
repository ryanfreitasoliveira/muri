import sqlite3
from pathlib import Path
from datetime import datetime
from models.topico import Topico
from models.usuario import Cadastro


CAMINHO_BANCO = Path("dados/muri.db")

"""ATENÇÃO: Todas as funções estão relacionadas diretamente com o banco de dados e por isso estão aqui.
As funções atualizar_visualizacoes e buscar_topico foram importadas para o caminho features/forum.py pois
tem relação direta com a classe Topico. Já outras funções como listar_topicos vai ser chamada a partir do main quando o programa iniciar
"""


def criar_tabelas():
    conexao = sqlite3.connect(CAMINHO_BANCO)
    conexao.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            email TEXT PRIMARY KEY,
            nome TEXT,
            sobrenome TEXT,
            username TEXT,
            tipo TEXT
        )
    """)
    conexao.execute("""
        CREATE TABLE IF NOT EXISTS topicos (
            id TEXT PRIMARY KEY,
            titulo TEXT NOT NULL,
            autor_email TEXT REFERENCES usuarios(email),
            tags TEXT,
            mensagem TEXT,
            anexos TEXT,
            data_criacao TEXT,
            visualizacoes INTEGER DEFAULT 0
        )
    """)
    conexao.commit()
    conexao.close()
    
#insere topico novo no banco de dados SQL
def inserir_topico(novo_topico):
    conexao = sqlite3.connect(CAMINHO_BANCO)
    conexao.execute(
        """
        INSERT INTO topicos (id, titulo, autor_email, tags, mensagem, anexos, data_criacao, visualizacoes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            str(novo_topico.id),
            novo_topico.titulo,
            novo_topico.autor.email,
            ",".join(novo_topico.tags),
            novo_topico.mensagem,
            ",".join(str(a) for a in novo_topico.anexos),
            novo_topico.data_criacao.isoformat(),
            novo_topico.visualizacoes,
        ),
    )
    conexao.commit()
    conexao.close()
#ATENÇÃO: classe Usuario não adcionado
"""def inserir_usuario(novo_usuario):
    conexao = sqlite3.connect(CAMINHO_BANCO)
    conexao.execute(
        
        #INSERT INTO topicos (email, nome, sobrenome, username, tipo)
        #VALUES (?, ?, ?, ?, ?)
        
        (
            str(novo_usuario.nome),
            novo_usuario.email,
            novo_topico.sobrenome,
            novo_topico.username,
        ),
    )
    conexao.commit()
    conexao.close()"""
    
#transforma as linhas salvas de volta em objetos do tipo 'Topico' e os armazena em uma lista
def listar_topicos():
    conexao = sqlite3.connect(CAMINHO_BANCO)
    linhas = conexao.execute("SELECT * FROM topicos").fetchall()
    conexao.close()
    return [_linha_para_topico(linha) for linha in linhas]

#transforma uma linha da tabela usuario de volta em objeto do tipo 'Cadastro' atraves da chave primaria 'email'
def buscar_usuario(email):
    conexao = sqlite3.connect(CAMINHO_BANCO)
    linha = conexao.execute(
        "SELECT * FROM usuarios WHERE email = ?", (email,)
    ).fetchone()
    conexao.close()
    if not linha:
        return None
    email_, nome, sobrenome, username, tipo = linha
    return Cadastro(email=email_, nome=nome, sobrenome=sobrenome, username=username, tipo=tipo)

#transforma uma linha da tabela topico de volta em objeto do tipo 'Topico'
def _linha_para_topico(linha):
    id_, titulo, autor_email, tags, mensagem, anexos, data_criacao, visualizacoes = linha
    return Topico(
        id=id_,
        titulo=titulo,
        autor=buscar_usuario(autor_email), #a função 'buscar_usuario' devolve o objeto usuario inteiro
        tags=tags.split(",") if tags else [],
        mensagem=mensagem,
        anexos=[Path(a) for a in anexos.split(",")] if anexos else [],
        data_criacao=datetime.fromisoformat(data_criacao),
        visualizacoes=visualizacoes,
    )
    

def atualizar_visualizacoes(id_topico, novo_valor):
    conexao = sqlite3.connect(CAMINHO_BANCO)
    conexao.execute(
        "UPDATE topicos SET visualizacoes = ? WHERE id = ?",
        (novo_valor, str(id_topico)),
    )
    conexao.commit()
    conexao.close()
    
    
def buscar_topico(id_topico):
    conexao = sqlite3.connect(CAMINHO_BANCO)
    linha = conexao.execute(
        "SELECT * FROM topicos WHERE id = ?", (str(id_topico),)
    ).fetchone()
    conexao.close()
    return _linha_para_topico(linha) if linha else None