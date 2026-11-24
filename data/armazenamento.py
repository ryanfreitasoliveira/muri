import sqlite3
from pathlib import Path
from datetime import date, datetime
from models.topico import Topico
from models.usuario import Cadastro
from models.resposta import Resposta
from models.tarefa import Tarefa

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
    conexao.execute("""
        CREATE TABLE IF NOT EXISTS tarefas (
            id TEXT PRIMARY KEY,
            usuario_email TEXT NOT NULL REFERENCES usuarios(email),
            dia TEXT NOT NULL,
            texto TEXT NOT NULL,
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
        for tabela in ("badges_usuarios", "badge_ativa", "missao_diaria"):
            conexao.execute(f"DELETE FROM {tabela} WHERE email = ?", (email,))
        conexao.execute("DELETE FROM tarefas WHERE usuario_email = ?", (email,))
        cursor = conexao.execute("DELETE FROM usuarios WHERE email = ?", (email,))
        conexao.commit()
        return cursor.rowcount > 0
    except Exception:
        conexao.rollback()
        raise
    finally:
        conexao.close()


def atualizar_usuario(email_antigo, usuario):
    """Atualiza o usuário e propaga o novo e-mail para tópicos e respostas."""
    conexao = sqlite3.connect(CAMINHO_BANCO)
    try:
        cursor = conexao.execute(
            """
            UPDATE usuarios
            SET email = ?, nome = ?, sobrenome = ?, username = ?, tipo = ?, senha = ?
            WHERE email = ?
            """,
            (
                usuario.email,
                usuario.nome,
                usuario.sobrenome,
                usuario.username,
                usuario.tipo,
                usuario.senha,
                email_antigo,
            ),
        )
        if cursor.rowcount == 0:
            conexao.rollback()
            return False
        if usuario.email != email_antigo:
            conexao.execute(
                "UPDATE topicos SET autor_email = ? WHERE autor_email = ?",
                (usuario.email, email_antigo),
            )
            conexao.execute(
                "UPDATE respostas SET autor_email = ? WHERE autor_email = ?",
                (usuario.email, email_antigo),
            )
            for tabela in ("badges_usuarios", "badge_ativa", "missao_diaria"):
                conexao.execute(
                    f"UPDATE {tabela} SET email = ? WHERE email = ?",
                    (usuario.email, email_antigo),
                )
            conexao.execute(
                "UPDATE tarefas SET usuario_email = ? WHERE usuario_email = ?",
                (usuario.email, email_antigo),
            )
        conexao.commit()
        return True
    except sqlite3.IntegrityError:
        conexao.rollback()
        return False
    finally:
        conexao.close()


def deletar_topico(id_topico):
    conexao = sqlite3.connect(CAMINHO_BANCO)
    try:
        conexao.execute("DELETE FROM respostas WHERE topico_id = ?", (str(id_topico),))
        cursor = conexao.execute("DELETE FROM topicos WHERE id = ?", (str(id_topico),))
        conexao.commit()
        return cursor.rowcount > 0
    except Exception:
        conexao.rollback()
        raise
    finally:
        conexao.close()


def buscar_resposta(id_resposta):
    conexao = sqlite3.connect(CAMINHO_BANCO)
    linha = conexao.execute(
        "SELECT * FROM respostas WHERE id = ?", (str(id_resposta),)
    ).fetchone()
    conexao.close()
    return _linha_para_resposta(linha) if linha else None


def deletar_resposta(id_resposta):
    conexao = sqlite3.connect(CAMINHO_BANCO)
    cursor = conexao.execute("DELETE FROM respostas WHERE id = ?", (str(id_resposta),))
    conexao.commit()
    conexao.close()
    return cursor.rowcount > 0


def listar_respostas_do_usuario(email):
    """Retorna (id_resposta, titulo_do_topico, conteudo), da mais recente para a mais antiga."""
    conexao = sqlite3.connect(CAMINHO_BANCO)
    linhas = conexao.execute(
        """
        SELECT r.id, t.titulo, r.conteudo
        FROM respostas r JOIN topicos t ON t.id = r.topico_id
        WHERE r.autor_email = ?
        ORDER BY r.data_criacao DESC
        """,
        (email,),
    ).fetchall()
    conexao.close()
    return linhas

# ---------- Agenda (tarefas por dia) ----------


def inserir_tarefa(tarefa: Tarefa):
    conexao = sqlite3.connect(CAMINHO_BANCO)
    try:
        conexao.execute(
            "INSERT INTO tarefas (id, usuario_email, dia, texto, data_criacao) VALUES (?, ?, ?, ?, ?)",
            (
                str(tarefa.id),
                tarefa.usuario_email,
                tarefa.dia.isoformat(),
                tarefa.texto,
                datetime.now().isoformat(),
            ),
        )
        conexao.commit()
    finally:
        conexao.close()


def listar_tarefas_do_dia(email, dia: date):
    conexao = sqlite3.connect(CAMINHO_BANCO)
    try:
        linhas = conexao.execute(
            "SELECT id, usuario_email, dia, texto FROM tarefas "
            "WHERE usuario_email = ? AND dia = ? ORDER BY data_criacao ASC",
            (email, dia.isoformat()),
        ).fetchall()
    finally:
        conexao.close()
    return [
        Tarefa(id=id_, usuario_email=u, dia=date.fromisoformat(d), texto=t)
        for id_, u, d, t in linhas
    ]


def deletar_tarefa(id_tarefa, email):
    """Só apaga se a tarefa pertencer ao usuário informado."""
    conexao = sqlite3.connect(CAMINHO_BANCO)
    try:
        cursor = conexao.execute(
            "DELETE FROM tarefas WHERE id = ? AND usuario_email = ?",
            (str(id_tarefa), email),
        )
        conexao.commit()
        return cursor.rowcount > 0
    finally:
        conexao.close()


def listar_tarefas_do_usuario(email):
    """Todas as tarefas do usuário (todos os dias), em ordem de dia e criação."""
    conexao = sqlite3.connect(CAMINHO_BANCO)
    try:
        linhas = conexao.execute(
            "SELECT id, usuario_email, dia, texto FROM tarefas "
            "WHERE usuario_email = ? ORDER BY dia ASC, data_criacao ASC",
            (email,),
        ).fetchall()
    finally:
        conexao.close()
    return [
        Tarefa(id=id_, usuario_email=u, dia=date.fromisoformat(d), texto=t)
        for id_, u, d, t in linhas
    ]
