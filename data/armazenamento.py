import sqlite3
from pathlib import Path
from datetime import datetime
from models.topico import Topico
from models.usuario import Cadastro
from models.resposta import Resposta

BASE_DIR = Path(__file__).resolve().parent.parent
CAMINHO_BANCO = BASE_DIR / "dados" / "muri.db"

def criar_tabelas():
    CAMINHO_BANCO.parent.mkdir(parents=True, exist_ok=True)
    conexao = sqlite3.connect(CAMINHO_BANCO)
    conexao.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            email TEXT PRIMARY KEY,
            nome TEXT,
            sobrenome TEXT,
            username TEXT,
            tipo TEXT,
            senha TEXT
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
    conexao.execute("""
        CREATE TABLE IF NOT EXISTS respostas (
            id TEXT PRIMARY KEY,
            topico_id TEXT NOT NULL REFERENCES topicos(id),
            autor_email TEXT REFERENCES usuarios(email),
            conteudo TEXT NOT NULL,
            data_criacao TEXT
        )
    """)
    conexao.commit()
    conexao.close()

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

def inserir_resposta(nova_resposta):
    conexao = sqlite3.connect(CAMINHO_BANCO)
    conexao.execute(
        """
        INSERT INTO respostas (id, topico_id, autor_email, conteudo, data_criacao)
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            str(nova_resposta.id),
            str(nova_resposta.topico_id),
            nova_resposta.autor.email,
            nova_resposta.conteudo,
            nova_resposta.data_criacao.isoformat(),
        ),
    )
    conexao.commit()
    conexao.close()

def inserir_usuario(novo_usuario):
    conexao = sqlite3.connect(CAMINHO_BANCO)
    try:
        conexao.execute(
            """
            INSERT INTO usuarios (email, nome, sobrenome, username, tipo, senha)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                novo_usuario.email,
                novo_usuario.nome,
                novo_usuario.sobrenome,
                novo_usuario.username,
                novo_usuario.tipo,
                novo_usuario.senha,
            ),
        )
        conexao.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conexao.close()

def listar_respostas(id_topico):
    conexao = sqlite3.connect(CAMINHO_BANCO)
    linhas = conexao.execute(
        "SELECT * FROM respostas WHERE topico_id = ? ORDER BY data_criacao ASC",
        (str(id_topico),),
    ).fetchall()
    conexao.close()
    return [_linha_para_resposta(linha) for linha in linhas]

def _linha_para_resposta(linha):
    id_, topico_id, autor_email, conteudo, data_criacao = linha
    return Resposta(
        id=id_,
        topico_id=topico_id,
        autor=buscar_usuario(autor_email),
        conteudo=conteudo,
        data_criacao=datetime.fromisoformat(data_criacao),
    )

def listar_topicos():
    conexao = sqlite3.connect(CAMINHO_BANCO)
    linhas = conexao.execute("""
        SELECT t.* FROM topicos t
        ORDER BY COALESCE(
            (SELECT MAX(r.data_criacao) FROM respostas r WHERE r.topico_id = t.id),
            t.data_criacao
        ) DESC
    """).fetchall()
    conexao.close()
    return [_linha_para_topico(linha) for linha in linhas]

_COLUNAS_USUARIO = "email, nome, sobrenome, username, tipo, senha"

def _linha_para_usuario(linha):
    email_, nome, sobrenome, username, tipo, senha = linha
    return Cadastro(
        email=email_, nome=nome, sobrenome=sobrenome, username=username,
        tipo=tipo, senha=senha, email_e_ufrpe=(tipo == "universitario"),
    )

def buscar_usuario(email):
    conexao = sqlite3.connect(CAMINHO_BANCO)
    linha = conexao.execute(
        f"SELECT {_COLUNAS_USUARIO} FROM usuarios WHERE email = ?", (email,)
    ).fetchone()
    conexao.close()
    return _linha_para_usuario(linha) if linha else None

def buscar_usuario_por_username(username):
    conexao = sqlite3.connect(CAMINHO_BANCO)
    linha = conexao.execute(
        f"SELECT {_COLUNAS_USUARIO} FROM usuarios WHERE lower(username) = lower(?)",
        (username,),
    ).fetchone()
    conexao.close()
    return _linha_para_usuario(linha) if linha else None

def contar_respostas_do_usuario(email):
    conexao = sqlite3.connect(CAMINHO_BANCO)
    total = conexao.execute(
        "SELECT COUNT(*) FROM respostas WHERE autor_email = ?", (email,)
    ).fetchone()[0]
    conexao.close()
    return total

def _linha_para_topico(linha):
    id_, titulo, autor_email, tags, mensagem, anexos, data_criacao, visualizacoes = linha
    return Topico(
        id=id_,
        titulo=titulo,
        autor=buscar_usuario(autor_email),
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

def deletar_usuario(email):
    conexao = sqlite3.connect(CAMINHO_BANCO)
    try:
        conexao.execute("BEGIN")
        conexao.execute("DELETE FROM respostas WHERE autor_email = ?", (email,))
        conexao.execute(
            "DELETE FROM respostas WHERE topico_id IN "
            "(SELECT id FROM topicos WHERE autor_email = ?)", (email,)
        )
        conexao.execute("DELETE FROM topicos WHERE autor_email = ?", (email,))
        cursor = conexao.execute("DELETE FROM usuarios WHERE email = ?", (email,))
        conexao.commit()
        return cursor.rowcount > 0
    except Exception:
        conexao.rollback()
        raise
    finally:
        conexao.close()
