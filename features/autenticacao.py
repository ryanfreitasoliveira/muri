# features/autenticacao.py — regras de negócio de cadastro e login (RF001)
from data.armazenamento import (
    buscar_usuario,
    buscar_usuario_por_username,
    inserir_usuario,
)
from models.usuario import Cadastro

TAMANHO_MINIMO_SENHA = 6


def cadastrar_usuario(nome, sobrenome, email, username, senha):
    nome, sobrenome = nome.strip(), sobrenome.strip()
    email, username = email.strip().lower(), username.strip()

    if not all([nome, sobrenome, email, username, senha]):
        return None, "Preencha todos os campos."

    valido, mensagem = Cadastro.verifica_email(email)
    if not valido:
        return None, mensagem

    if " " in username:
        return None, "O username não pode ter espaços."
    
    if len(senha) < TAMANHO_MINIMO_SENHA:
        return None, f"A senha precisa ter pelo menos {TAMANHO_MINIMO_SENHA} caracteres."
    
    if buscar_usuario(email) is not None:
        return None, "Já existe uma conta com esse e-mail."
    
    if buscar_usuario_por_username(username) is not None:
        return None, "Esse username já está em uso."

    universitario = email.endswith("@ufrpe.br")
    usuario = Cadastro(
        nome=nome,
        sobrenome=sobrenome,
        email=email,
        username=username,
        senha=senha,
        tipo="universitario" if universitario else "visitante",
        email_e_ufrpe=universitario,
    )
    if not inserir_usuario(usuario):
        return None, "Já existe uma conta com esse e-mail."
    return usuario, None


def autenticar(identificador: str, senha: str):
    identificador = identificador.strip()
    if not identificador or not senha:
        return None, "Preencha todos os campos."

    if "@" in identificador:
        usuario = buscar_usuario(identificador.lower())
    else:
        usuario = buscar_usuario_por_username(identificador)

    if not usuario or usuario.senha != senha:
        return None, "Usuário ou senha incorretos."
    return usuario, None
