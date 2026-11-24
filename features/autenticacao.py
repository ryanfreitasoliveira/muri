# features/autenticacao.py — regras de negócio de cadastro e login (RF001)
from data.armazenamento import (
    buscar_usuario,
    buscar_usuario_por_username,
    inserir_usuario,
    atualizar_usuario,
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
        return (
            None,
            f"A senha precisa ter pelo menos {TAMANHO_MINIMO_SENHA} caracteres.",
        )

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


def validar_dados_perfil(usuario, nome, sobrenome, email, username):
    nome, sobrenome = nome.strip(), sobrenome.strip()
    email, username = email.strip().lower(), username.strip()

    if not all([nome, sobrenome, email, username]):
        return "Preencha nome, sobrenome, e-mail e username."

    valido, mensagem = Cadastro.verifica_email(email)
    if not valido:
        return mensagem

    if " " in username:
        return "O username não pode ter espaços."

    existente = buscar_usuario(email)
    if existente is not None and existente.email != usuario.email:
        return "Já existe uma conta com esse e-mail."

    existente = buscar_usuario_por_username(username)
    if existente is not None and existente.email != usuario.email:
        return "Esse username já está em uso."

    return None


def atualizar_perfil(usuario, nome, sobrenome, email, username, senha):
    erro = validar_dados_perfil(usuario, nome, sobrenome, email, username)
    if erro:
        return None, erro

    atual = buscar_usuario(usuario.email)
    if atual is None:
        return None, "Conta não encontrada."

    if not senha:
        return None, "Digite sua senha para confirmar."
    if senha != atual.senha:
        return None, "Senha incorreta."

    email = email.strip().lower()
    universitario = email.endswith("@ufrpe.br")
    atualizado = Cadastro(
        nome=nome.strip(),
        sobrenome=sobrenome.strip(),
        email=email,
        username=username.strip(),
        senha=atual.senha,
        tipo="universitario" if universitario else "visitante",
        email_e_ufrpe=universitario,
    )
    if not atualizar_usuario(atual.email, atualizado):
        return None, "Não foi possível atualizar os dados."
    return atualizado, None
