# Relatorio de Apresentacao do Projeto

## 1. Enquadramento

O presente projeto consiste numa aplicacao web para apoio a gestao de uma clinica veterinaria. O sistema foi desenvolvido com Python e Flask, recorrendo a uma base de dados MariaDB para armazenamento persistente da informacao. A aplicacao permite gerir donos, animais, consultas, tratamentos e relatorios de gastos, assegurando tambem controlo de acessos por perfil de utilizador.

Este projeto responde a necessidades comuns de uma clinica veterinaria de pequena ou media dimensao, centralizando informacao clinica e administrativa numa unica plataforma.

## 2. Objetivo do Sistema

O objetivo principal e digitalizar os processos base da clinica veterinaria, permitindo:

- Registar e consultar dados de donos.
- Registar, editar e arquivar animais.
- Marcar consultas e acompanhar o respetivo historico.
- Registar tratamentos associados a cada consulta.
- Produzir relatorios de gastos por dono ou por animal.
- Diferenciar permissoes conforme o perfil do utilizador.

## 3. Tecnologias Utilizadas

- Python
- Flask
- MariaDB
- mysql-connector-python
- HTML com templates Jinja2(é uma forma de criar páginas web dinâmicas, onde o HTML é combinado com dados vindos do backend (Flask))
- Tailwind CSS

Esta combinacao permitiu construir uma aplicacao web simples, organizada e adequada a um contexto academico e funcional.

## 4. Estrutura do Projeto

O projeto encontra-se organizado em modulos com responsabilidades distintas:

- [app.py](c:/Users/filip/Desktop/curso%20python/clinica_veterinaria/app.py): define a aplicacao Flask, as rotas e as regras de acesso.
- [auth.py](c:/Users/filip/Desktop/curso%20python/clinica_veterinaria/auth.py): trata da autenticacao de utilizadores.
- [db.py](c:/Users/filip/Desktop/curso%20python/clinica_veterinaria/db.py): centraliza a ligacao a base de dados.
- [services_recepcao.py](c:/Users/filip/Desktop/curso%20python/clinica_veterinaria/services_recepcao.py): contem a logica de negocio associada a donos e animais.
- [services_consultas.py](c:/Users/filip/Desktop/curso%20python/clinica_veterinaria/services_consultas.py): contem a logica de negocio de consultas, tratamentos e relatorios.
- [templates/](c:/Users/filip/Desktop/curso%20python/clinica_veterinaria/templates): inclui as paginas HTML da aplicacao.
- [clinica_veterinaria.sql](c:/Users/filip/Desktop/curso%20python/clinica_veterinaria/clinica_veterinaria.sql): script de criacao e povoamento da base de dados.

## 5. Funcionalidades Principais

### 5.1 Autenticacao e Perfis

O sistema exige autenticacao para acesso as funcionalidades. Existem tres perfis principais:

- `admin`: acesso total ao sistema.
- `rececao`: acesso a operacoes administrativas e de registo.
- `vet`: acesso as operacoes clinicas.

O controlo de acessos e assegurado por decoradores aplicados nas rotas, impedindo que utilizadores sem permissao executem determinadas acoes.

### 5.2 Gestao de Donos

O sistema permite:

- Registar novos donos.
- Listar donos ativos.
- Editar os dados de um dono.

Esta funcionalidade facilita a associacao entre cada animal e o respetivo responsavel.

### 5.3 Gestao de Animais

O sistema permite:

- Registar animais.
- Listar animais.
- Editar dados do animal.
- Arquivar animais que deixem de estar ativos.
- Consultar o historico clinico por animal.

O arquivo de animais evita eliminacao fisica de registos, preservando o historico clinico e administrativo.

### 5.4 Gestao de Consultas

O sistema permite:

- Marcar consultas.
- Listar consultas existentes.
- Consultar detalhes de cada consulta.
- Registar descricao clinica da consulta.

Cada consulta e associada a um animal, a um veterinario e a um motivo de atendimento.

### 5.5 Gestao de Tratamentos

Em cada consulta podem ser associados tratamentos com respetiva quantidade. O sistema permite:

- Adicionar tratamentos a uma consulta.
- Remover tratamentos de uma consulta.
- Calcular custos com base no preco definido para cada tratamento.

### 5.6 Relatorios

O projeto inclui um relatorio de gastos que pode ser filtrado por dono e por animal. Esta funcionalidade e util para apoio administrativo e controlo financeiro.

## 6. Base de Dados

O modelo de dados encontra-se estruturado em varias tabelas principais:

- `utilizadores`: guarda credenciais e perfis de acesso.
- `donos`: guarda os dados dos responsaveis pelos animais.
- `animais`: guarda os dados dos animais e o respetivo estado ativo ou arquivado.
- `veterinarios`: guarda os dados dos profissionais clinicos.
- `consultas`: guarda data, motivo, animal, veterinario e descricao clinica.
- `tratamentos`: guarda o catalogo de tratamentos e respetivos precos.
- `consulta_tratamento`: implementa a relacao entre consultas e tratamentos.

Este modelo relacional garante consistencia e permite cruzar informacao de forma eficiente.

## 7. Fluxo de Utilizacao

O fluxo normal de utilizacao do sistema pode ser descrito da seguinte forma:

1. O utilizador inicia sessao no sistema.
2. A rececao regista donos e animais.
3. A rececao ou o veterinario marca uma consulta.
4. O veterinario consulta o detalhe da consulta e regista observacoes clinicas.
5. O veterinario adiciona tratamentos realizados.
6. O sistema disponibiliza historico clinico e relatorios de gastos.

## 7. Possiveis Evolucoes Futuras

- Encriptacao segura de passwords.
- Pesquisa e filtros avancados em listas de donos, animais e consultas.
- Dashboard inicial com indicadores resumidos.
- Impressao ou exportacao de relatorios em PDF.
- Gestao de estados da consulta, como marcada, realizada ou cancelada.
- Agenda visual para consultas.
- Validacoes adicionais de campos como NIF, email e telefone.

## 12. Conclusao

O projeto de Clinica Veterinaria cumpre os objetivos essenciais propostos, oferecendo uma solucao web para gestao de dados administrativos e clinicos. A aplicacao apresenta uma estrutura clara, integra autenticacao por perfil, utiliza base de dados relacional e disponibiliza funcionalidades relevantes para o funcionamento de uma clinica veterinaria.

Trata-se de um projeto consistente para demonstracao academica, com margem realista para evolucao futura tanto a nivel tecnico como funcional.

## 13. Demonstracao Rapida

Para demonstrar o projeto numa apresentacao, o percurso sugerido e:

1. Mostrar o login com perfis diferentes.
2. Apresentar a listagem de donos e animais.
3. Registar ou editar um animal.
4. Arquivar um animal e explicar a preservacao do historico.
5. Marcar uma consulta e demonstrar as validacoes de data.
6. Abrir o detalhe da consulta e adicionar tratamentos.
7. Mostrar o historico clinico de um animal.
8. Mostrar o relatorio de gastos com filtros.

## 14. Dados de Teste

Os utilizadores de teste definidos no projeto sao:

- `admin` / `admin123`
- `rececao1` / `rececao123`
- `vet1` / `vet123`

## 15. Resumo Final

Em sintese, este projeto implementa um sistema de gestao para clinica veterinaria com autenticacao, organizacao de dados clinicos e administrativos, suporte a consultas e tratamentos, e relatorios de gastos. A aplicacao demonstra a integracao entre frontend, backend e base de dados, constituindo um bom exemplo de aplicacao web CRUD com regras de negocio e controlo de acessos.