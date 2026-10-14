from dataclasses import dataclass

@dataclass
class Cadastro:
    username: str = ""
    email: str = ""
    senha: str = ""
    nome: str = ""
    sobrenome: str = ""
    tipo: str = "visitante"  # "universitario" (e-mail @ufrpe.br) ou "visitante"
    email_e_ufrpe: bool = False
    dominio: str = "@ufrpe.br"

    
    def verifica_email(email: str) -> tuple[bool, str]:
        email = email.lower()

        # Verifica a estrutura básica do e-mail
        if len(email) < 6 or email.count("@") != 1:
            return False, "E-mail curto ou inválido!"

        parte_local, dominio_email = email.rsplit("@", 1)

        if not parte_local or not dominio_email:
            return False, "E-mail inválido!"

        if "." not in dominio_email:
            return False, "Domínio do e-mail inválido!"

        if dominio_email.startswith(".") or dominio_email.endswith("."):
            return False, "Domínio do e-mail inválido!"

        # Verifica se o domínio é institucional
        if dominio_email == "ufrpe.br":
            return True, "E-mail institucional verificado!"

        return True, "E-mail válido, mas não institucional."
