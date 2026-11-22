# data/gamificacao_db.py — acesso ao banco para badges e missões
import sqlite3
from datetime import datetime

from data.armazenamento import CAMINHO_BANCO


def criar_tabelas_gamificacao():
    conexao = sqlite3.connect(CAMINHO_BANCO)
    conexao.execute("""
        CREATE TABLE IF NOT EXISTS badges_usuarios (
            email TEXT NOT NULL REFERENCES usuarios(email),
            badge_id TEXT NOT NULL,
            data_conquista TEXT,
            PRIMARY KEY (email, badge_id)
        )
    """)
    conexao.execute("""
        CREATE TABLE IF NOT EXISTS badge_ativa (
            email TEXT PRIMARY KEY REFERENCES usuarios(email),
            badge_id TEXT
        )
    """)
    conexao.execute("""
        CREATE TABLE IF NOT EXISTS missao_diaria (
            email TEXT PRIMARY KEY REFERENCES usuarios(email),
            missao_id TEXT NOT NULL,
            data TEXT NOT NULL,
            concluida INTEGER DEFAULT 0
        )
    """)
    conexao.commit()
    conexao.close()


# ---------- helpers: abrem e fecham a conexão para quem chama ----------

def _consultar(sql, parametros=()):
    conexao = sqlite3.connect(CAMINHO_BANCO)
    try:
        return conexao.execute(sql, parametros).fetchall()
    finally:
        conexao.close()


def _escrever(sql, parametros=()):
    conexao = sqlite3.connect(CAMINHO_BANCO)
    try:
        cursor = conexao.execute(sql, parametros)
        conexao.commit()
        return cursor.rowcount
    finally:
        conexao.close()


# ---------- métricas (base das missões) ----------

def contar_topicos_do_usuario(email, desde=None):
    sql = "SELECT COUNT(*) FROM topicos WHERE autor_email = ?"
    parametros = [email]
    if desde:
        sql += " AND data_criacao >= ?"
        parametros.append(desde)
    return _consultar(sql, parametros)[0][0]


def contar_comentarios_do_usuario(email, desde=None):
    sql = "SELECT COUNT(*) FROM respostas WHERE autor_email = ?"
    parametros = [email]
    if desde:
        sql += " AND data_criacao >= ?"
        parametros.append(desde)
    return _consultar(sql, parametros)[0][0]


def contar_topicos_respondidos_distintos(email, desde=None):
    """Tópicos DE OUTROS autores que o usuário respondeu (sem contar repetidos)."""
    sql = """
        SELECT COUNT(DISTINCT r.topico_id)
        FROM respostas r JOIN topicos t ON t.id = r.topico_id
        WHERE r.autor_email = ? AND t.autor_email != ?
    """
    parametros = [email, email]
    if desde:
        sql += " AND r.data_criacao >= ?"
        parametros.append(desde)
    return _consultar(sql, parametros)[0][0]


def maior_visualizacao_do_usuario(email):
    sql = "SELECT COALESCE(MAX(visualizacoes), 0) FROM topicos WHERE autor_email = ?"
    return _consultar(sql, [email])[0][0]


# ---------- badges ----------

def listar_badges_do_usuario(email):
    linhas = _consultar(
        "SELECT badge_id FROM badges_usuarios WHERE email = ? ORDER BY data_conquista",
        [email],
    )
    return [linha[0] for linha in linhas]


def conceder_badge(email, badge_id):
    """True se a badge era nova; False se o usuário já tinha."""
    alteradas = _escrever(
        "INSERT OR IGNORE INTO badges_usuarios (email, badge_id, data_conquista) VALUES (?, ?, ?)",
        [email, badge_id, datetime.now().isoformat()],
    )
    return alteradas > 0


def buscar_badge_ativa(email):
    linhas = _consultar("SELECT badge_id FROM badge_ativa WHERE email = ?", [email])
    return linhas[0][0] if linhas else None


def definir_badge_ativa(email, badge_id):
    _escrever("INSERT OR REPLACE INTO badge_ativa (email, badge_id) VALUES (?, ?)", [email, badge_id])


# ---------- missão do dia ----------

def buscar_missao_diaria(email):
    """Devolve (missao_id, data, concluida) ou None."""
    linhas = _consultar(
        "SELECT missao_id, data, concluida FROM missao_diaria WHERE email = ?", [email]
    )
    return linhas[0] if linhas else None


def salvar_missao_diaria(email, missao_id, data):
    _escrever(
        "INSERT OR REPLACE INTO missao_diaria (email, missao_id, data, concluida) VALUES (?, ?, ?, 0)",
        [email, missao_id, data],
    )


def concluir_missao_diaria(email):
    _escrever("UPDATE missao_diaria SET concluida = 1 WHERE email = ?", [email])
