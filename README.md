<a id="topo"></a>
<div align="center">

# 🎓 M.U.R.I. - **M**ural **U**niversitário de **R**ede **I**nterativa


**Fórum aberto para a comunidade acadêmica e alunos visitantes da Universidade Federal Rural de Pernambuco (UFRPE)**


<br/><br/>

<!-- TODO: substituir por assets/logo.png quando a logo estiver pronta -->
<img src="assets/logo.png" width="180" alt="Logotipo do M.U.R.I. (ainda em desenvolvimento)"/>

</div>

---

## 📑 Sumário

- [Sobre o projeto](#sobre)
- [Funcionalidades](#funcionalidades)
- [Preview](#preview)
- [Requisitos funcionais](#requisitos-funcionais)
- [Equipe](#equipe)
- [Tecnologias](#tecnologias)
- [Como executar](#como-executar)
- [Licença](#licenca)

<a id="sobre"></a>
## 📖 Sobre o projeto

O **M.U.R.I.**(Mural Universitário de Rede Interativa) é um mural interativo e aberto que conecta a comunidade da UFRPE. Focado na colaboração entre alunos e visitantes, o projeto centraliza a troca de informações acadêmicas, permitindo que estudantes resolvam problemas em conjunto e construam comunidades ativas dentro do ambiente universitário.

Além do fórum, a plataforma reúne outras funcionalidades pensadas para o dia a dia de quem estuda na universidade:

- um **mapa interativo** do campus;
- uma aba de **cursos**, que funciona como um fórum privado para os alunos de cada curso;
- uma **agenda** de eventos;
- um sistema de **tags** para facilitar a busca e a filtragem de tópicos;
- um sistema **gamificado de badges** para reconhecer a participação dos usuários.

<a id="funcionalidades"></a>
## ✨ Funcionalidades

- 💬 **Fórum geral** — criação de tópicos, respostas, busca e filtro por tags
- 📚 **Cursos** — espaço/fórum privado por curso, com grade, documentos e contatos
- 🗺️ **Mapa interativo** — pontos do campus (blocos, RU, biblioteca, bicicletário...) com filtros
- 📅 **Agenda** — criação de eventos, podendo vincular a um local do mapa
- 🏷️ **Tags** — organização e busca de tópicos
- 🏅 **Badges** — gamificação para reconhecer a participação dos usuários *(ainda sem RF detalhado — ver observação abaixo)*

<a id="preview"></a>
## 🖼️ Preview

> As imagens abaixo são do protótipo da interface e podem mudar até a versão final.

<div align="center">
  <img src="assets/preview-forum-home.png" width="700" alt="Tela inicial do fórum com lista de tópicos e filtro por tags"/>
  <p><em>Página inicial do fórum: listagem de tópicos, filtro por tags e busca</em></p>
  <br/>
  <img src="assets/preview-novo-topico.png" width="340" alt="Modal de criação de novo tópico"/>
  <p><em>Criação de um novo tópico, com título, tag, mensagem e anexos</em></p>
</div>

<a id="requisitos-funcionais"></a>
## 📋 Requisitos funcionais

| RF | Módulo | O que faz | Prioridade |
|---|---|---|---|
| RF001 - Cadastro e Login | Usuário | Cadastro e visualização de conta como universitário (e-mail `@ufrpe.br`) ou visitante — nome, username, telefone, e-mail e senha. | P1 · Altíssima |
| RF002 -  Criação de tópico | Fórum | Criação de um novo tópico no fórum global: título, tag opcional, mensagem e anexos (imagem/vídeo até 25&nbsp;MB) - Exige cadastro. | P1 · Altíssima |
| RF003 - Responder Tópico | Fórum | Resposta a um tópico existente; a resposta é salva e o contador de respostas do tópico é atualizado - Exige cadastro. | P2 · Alta |
| RF004 - Listagem de tópicos | Fórum | Listagem dos tópicos do fórum global, ordenados por atividade recente, com título, tags, nº de respostas e de visualizações. | P2 · Alta |
| RF005 - Busca e filtro | Fórum | Busca por texto em tempo real combinada com filtro por tags (ex: sisu, matrícula, bolsas, estágio). | P2 · Alta |
| RF006 - Aba privada | Cursos | Aba de cursos: cada curso tem seu espaço com grade curricular, documentação, contatos e um fórum restrito aos alunos daquele curso. | P2 · Alta |
| RF007 -  Mapa interativo | Mapa | Mapa interativo do campus com marcadores por categoria (blocos de aula, RU, biblioteca, bicicletário...), com filtro e detalhes de cada ponto. | P2 · Alta |
| RF008 - Criação de evento | Agenda | Criação de eventos na agenda (título, data, horário, descrição e local) - Exige cadastro. | P2 · Alta |

> ℹ️ **Observação:** o sistema de badges/gamificação citado na descrição do projeto ainda não possui um requisito funcional detalhado na planilha de origem. 

<a id="equipe"></a>
## 👥 Equipe

| Nome | Matrícula | Função |
|---|---|---|
| Luis Fernando Melo| _preencher_ | Desenvolvedor |
| Ryan Freitas Oliveira | _preencher_ | Desenvolvedor |

<a id="tecnologias"></a>
## 🛠️ Tecnologias


- **Front-end:** `a definir`
- **Back-end:** `Python`
- **Banco de dados:** `a definir`
- **Outras ferramentas:** `a definir`

<a id="como-executar"></a>
## 🚀 Como executar o projeto


```bash
# 1. Clonar o repositório
git clone https://github.com/<seu-usuario>/<nome-do-repositorio>.git
cd <nome-do-repositorio>

# 2. Instalar dependências
# npm install                       # se for Node.js
# pip install -r requirements.txt   # se for Python

# 3. Rodar o projeto
# npm run dev
```

<a id="licenca"></a>
## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

---

<div align="center">

Feito por alunos da UFRPE 🎓

[⬆ voltar ao topo](#topo)

</div>
