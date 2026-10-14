from pathlib import Path
import shutil

from data.armazenamento import (
    BASE_DIR, atualizar_visualizacoes, buscar_topico, buscar_usuario, inserir_topico,
    inserir_resposta, listar_topicos, listar_respostas,
)
from models.resposta import Resposta
from models.topico import Topico
from utils.arquivos import gerar_nome_unico

TAGS_DISPONIVEIS = ["sisu", "matricula", "bolsas", "estagio", "RU"]
EXTENSOES_VALIDAS = {".png", ".jpg", ".jpeg", ".mp4"}
TAMANHO_MAXIMO = 25 * 1024 * 1024  # 25 MB em bytes
PASTA_ANEXOS = BASE_DIR / "data" / "anexos"
LIMITE_RESPOSTA = 2000


def usuario_cadastrado(usuario):
    """True só se há um usuário e o e-mail dele existe no banco."""

    return usuario is not None and buscar_usuario(usuario.email) is not None


def validar_titulo(titulo: str):

    if not titulo.strip():
        return "Título vazio"

    if len(titulo) > 300:
        return "Limite de texto atingido"

    return None


def validar_resposta(conteudo: str):
    if not conteudo.strip():
        return "Resposta vazia"
    if len(conteudo) > LIMITE_RESPOSTA:
        return "Limite de texto atingido"
    return None


def validar_e_salvar_anexo(caminho_original: str):

    caminho = Path(caminho_original.strip().strip('"'))

    if not caminho.is_file():
        return None, "Arquivo não encontrado"

    if caminho.suffix.lower() not in EXTENSOES_VALIDAS:
        return None, "Formato de arquivo não suportado"

    if caminho.stat().st_size > TAMANHO_MAXIMO:
        return None, "Arquivo maior que o limite permitido (máx. 25 MB)"

    PASTA_ANEXOS.mkdir(parents=True, exist_ok=True)
    novo_nome = gerar_nome_unico(str(caminho))
    destino = PASTA_ANEXOS / novo_nome
    shutil.copy(caminho, destino)

    return destino, None


def criar_topico(usuario, titulo, tags, mensagem, caminho_anexo):
    if not usuario_cadastrado(usuario):
        return None, "É preciso estar cadastrado para criar um tópico"
    
    erro = validar_titulo(titulo)
    if erro:
        return None, erro

    anexo_validado = None
    if caminho_anexo:
        anexo_validado, erro = validar_e_salvar_anexo(caminho_anexo)
        if erro:
            return None, erro

    novo_topico = Topico(
        titulo=titulo,
        autor=usuario,
        tags=tags,
        mensagem=mensagem,
        anexos=[anexo_validado] if anexo_validado else [],
    )
    inserir_topico(novo_topico) #manda direto para o banco de dados SQL
    return novo_topico, None


def abrir_topico(id_topico):
    topico = buscar_topico(id_topico)
    if topico is None:
        return None, "Este tópico não existe mais"

    topico.incrementar_visualizacao()
    atualizar_visualizacoes(topico.id, topico.visualizacoes)

    return topico, None


def responder_topico(usuario, id_topico, conteudo):
    if not usuario_cadastrado(usuario):
        return None, "É preciso estar cadastrado para responder"

    erro = validar_resposta(conteudo)
    if erro:
        return None, erro

    if buscar_topico(id_topico) is None:
        return None, "Este tópico não existe mais"

    nova = Resposta(
        topico_id=str(id_topico),
        autor=usuario,
        conteudo=conteudo.strip(),
    )
    inserir_resposta(nova)
    return nova, None
