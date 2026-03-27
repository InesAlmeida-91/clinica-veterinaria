# 🐾 Sistema de Clínica Veterinária

Projeto desenvolvido em Python com ligação a base de dados MariaDB, com o objetivo de gerir a informação de uma clínica veterinária.

---

## 🎯 Objetivo

Organizar e gerir:

* donos
* animais
* consultas
* tratamentos

Inclui funcionalidades de histórico clínico e relatórios, simulando um sistema real.

---

## ⚙️ Tecnologias Utilizadas

* Python
* MariaDB (XAMPP / phpMyAdmin)
* mysql-connector-python

---

## 📦 Instalação

### 1. Instalar dependência

pip install mysql-connector-python

---

### 2. Base de dados

Importar o ficheiro `.sql` no phpMyAdmin:

* Criar base de dados: `clinica_veterinaria`
* Importar o ficheiro SQL fornecido

---

## ▶️ Como executar

1. Ligar o MySQL no XAMPP
2. Executar no terminal:

python main.py

---

## 🧩 Funcionalidades

### 👤 Receção

* Registar donos
* Listar donos
* Registar animais
* Listar animais
* Arquivar animais

### 🩺 Consultas

* Marcar consultas
* Listar consultas
* Histórico clínico por animal
* Relatório de gastos por dono

---

## 🧠 Funcionalidades Avançadas

* Validação de IDs (evita erros do utilizador)
* Histórico clínico completo
* Associação de tratamentos a consultas
* Relatórios com cálculo automático
* Arquivamento de animais (ex: falecimento)

---

## 📂 Estrutura do Projeto

* main.py → menu principal
* gestao_recepcao.py → gestão administrativa
* gestao_consultas.py → gestão clínica

---

## 🚀 Melhorias Futuras

* Interface gráfica
* Sistema de login
* Arquivamento de donos
* Exportação de relatórios

---

## 👩‍💻 Autor

Inês Almeida

---

## 📌 Nota

O sistema utiliza arquivamento em vez de eliminação de dados, garantindo a preservação do histórico clínico, como acontece em sistemas reais.
