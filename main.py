from data.armazenamento import criar_tabelas
from data.gamificacao_db import criar_tabelas_gamificacao
from interface.menu_principal import Muri_app


def main() -> None:
    criar_tabelas()
    criar_tabelas_gamificacao()
    Muri_app().run()


if __name__ == "__main__":
    main()
