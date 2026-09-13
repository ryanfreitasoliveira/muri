<a id="topo"></a>

<div align="center">



\# 🎓 M.U.R.I.



\*\*Fórum aberto da comunidade acadêmica da Universidade Federal Rural de Pernambuco (UFRPE)\*\*



<sub>\*\*M\*\*ural \*\*U\*\*niversitário de \*\*R\*\*ede \*\*I\*\*nterativa</sub>



<br/><br/>



<!-- TODO: substituir por assets/logo.png quando a logo estiver pronta -->

<img src="assets/logo.png" width="180" alt="Logotipo do M.U.R.I. (ainda em desenvolvimento)"/>



</div>



\---



\## 📑 Sumário



\- \[Sobre o projeto](#sobre)

\- \[Funcionalidades](#funcionalidades)

\- \[Preview](#preview)

\- \[Requisitos funcionais](#requisitos-funcionais)

\- \[Equipe](#equipe)

\- \[Tecnologias](#tecnologias)

\- \[Como executar](#como-executar)

\- \[Licença](#licenca)



<a id="sobre"></a>

\## 📖 Sobre o projeto



O \*\*M.U.R.I.\*\* é um fórum aberto para alunos da UFRPE. O fórum é o coração do projeto: nele, os estudantes podem tirar dúvidas entre si, construir comunidades, resolver problemas em conjunto e trocar informações do dia a dia acadêmico.



Além do fórum, a plataforma reúne outras funcionalidades pensadas para o dia a dia de quem estuda na universidade:



\- um \*\*mapa interativo\*\* do campus;

\- uma aba de \*\*cursos\*\*, que funciona como um fórum privado para os alunos de cada curso;

\- uma \*\*agenda\*\* de eventos;

\- um sistema de \*\*tags\*\* para facilitar a busca e a filtragem de tópicos;

\- um sistema \*\*gamificado de badges\*\* para reconhecer a participação dos usuários.



<a id="funcionalidades"></a>

\## ✨ Funcionalidades



\- 💬 \*\*Fórum geral\*\* — criação de tópicos, respostas, busca e filtro por tags

\- 🎓 \*\*Cursos\*\* — espaço/fórum privado por curso, com grade, documentos e contatos

\- 🗺️ \*\*Mapa interativo\*\* — pontos do campus (blocos, RU, biblioteca, bicicletário...) com filtros

\- 📅 \*\*Agenda\*\* — criação de eventos, podendo vincular a um local do mapa

\- 🏷️ \*\*Tags\*\* — organização e busca de tópicos

\- 🏅 \*\*Badges\*\* — gamificação para reconhecer a participação dos usuários \*(ainda sem RF detalhado — ver observação abaixo)\*



<a id="preview"></a>

\## 🖼️ Preview



> As imagens abaixo são do protótipo da interface e podem mudar até a versão final.



<div align="center">

&#x20; <img src="assets/preview-forum-home.png" width="700" alt="Tela inicial do fórum com lista de tópicos e filtro por tags"/>

&#x20; <p><em>Página inicial do fórum: listagem de tópicos, filtro por tags e busca</em></p>

&#x20; <br/>

&#x20; <img src="assets/preview-novo-topico.png" width="340" alt="Modal de criação de novo tópico"/>

&#x20; <p><em>Criação de um novo tópico, com título, tag, mensagem e anexos</em></p>

</div>



<a id="requisitos-funcionais"></a>

\## 📋 Requisitos funcionais



| RF | Módulo | O que faz | Prioridade |

|---|---|---|---|

| RF001 | Usuário | Cadastro e visualização de conta como universitário (e-mail `@ufrpe.br`) ou visitante — nome, username, telefone, e-mail e senha, com validações de e-mail duplicado, senha inválida etc. | P1 · Altíssima |

| RF002 | Fórum | Criação de um novo tópico no fórum global: título, tag opcional, mensagem e anexos (imagem/vídeo até 25\&nbsp;MB). | P1 · Altíssima |

| RF003 | Fórum | Resposta a um tópico existente; a resposta é salva e o contador de respostas do tópico é atualizado. | P2 · Alta |

| RF004 | Fórum | Listagem dos tópicos do fórum global, ordenados por atividade recente, com título, tags, nº de respostas e de visualizações. | P2 · Alta |

| RF005 | Fórum | Busca por texto em tempo real combinada com filtro por tags (ex: sisu, matrícula, bolsas, estágio). | P2 · Alta |

| RF006 | Cursos | Aba de cursos: cada curso tem seu espaço com grade curricular, documentação, contatos e um fórum restrito aos alunos daquele curso. | P2 · Alta |

| RF007 | Mapa | Mapa interativo do campus com marcadores por categoria (blocos de aula, RU, biblioteca, bicicletário...), com filtro e detalhes de cada ponto. | P2 · Alta |

| RF008 | Agenda | Criação de eventos na agenda (título, data, horário, descrição e local, podendo vincular a um ponto do mapa). Exige cadastro. | P2 · Alta |



> ℹ️ \*\*Observação:\*\* o sistema de badges/gamificação citado na descrição do projeto ainda não possui um requisito funcional detalhado na planilha de origem.



<a id="equipe"></a>

\## 👥 Equipe



| Nome | Matrícula | Função |

|---|---|---|

| Luis Fernando | \_preencher\_ | Desenvolvedor |

| Ryan Freitas | \_preencher\_ | Desenvolvedor |



<a id="tecnologias"></a>

\## 🛠️ Tecnologias



> ✍️ Preencha conforme a stack escolhida — deixei uma estrutura comum como sugestão.



\- \*\*Front-end:\*\* `a definir`

\- \*\*Back-end:\*\* `a definir`

\- \*\*Banco de dados:\*\* `a definir`

\- \*\*Outras ferramentas:\*\* `a definir`



<a id="como-executar"></a>

\## 🚀 Como executar o projeto



> ✍️ Ajuste os comandos abaixo assim que a stack estiver definida.



```bash

\# 1. Clonar o repositório

git clone https://github.com/<seu-usuario>/<nome-do-repositorio>.git

cd <nome-do-repositorio>



\# 2. Instalar dependências

\# npm install                       # se for Node.js

\# pip install -r requirements.txt   # se for Python



\# 3. Rodar o projeto

\# npm run dev

```



<a id="licenca"></a>

\## 📄 Licença



Este projeto está sob a licença MIT. Veja o arquivo \[LICENSE](LICENSE) para mais detalhes.



\---



<div align="center">



Feito por alunos da UFRPE 💚



\[⬆ voltar ao topo](#topo)



</div>

