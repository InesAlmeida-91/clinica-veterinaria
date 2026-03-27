import os
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, flash, session

from services_recepcao import (
    registar_dono, listar_donos,
    registar_animal, listar_animais, arquivar_animal
)
from services_consultas import (
    marcar_consulta, listar_consultas,
    historico_por_animal, relatorio_gastos_por_dono,
    listar_tratamentos, adicionar_tratamento_a_consulta
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
def donos():
    donos_lista = listar_donos()
    return render_template("donos.html", donos=donos_lista)


@app.route("/donos/novo", methods=["GET", "POST"])
@login_required
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

        flash("Erro ao registar dono.")

    return render_template("novo_dono.html")


# --- Animais ---

@app.route("/animais")
@login_required
def animais():
    animais_lista = listar_animais()
    return render_template("animais.html", animais=animais_lista)


@app.route("/animais/novo", methods=["GET", "POST"])
@login_required
def novo_animal():
    if request.method == "POST":
        nome = request.form.get("nome", "").strip()
        especie = request.form.get("especie", "").strip()
        raca = request.form.get("raca", "").strip()
        data_nasc = request.form.get("data_nascimento")
        id_dono = request.form.get("id_dono")

        if not nome or not especie:
            flash("Nome e espécie são obrigatórios.")
            return redirect(url_for("novo_animal"))

        ok, erro = registar_animal(nome, especie, raca, data_nasc, id_dono)

        if ok:
            flash("Animal registado com sucesso.")
            return redirect(url_for("animais"))
        else:
            flash(erro)

    return render_template("novo_animal.html")


@app.route("/animais/<int:id_animal>/arquivar", methods=["POST"])
@login_required
def arquivar_animal_route(id_animal):
    ok, erro = arquivar_animal(id_animal)

    if ok:
        flash("Animal arquivado com sucesso.")
    else:
        flash(erro)

    return redirect(url_for("animais"))


@app.route("/animais/<int:id_animal>/historico")
@login_required
def historico_animal(id_animal):
    historico = historico_por_animal(id_animal)
    return render_template(
        "historico_animal.html",
        historico=historico,
        id_animal=id_animal
    )


# --- Consultas ---

@app.route("/consultas")
@login_required
def consultas():
    consultas_lista = listar_consultas()
    return render_template("consultas.html", consultas=consultas_lista)


@app.route("/consultas/nova", methods=["GET", "POST"])
@login_required
def nova_consulta():
    if request.method == "POST":
        data_consulta = request.form.get("data_consulta")
        motivo = request.form.get("motivo", "").strip()
        id_animal = request.form.get("id_animal")
        id_vet = request.form.get("id_vet")

        if not motivo:
            flash("Motivo é obrigatório.")
            return redirect(url_for("nova_consulta"))

        ok, erro = marcar_consulta(data_consulta, motivo, id_animal, id_vet)

        if ok:
            flash("Consulta marcada com sucesso.")
            return redirect(url_for("consultas"))
        else:
            flash(erro)

    return render_template("nova_consulta.html")


# --- Tratamentos em consulta ---

@app.route("/consultas/<int:id_consulta>/tratamentos", methods=["GET", "POST"])
@login_required
def tratamentos_consulta(id_consulta):

    if session.get("role") != "vet":
        flash("Apenas veterinários podem adicionar tratamentos.")
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
        tratamentos=tratamentos
    )


# --- Relatórios ---

@app.route("/relatorios/gastos")
@login_required
def relatorio_gastos():
    relatorio = relatorio_gastos_por_dono()
    return render_template("relatorio_gastos.html", relatorio=relatorio)


# --- Run ---

if __name__ == "__main__":
    app.run(debug=True)