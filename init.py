from rich import print
import os
import time
from menu import start_menu


def start():
    print("[bold dark_blue]Olá!! Bem vindo ao Muri[/bold dark_blue]")
    time.sleep(0.5)
    print("[bold bright_blue]Faça seu login ou seu cadastro[/bold bright_blue]")
    time.sleep(0.5)


class Cadastro:
    def __init__(self):
        print("[bold bright_blue]Insira o seu nome[/bold bright_blue]")
        self.name = input()
        os.system('cls')
        self.email = input("Insira o seu email: ")
        self.isufrpe = True
        os.system('cls')
        self.senha = input("Insira sua senha: ")
        self.domain = "@ufrpe.br"
        self.verify_email_ufrpe()

    def verify_email_ufrpe(self):
        if self.domain in self.email:
            self.isufrpe = True
        else:
            self.isufrpe = False

    def email_not_ufrpe(self):
        if self.isufrpe == False:
            print("Você não precisa fazer cadastro! Sua conta é de visitante!")

    def email_invalido(self):
        if len(self.email) < 10:
            print("Email inválido!")


start()
time.sleep(1)
novo_cadastro = Cadastro()
time.sleep(1)


novo_cadastro.email_invalido()
novo_cadastro.email_not_ufrpe()
os.system('cls')
if Cadastro.isufrpe == True:
    print(f"Cadastro Realizado {Cadastro.name}")

time.sleep(1)
os.system('cls')
start_menu()