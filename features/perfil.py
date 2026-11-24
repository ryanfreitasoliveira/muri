from data.armazenamento import contar_respostas_do_usuario, listar_topicos
from features.gamificacao import resumo_gamificacao


def resumo_do_usuario(usuario) -> dict:
    meus_topicos = [
        t for t in listar_topicos() if t.autor and t.autor.email == usuario.email
    ]
    return {
        "nome_completo": f"{usuario.nome} {usuario.sobrenome}".strip(),
        "username": usuario.username,
        "email": usuario.email,
        "tipo": (
            "Universitário (UFRPE)" if usuario.tipo == "universitario" else "Visitante"
        ),
        "total_topicos": len(meus_topicos),
        "total_respostas": contar_respostas_do_usuario(usuario.email),
        "topicos": [(t.id, t.titulo, t.visualizacoes) for t in meus_topicos],
        "gamificacao": resumo_gamificacao(usuario),
    }
