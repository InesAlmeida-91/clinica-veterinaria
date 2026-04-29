import os
import re
import logging
from datetime import datetime, timedelta
from functools import wraps

from flask import Flask, render_template, request, redirect, url_for, flash, session
from markupsafe import escape
from flask_wtf.csrf import CSRFProtect

from db import ligar
from services_recepcao import (
    registar_dono, listar_donos,
    registar_animal, listar_animais, listar_animais_ativos, arquivar_animal,
    buscar_dono, buscar_animal
)
from services_consultas import (
    marcar_consulta, listar_consultas,
    historico_por_animal, relatorio_gastos_por_dono, relatorio_gastos_filtro,
    listar_tratamentos, adicionar_tratamento_a_consulta,
    listar_veterinarios, consulta_por_id, atualizar_descricao_consulta,
    tratamentos_por_consulta, remover_tratamento_consulta
)
from auth import autenticar

app = Flask(__name__)

# ==========================================================
# CONFIGURAÇÃO BASE DE SEGURANÇA
# ==========================================================
# Mantém a estrutura original, mas reforça a segurança das sessões.
# - SECRET_KEY deve vir de variável de ambiente em produção
# - cookies HttpOnly dificultam roubo da sessão por JavaScript
# - SameSite ajuda na mitigação de ataques CSRF
# - tempo de sessão limitado para reduzir risco de sessão esquecida
app.secret_key = os.environ.get("SECRET_KEY", "dev_key")
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(minutes=20)
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
app.config["SESSION_COOKIE_SECURE"] = False  # Em produção com HTTPS deve ser True


# Ativa proteção CSRF sem obrigar a refazer a app toda.
# Depois é preciso colocar {{ csrf_token() }} nos formulários HTML com POST.
csrf = CSRFProtect(app)

# Logging básico para registar acessos, falhas de login e erros de autorização.
logging.basicConfig(
    filename="app_security.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# ==========================================================
# VALIDAÇÃO E SANITIZAÇÃO DE INPUTS
# ==========================================================
# Estas funções são simples, mas permitem justificar:
# - validação de tipo
# - validação de tamanho
# - validação de formato
# - sanitização / escape para reduzir risco de XSS
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def limpar_texto(valor, max_len=100):
    valor = (valor or "").strip()
    valor = escape(valor)
    if len(valor) > max_len:
        raise ValueError(f"Máximo de {max_len} caracteres.")
    return valor


def validar_email(email):
    email = (email or "").strip()
    if email and not EMAIL_RE.match(email):
        raise ValueError("Email inválido.")
    return email


def validar_nif(nif):
    nif = (nif or "").strip()
    if nif and (not nif.isdigit() or len(nif) != 9):
        raise ValueError("NIF inválido.")
    return nif


def validar_telefone(telefone):
    telefone = (telefone or "").strip()
    if telefone and (not telefone.isdigit() or len(telefone) < 9 or len(telefone) > 15):
        raise ValueError("Telefone inválido.")
    return telefone


def validar_id(valor, nome="ID"):
    valor = str(valor).strip()
    if not valor.isdigit():
        raise ValueError(f"{nome} inválido.")
    return int(valor)


def validar_quantidade(valor):
    valor = str(valor).strip()
    if not valor.isdigit():
        raise ValueError("Quantidade inválida.")
    valor = int(valor)
    if valor <= 0:
        raise ValueError("Quantidade inválida.")
    return valor


# ==========================================================
# HELPERS
# ==========================================================
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            flash("Precisa de fazer login primeiro.")
            return redirect(url_for("login"))

        # Ao marcar a sessão como permanente, a app aplica o tempo de expirar definido
        session.permanent = True
        return f(*args, **kwargs)
    return decorated


def role_required(allowed_roles):
    @wraps(role_required)
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if "role" not in session:
                logging.warning("Tentativa de acesso sem sessão válida.")
                flash("Acesso negado.")
                return redirect(url_for("index"))

            if session["role"] not in allowed_roles:
                logging.warning(
                    f"Acesso proibido user={session.get('username')} role={session.get('role')} rota={request.path}"
                )
                flash("Não tem permissões para esta ação.")
                return redirect(url_for("index"))

            return f(*args, **kwargs)
        return decorated
    return decorator


@app.template_filter("format_datetime")
def format_datetime(value):
    if not value:
        return ""
    if isinstance(value, str):
        try:
            value = datetime.fromisoformat(value)
        except ValueError:
            return value
    try:
        return value.strftime("%d-%m-%Y %H:%M")
    except Exception:
        return str(value)


# ==========================================================
# AUTH
# ==========================================================
@app.route("/login", methods=["GET", "POST"])
def login():
    # Limitação simples de tentativas de login.
    # Não é tão forte como rate limiting por IP/Redis, mas já demonstra
    # controlo de abuso e monitorização de acessos falhados.
    if "login_tentativas" not in session:
        session["login_tentativas"] = 0

    if request.method == "POST":
        if session["login_tentativas"] >= 5:
            logging.warning("Demasiadas tentativas de login falhadas na mesma sessão.")
            flash("Demasiadas tentativas falhadas. Tente mais tarde.")
            return render_template("login.html")

        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        if not username or not password:
            flash("Preencha todos os campos.")
            return redirect(url_for("login"))

        # A função autenticar deve usar hash de passwords no auth.py,
        # substituindo a comparação insegura em texto simples do ficheiro inicial.
        user = autenticar(username, password)

        if user:
            # Limpa a sessão antes de criar nova sessão autenticada.
            # Isto ajuda a reduzir risco de fixação de sessão.
            session.clear()
            session.permanent = True
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            session["role"] = user.get("role")
            session["login_tentativas"] = 0

            logging.info(f"Login com sucesso: {username}")
            flash("Login efetuado com sucesso.")
            return redirect(url_for("index"))
        else:
            session["login_tentativas"] += 1
            logging.warning(f"Login falhado: {username}")
            flash("Credenciais inválidas.")

    return render_template("login.html")


@app.route("/logout")
@login_required
def logout():
    session.clear()
    flash("Sessão terminada.")
    return redirect(url_for("login"))


# ==========================================================
# PÁGINA INICIAL
# ==========================================================
@app.route("/")
@login_required
def index():
    return render_template("index.html")


# ==========================================================
# DONOS
# ==========================================================
@app.route("/donos")
@login_required
@role_required(["rececao", "vet", "admin"])
def donos():
    donos_lista = listar_donos()
    return render_template("donos.html", donos=donos_lista)


@app.route("/donos/novo", methods=["GET", "POST"])
@login_required
@role_required(["rececao", "admin"])
def novo_dono():
    if request.method == "POST":
        try:
            # Validação e sanitização de dados recebidos do utilizador
            nome = limpar_texto(request.form.get("nome", ""), 100)
            nif = validar_nif(request.form.get("nif"))
            telefone = validar_telefone(request.form.get("telefone"))
            email = validar_email(request.form.get("email"))

            if not nome:
                flash("Nome é obrigatório.")
                return redirect(url_for("novo_dono"))

            ok = registar_dono(nome, nif, telefone, email)

            if ok:
                flash("Dono registado com sucesso.")
                return redirect(url_for("donos"))

            flash("Erro ao registar dono.")

        except ValueError as e:
            flash(str(e))

    return render_template("novo_dono.html")


@app.route("/donos/<int:id_dono>/editar", methods=["GET", "POST"])
@login_required
@role_required(["rececao", "admin"])
def editar_dono(id_dono):
    dono = buscar_dono(id_dono)
    if not dono:
        flash("Dono não encontrado.")
        return redirect(url_for("donos"))

    if request.method == "POST":
        try:
            nome = limpar_texto(request.form.get("nome", ""), 100)
            nif = validar_nif(request.form.get("nif"))
            telefone = validar_telefone(request.form.get("telefone"))
            email = validar_email(request.form.get("email"))

            if not nome:
                flash("Nome é obrigatório.")
                return redirect(url_for("editar_dono", id_dono=id_dono))

            # Mantém query parametrizada para prevenir SQL Injection
            conn = ligar()
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE donos SET nome=%s, nif=%s, telefone=%s, email=%s WHERE id_dono=%s",
                (nome, nif, telefone, email, id_dono)
            )
            conn.commit()
            conn.close()

            flash("Dono atualizado com sucesso.")
            return redirect(url_for("donos"))

        except ValueError as e:
            flash(str(e))

    return render_template("editar_dono.html", dono=dono)


# ==========================================================
# ANIMAIS
# ==========================================================
@app.route("/animais")
@login_required
@role_required(["rececao", "vet", "admin"])
def animais():
    animais_lista = listar_animais()
    return render_template("animais.html", animais=animais_lista)


@app.route("/animais/novo", methods=["GET", "POST"])
@login_required
@role_required(["rececao", "admin"])
def novo_animal():
    donos_lista = listar_donos()

    if request.method == "POST":
        try:
            nome = limpar_texto(request.form.get("nome", ""), 100)
            especie = limpar_texto(request.form.get("especie", ""), 50)
            raca = limpar_texto(request.form.get("raca", ""), 50)
            data_nasc = request.form.get("data_nascimento")
            id_dono = validar_id(request.form.get("id_dono"), "Dono")

            if not nome or not especie:
                flash("Nome, espécie e dono são obrigatórios.")
                return redirect(url_for("novo_animal"))

            ok, erro = registar_animal(nome, especie, raca, data_nasc, id_dono)

            if ok:
                flash("Animal registado com sucesso.")
                return redirect(url_for("animais"))
            else:
                flash(erro)

        except ValueError as e:
            flash(str(e))

    return render_template("novo_animal.html", donos=donos_lista)


@app.route("/animais/<int:id_animal>/editar", methods=["GET", "POST"])
@login_required
@role_required(["rececao", "admin"])
def editar_animal(id_animal):
    animal = buscar_animal(id_animal)
    donos_lista = listar_donos()

    if not animal:
        flash("Animal não encontrado.")
        return redirect(url_for("animais"))

    if request.method == "POST":
        try:
            nome = limpar_texto(request.form.get("nome", ""), 100)
            especie = limpar_texto(request.form.get("especie", ""), 50)
            raca = limpar_texto(request.form.get("raca", ""), 50)
            data_nasc = request.form.get("data_nascimento")
            id_dono = validar_id(request.form.get("id_dono"), "Dono")

            if not nome or not especie:
                flash("Nome, espécie e dono são obrigatórios.")
                return redirect(url_for("editar_animal", id_animal=id_animal))

            conn = ligar()
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE animais SET nome=%s, especie=%s, raca=%s, data_nascimento=%s, id_dono=%s WHERE id_animal=%s",
                (nome, especie, raca, data_nasc, id_dono, id_animal)
            )
            conn.commit()
            conn.close()

            flash("Animal atualizado com sucesso.")
            return redirect(url_for("animais"))

        except ValueError as e:
            flash(str(e))

    return render_template("editar_animal.html", animal=animal, donos=donos_lista)


@app.route("/animais/<int:id_animal>/arquivar", methods=["POST"])
@login_required
@role_required(["rececao", "admin"])
def arquivar_animal_route(id_animal):
    ok, erro = arquivar_animal(id_animal)

    if ok:
        flash("Animal arquivado com sucesso.")
    else:
        flash(erro)

    return redirect(url_for("animais"))


@app.route("/animais/<int:id_animal>/historico")
@login_required
@role_required(["rececao", "vet", "admin"])
def historico_animal(id_animal):
    animal = buscar_animal(id_animal)
    if not animal:
        flash("Animal não encontrado.")
        return redirect(url_for("animais"))

    historico = historico_por_animal(id_animal)
    return render_template(
        "historico_animal.html",
        historico=historico,
        animal=animal
    )


# ==========================================================
# CONSULTAS
# ==========================================================
@app.route("/consultas")
@login_required
@role_required(["rececao", "vet", "admin"])
def consultas():
    consultas_lista = listar_consultas()
    return render_template("consultas.html", consultas=consultas_lista)


@app.route("/consultas/nova", methods=["GET", "POST"])
@login_required
@role_required(["rececao", "vet", "admin"])
def nova_consulta():
    animais_lista = listar_animais_ativos()
    veterinarios_lista = listar_veterinarios()
    min_datetime = datetime.now().replace(second=0, microsecond=0).strftime("%Y-%m-%dT%H:%M")

    form_data = {
        "data_consulta": "",
        "motivo": "",
        "id_animal": "",
        "id_vet": "",
    }

    if request.method == "POST":
        try:
            form_data = {
                "data_consulta": request.form.get("data_consulta", "").strip(),
                "motivo": request.form.get("motivo", "").strip(),
                "id_animal": request.form.get("id_animal", "").strip(),
                "id_vet": request.form.get("id_vet", "").strip(),
            }

            data_consulta = form_data["data_consulta"]
            motivo = limpar_texto(form_data["motivo"], 255)
            id_animal = validar_id(form_data["id_animal"], "Animal")
            id_vet = validar_id(form_data["id_vet"], "Veterinário")
            agora = datetime.now().replace(second=0, microsecond=0)

            if not data_consulta or not motivo:
                flash("Data, motivo, animal e veterinário são obrigatórios.", "error")
                return render_template(
                    "nova_consulta.html",
                    animais=animais_lista,
                    veterinarios=veterinarios_lista,
                    form_data=form_data,
                    min_datetime=min_datetime
                )

            # Validação do formato e da lógica temporal da data
            try:
                dt = datetime.strptime(data_consulta, "%Y-%m-%dT%H:%M")
            except ValueError:
                try:
                    dt = datetime.strptime(data_consulta, "%d-%m-%Y %H:%M")
                except ValueError:
                    flash("Formato de data inválido. Selecione uma data e hora válidas.", "error")
                    return render_template(
                        "nova_consulta.html",
                        animais=animais_lista,
                        veterinarios=veterinarios_lista,
                        form_data=form_data,
                        min_datetime=min_datetime
                    )

            if dt < agora:
                flash("A data da consulta não pode ser no passado.", "error")
                return render_template(
                    "nova_consulta.html",
                    animais=animais_lista,
                    veterinarios=veterinarios_lista,
                    form_data=form_data,
                    min_datetime=min_datetime
                )

            data_consulta = dt.strftime("%Y-%m-%d %H:%M:%S")

            ok, erro = marcar_consulta(data_consulta, motivo, id_animal, id_vet)

            if ok:
                flash("Consulta marcada com sucesso.", "success")
                return redirect(url_for("consultas"))
            else:
                flash(erro, "error")

        except ValueError as e:
            flash(str(e), "error")

    return render_template(
        "nova_consulta.html",
        animais=animais_lista,
        veterinarios=veterinarios_lista,
        form_data=form_data,
        min_datetime=min_datetime
    )


@app.route("/consultas/<int:id_consulta>", methods=["GET", "POST"])
@login_required
@role_required(["vet", "admin"])
def consulta_detalhes(id_consulta):
    consulta = consulta_por_id(id_consulta)
    if not consulta:
        flash("Consulta não encontrada.")
        return redirect(url_for("consultas"))

    tratamentos_disponiveis = listar_tratamentos()
    consulta_tratamentos = tratamentos_por_consulta(id_consulta)

    if request.method == "POST":
        action = request.form.get("action", "")

        if action == "descricao" and session.get("role") in ["vet", "admin"]:
            try:
                descricao = limpar_texto(request.form.get("descricao", ""), 2000)
                ok, erro = atualizar_descricao_consulta(id_consulta, descricao)
                if ok:
                    flash("Descrição da consulta atualizada.")
                else:
                    flash(erro)
            except ValueError as e:
                flash(str(e))

        elif action == "add_tratamento" and session.get("role") in ["vet", "admin"]:
            try:
                id_tratamento = validar_id(request.form.get("id_tratamento"), "Tratamento")
                quantidade = validar_quantidade(request.form.get("quantidade", 1))
                ok, erro = adicionar_tratamento_a_consulta(id_consulta, id_tratamento, quantidade)
                if ok:
                    flash("Tratamento adicionado com sucesso.")
                else:
                    flash(erro)
            except ValueError as e:
                flash(str(e))

        else:
            flash("Ação não permitida.")

        return redirect(url_for("consulta_detalhes", id_consulta=id_consulta))

    return render_template(
        "consulta_detalhes.html",
        consulta=consulta,
        tratamentos_disponiveis=tratamentos_disponiveis,
        consulta_tratamentos=consulta_tratamentos
    )


@app.route("/consultas/<int:id_consulta>/tratamentos/<int:id_tratamento>/remover", methods=["POST"])
@login_required
@role_required(["vet", "admin"])
def remover_tratamento_route(id_consulta, id_tratamento):
    ok, erro = remover_tratamento_consulta(id_consulta, id_tratamento)
    if ok:
        flash("Tratamento removido.")
    else:
        flash(erro)
    return redirect(url_for("consulta_detalhes", id_consulta=id_consulta))


@app.route("/consultas/<int:id_consulta>/tratamentos", methods=["GET", "POST"])
@login_required
@role_required(["vet", "admin"])
def tratamentos_consulta(id_consulta):
    consulta = consulta_por_id(id_consulta)
    if not consulta:
        flash("Consulta não encontrada.")
        return redirect(url_for("consultas"))

    tratamentos = listar_tratamentos()

    if request.method == "POST":
        try:
            id_tratamento = validar_id(request.form.get("id_tratamento"), "Tratamento")
            quantidade = validar_quantidade(request.form.get("quantidade"))

            ok, erro = adicionar_tratamento_a_consulta(
                id_consulta, id_tratamento, quantidade
            )

            if ok:
                flash("Tratamento adicionado com sucesso.")
            else:
                flash(erro)

        except ValueError as e:
            flash(str(e))

        return redirect(url_for("tratamentos_consulta", id_consulta=id_consulta))

    return render_template(
        "tratamentos_consulta.html",
        id_consulta=id_consulta,
        consulta=consulta,
        tratamentos=tratamentos
    )


# ==========================================================
# RELATÓRIOS
# ==========================================================
@app.route("/relatorios/gastos", methods=["GET", "POST"])
@login_required
@role_required(["rececao", "vet", "admin"])
def relatorio_gastos():
    donos_lista = listar_donos()
    animais_lista = listar_animais()
    relatorio = []
    selecionado = False

    if request.method == "POST":
        try:
            id_dono = request.form.get("id_dono")
            id_animal = request.form.get("id_animal")

            # Validação leve: só converte para inteiro se vier valor preenchido
            if id_dono:
                id_dono = validar_id(id_dono, "Dono")
            else:
                id_dono = None

            if id_animal:
                id_animal = validar_id(id_animal, "Animal")
            else:
                id_animal = None

            relatorio = relatorio_gastos_filtro(id_dono=id_dono, id_animal=id_animal)
            selecionado = True

        except ValueError as e:
            flash(str(e))

    return render_template(
        "relatorio_gastos.html",
        relatorio=relatorio,
        donos=donos_lista,
        animais=animais_lista,
        selecionado=selecionado
    )


# ==========================================================
# RUN
# ==========================================================
if __name__ == "__main__":
    # Em ambiente de desenvolvimento pode ficar debug=True,
    # mas em produção deve ser False.
    app.run(debug=True)