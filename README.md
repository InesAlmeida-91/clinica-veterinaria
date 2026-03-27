# 🐾 Sistema de Clínica Veterinária

Aplicação web desenvolvida em Python/Flask com ligação a base de dados MariaDB, para gerir uma clínica veterinária com controlo de acessos por perfil de utilizador.

---

## 🎯 Objetivo

Organizar e gerir:

* Donos de animais
* Animais (com arquivo)
* Consultas e descrições clínicas
* Tratamentos por consulta
* Relatórios de gastos

---

## ⚙️ Tecnologias Utilizadas

* Python + Flask
* MariaDB (XAMPP / phpMyAdmin)
* mysql-connector-python
* Tailwind CSS

---

## 📦 Instalação

### 1. Instalar dependências

```bash
pip install flask mysql-connector-python
```

### 2. Base de dados

1. Iniciar o MySQL no XAMPP
2. Abrir o phpMyAdmin
3. Criar base de dados: `clinica_veterinaria`
4. Importar o ficheiro `clinica_veterinaria.sql`

---

## ▶️ Como executar

1. Ligar o MySQL no XAMPP
2. Executar no terminal:

```bash
python app.py
```

3. Abrir o browser em `http://localhost:5000`

---

## 👥 Utilizadores de teste

| Username  | Password     | Perfil  |
|-----------|--------------|---------|
| admin     | admin123     | admin   |
| rececao1  | rececao123   | rececao |
| vet1      | vet123       | vet     |

---

## 🧩 Funcionalidades por perfil

### 👤 Receção (`rececao`)

* Registar e listar donos
* Registar, listar e arquivar animais
* Marcar e listar consultas
* Ver histórico clínico por animal
* Relatório de gastos por dono/animal

### 🩺 Veterinário (`vet`)

* Listar donos e animais
* Marcar e listar consultas
* Ver e editar detalhes de consulta (descrição clínica)
* Gerir tratamentos por consulta
* Ver histórico clínico por animal
* Relatório de gastos

### 🔧 Administrador (`admin`)

* Acesso total a todas as funcionalidades

---

## 📂 Estrutura do Projeto

```
app.py                    # Aplicação Flask e rotas
auth.py                   # Autenticação de utilizadores
db.py                     # Ligação à base de dados
services_recepcao.py      # Serviços de donos e animais
services_consultas.py     # Serviços de consultas e tratamentos
templates/                # Templates HTML (Tailwind CSS)
clinica_veterinaria.sql   # Script SQL da base de dados
```

---

## 👩‍💻 Autor

Inês Almeida

---

