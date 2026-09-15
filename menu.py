import rich
import time
import os 
from mural_muri import mural
from init import Cadastro


def start_menu():
  print("[blue]1-Acessar mural[/blue]")
  print("[blue]2-Alterar/Excluir dados[/blue]")
  print("[blue]0-Sair do muri[/blue]")
  escolha = input()
while True:
    start_menu()
    if start_menu.escolha == 1:
        mural()

    elif start_menu.escolha == 2:
        print("nome: " + Cadastro.name)
        print("email: " + Cadastro.email)
        print("Senha:" + Cadastro.senha)
        print("[blue]Escolha que alteração você quer fazer[/blue]")
        print("[blue]1-Alterar Nome[/blue]")
        print("[blue]2-Alterar email[/blue]")
        print("[blue]3-Alterar senha[/blue]")
        print("[blue]0-Retornar[/blue]")
        alterar_item = input()
        if alterar_item == 1:
           novo_nome = input("Insira o novo nome")
           novo_nome = Cadastro.name
    elif start_menu.escolha == 0:
        break