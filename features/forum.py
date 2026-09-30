
from models.topico import Topico
from utils.arquivos import gerar_nome_unico
from data.armazenamento import atualizar_visualizacoes, buscar_topico, inserir_topico
from pathlib import Path
import shutil

TAGS_DISPONIVEIS = ["sisu", "matricula", "bolsas", "estagio", "RU"]
EXTENSOES_VALIDAS = {".png", ".jpg", ".jpeg", ".mp4"}
TAMANHO_MAXIMO = 25 * 1024 * 1024  # 25 MB em bytes
PASTA_ANEXOS = Path("data/anexos")


def validar_titulo(titulo: str):
    
    if not titulo.strip():
        return "Título vazio"
    
    if len(titulo) > 300:
        return "Limite de texto atingido"
    
    return None


def validar_e_salvar_anexo(caminho_original: str):

    caminho = Path(caminho_original)

    if caminho.suffix.lower() not in EXTENSOES_VALIDAS:
        return None, "Formato de arquivo não suportado"

    if caminho.stat().st_size > TAMANHO_MAXIMO:
        return None, "Arquivo maior que o limite permitido (máx. 25 MB)"

    novo_nome = gerar_nome_unico(caminho_original)
    destino = PASTA_ANEXOS / novo_nome
    shutil.copy(caminho, destino)

    return destino, None


def criar_topico(usuario, titulo, tags, mensagem, caminho_anexo):
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
    if topico == None:
        return None, "Este tópico não existe mais"

    topico.incrementar_visualizacao()
    atualizar_visualizacoes(topico.id, topico.visualizacoes)

    return topico, None