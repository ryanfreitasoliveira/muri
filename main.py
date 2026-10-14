
from data.armazenamento import criar_tabelas
from interface.menu_principal import Muri_app


def main() -> None:
    criar_tabelas()
    Muri_app().run()


if __name__ == "__main__":
    main()
