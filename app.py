import os
from datetime import datetime
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, flash, session
from db import ligar

from services_recepcao import (
    registar_dono, listar_donos,
    registar_animal, listar_animais, arquivar_animal,
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
app.secret_key = os.environ.get("SECRET_KEY", "dev_key")


# --- helpers ---

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            flash("Precisa de fazer login primeiro.")
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated


def role_required(allowed_roles):
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if "role" not in session:
                flash("Acesso negado.")
                return redirect(url_for("index"))
            if session["role"] not in allowed_roles:
                flash("Não tem permissões para esta ação.")
                return redirect(url_for("index"))
            return f(*args, **kwargs)
        return decorated
    return decorator


@app.template_filter('format_datetime')
def format_datetime(value):
    if not value:
        return ''
    if isinstance(value, str):
        try:
            value = datetime.fromisoformat(value)
        except ValueError:
            return value
    try:
        return value.strftime('%d-%m-%Y %H:%M')
    except Exception:
        return str(value)


# --- Auth ---

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        if not username or not password:
            flash("Preencha todos os campos.")
            return redirect(url_for("login"))

        user = autenticar(username, password)

        if user:
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            session["role"] = user.get("role")

            flash("Login efetuado com sucesso.")
            return redirect(url_for("index"))
        else:
            flash("Credenciais inválidas.")

    return render_template("login.html")


@app.route("/logout")
@login_required
def logout():
    session.clear()
    flash("Sessão terminada.")
    return redirect(url_for("login"))


# --- Página inicial ---

@app.route("/")
@login_required
def index():
    return render_template("index.html")


# --- Donos ---

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
        nome = request.form.get("nome", "").strip()
        nif = request.form.get("nif")
        telefone = request.form.get("telefone")
        email = request.form.get("email")

        if not nome:
            flash("Nome é obrigatório.")
            return redirect(url_for("novo_dono"))

        ok = registar_dono(nome, nif, telefone, email)

        if ok:
            flash("Dono registado com sucesso.")
            return redirect(url_for("donos"))

        flash("Erro ao registar dono." )

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
        nome = request.form.get("nome", "").strip()
        nif = request.form.get("nif")
        telefone = request.form.get("telefone")
        email = request.form.get("email")

        if not nome:
            flash("Nome é obrigatório.")
            return redirect(url_for("editar_dono", id_dono=id_dono))

        conn = ligar()
        cursor = conn.cursor()
        cursor.execute("UPDATE donos SET nome=%s, nif=%s, telefone=%s, email=%s WHERE id_dono=%s", (nome, nif, telefone, email, id_dono))
        conn.commit()
        conn.close()

        flash("Dono atualizado com sucesso.")
        return redirect(url_for("donos"))

    return render_template("editar_dono.html", dono=dono)


# --- Animais ---

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
        nome = request.form.get("nome", "").strip()
        especie = request.form.get("especie", "").strip()
        raca = request.form.get("raca", "").strip()
        data_nasc = request.form.get("data_nascimento")
        id_dono = request.form.get("id_dono")

        if not nome or not especie or not id_dono:
            flash("Nome, espécie e dono são obrigatórios.")
            return redirect(url_for("novo_animal"))

        ok, erro = registar_animal(nome, especie, raca, data_nasc, id_dono)

        if ok:
            flash("Animal registado com sucesso.")
            return redirect(url_for("animais"))
        else:
            flash(erro)

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
        nome = request.form.get("nome", "").strip()
        especie = request.form.get("especie", "").strip()
        raca = request.form.get("raca", "").strip()
        data_nasc = request.form.get("data_nascimento")
        id_dono = request.form.get("id_dono")

        if not nome or not especie or not id_dono:
            flash("Nome, espécie e dono são obrigatórios.")
            return redirect(url_for("editar_animal", id_animal=id_animal))

        conn = ligar()
        cursor = conn.cursor()
        cursor.execute("UPDATE animais SET nome=%s, especie=%s, raca=%s, data_nascimento=%s, id_dono=%s WHERE id_animal=%s", (nome, especie, raca, data_nasc, id_dono, id_animal))
        conn.commit()
        conn.close()

        flash("Animal atualizado com sucesso.")
        return redirect(url_for("animais"))

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


# --- Consultas ---

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
    animais_lista = listar_animais()
    veterinarios_lista = listar_veterinarios()

    if request.method == "POST":
        data_consulta = request.form.get("data_consulta")
        motivo = request.form.get("motivo", "").strip()
        id_animal = request.form.get("id_animal")
        id_vet = request.form.get("id_vet")

        if not motivo or not id_animal or not id_vet:
            flash("Motivo, animal e veterinário são obrigatórios.")
            return redirect(url_for("nova_consulta"))

        if data_consulta:
            try:
                dt = datetime.strptime(data_consulta, "%d-%m-%Y %H:%M")
                data_consulta = dt.strftime("%Y-%m-%d %H:%M:%S")
            except ValueError:
                flash("Formato de data inválido. Use DD-MM-AAAA HH:MM")
                return redirect(url_for("nova_consulta"))
        else:
            data_consulta = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        ok, erro = marcar_consulta(data_consulta, motivo, id_animal, id_vet)

        if ok:
            flash("Consulta marcada com sucesso.")
            return redirect(url_for("consultas"))
        else:
            flash(erro)

    return render_template("nova_consulta.html", animais=animais_lista, veterinarios=veterinarios_lista)


# --- Tratamentos em consulta ---

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
            descricao = request.form.get("descricao", "").strip()
            ok, erro = atualizar_descricao_consulta(id_consulta, descricao)
            if ok:
                flash("Descrição da consulta atualizada.")
            else:
                flash(erro)

        elif action == "add_tratamento" and session.get("role") in ["vet", "admin"]:
            id_tratamento = request.form.get("id_tratamento")
            quantidade = request.form.get("quantidade", 1)
            ok, erro = adicionar_tratamento_a_consulta(id_consulta, id_tratamento, quantidade)
            if ok:
                flash("Tratamento adicionado com sucesso.")
            else:
                flash(erro)

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
        id_tratamento = request.form.get("id_tratamento")
        quantidade = request.form.get("quantidade")

        ok, erro = adicionar_tratamento_a_consulta(
            id_consulta, id_tratamento, quantidade
        )

        if ok:
            flash("Tratamento adicionado com sucesso.")
        else:
            flash(erro)

        return redirect(url_for("tratamentos_consulta", id_consulta=id_consulta))

    return render_template(
        "tratamentos_consulta.html",
        id_consulta=id_consulta,
        consulta=consulta,
        tratamentos=tratamentos
    )


# --- Relatórios ---

@app.route("/relatorios/gastos", methods=["GET", "POST"])
@login_required
@role_required(["rececao", "vet", "admin"])
def relatorio_gastos():
    donos_lista = listar_donos()
    animais_lista = listar_animais()
    relatorio = []
    selecionado = False

    if request.method == "POST":
        id_dono = request.form.get("id_dono")
        id_animal = request.form.get("id_animal")
        relatorio = relatorio_gastos_filtro(id_dono=id_dono or None, id_animal=id_animal or None)
        selecionado = True

    return render_template(
        "relatorio_gastos.html",
        relatorio=relatorio,
        donos=donos_lista,
        animais=animais_lista,
        selecionado=selecionado
    )


# --- Run ---

if __name__ == "__main__":
    app.run(debug=True)