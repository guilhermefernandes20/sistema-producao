from flask import Flask, render_template, request, redirect, session
import sqlite3

app = Flask(__name__)
app.secret_key = "sistema_producao"


# -----------------------------
# CONECTAR BANCO
# -----------------------------
def conectar():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    return conn


# -----------------------------
# LOGIN
# -----------------------------
@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        usuario = request.form.get("usuario")
        senha = request.form.get("senha")

        if usuario == "admin" and senha == "123":
            session["user"] = usuario
            return redirect("/")

    return render_template("login.html")


# -----------------------------
# LOGOUT
# -----------------------------
@app.route("/logout")
def logout():

    session.clear()
    return redirect("/login")


# -----------------------------
# DASHBOARD
# -----------------------------
@app.route("/")
def index():

    if "user" not in session:
        return redirect("/login")

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT t.id, t.nome, t.funcao, t.valor,
    IFNULL(SUM(p.quantidade),0) as producao
    FROM trabalhadores t
    LEFT JOIN producao p
    ON t.id = p.trabalhador_id
    GROUP BY t.id
    """)

    trabalhadores = cursor.fetchall()

    total_producao = 0
    total_pagamento = 0

    for t in trabalhadores:
        total_producao += t["producao"]
        total_pagamento += t["valor"] * t["producao"]

    conn.close()

    return render_template(
        "index.html",
        trabalhadores=trabalhadores,
        total_producao=total_producao,
        total_pagamento=total_pagamento
    )


# -----------------------------
# TRABALHADORES
# -----------------------------
@app.route("/trabalhadores", methods=["GET", "POST"])
def trabalhadores():

    if "user" not in session:
        return redirect("/login")

    conn = conectar()
    cursor = conn.cursor()

    if request.method == "POST":

        nome = request.form.get("nome")
        funcao = request.form.get("funcao")
        valor = request.form.get("valor")

        cursor.execute("""
        INSERT INTO trabalhadores (nome, funcao, valor)
        VALUES (?, ?, ?)
        """, (nome, funcao, valor))

        conn.commit()

    cursor.execute("SELECT * FROM trabalhadores")
    lista = cursor.fetchall()

    conn.close()

    return render_template("trabalhadores.html", lista=lista)


# -----------------------------
# REGISTRAR PRODUÇÃO
# -----------------------------
@app.route("/produzir/<int:id>", methods=["POST"])
def produzir(id):

    if "user" not in session:
        return redirect("/login")

    quantidade = request.form.get("quantidade")

    if not quantidade:
        return redirect("/trabalhadores")

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO producao (trabalhador_id, quantidade)
    VALUES (?, ?)
    """, (id, quantidade))

    conn.commit()
    conn.close()

    return redirect("/trabalhadores")


# -----------------------------
# EXCLUIR TRABALHADOR
# -----------------------------
@app.route("/excluir/<int:id>")
def excluir(id):

    if "user" not in session:
        return redirect("/login")

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM trabalhadores WHERE id=?", (id,))
    cursor.execute("DELETE FROM producao WHERE trabalhador_id=?", (id,))

    conn.commit()
    conn.close()

    return redirect("/trabalhadores")


# -----------------------------
# ZERAR PRODUÇÃO
# -----------------------------
@app.route("/zerar")
def zerar():

    if "user" not in session:
        return redirect("/login")

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM producao")

    conn.commit()
    conn.close()

    return redirect("/trabalhadores")


# -----------------------------
# INSUMOS
# -----------------------------
@app.route("/insumos", methods=["GET", "POST"])
def insumos():

    if "user" not in session:
        return redirect("/login")

    conn = conectar()
    cursor = conn.cursor()

    if request.method == "POST":

        nome = request.form.get("nome")
        valor = request.form.get("valor")

        cursor.execute("""
        INSERT INTO insumos (nome, valor)
        VALUES (?, ?)
        """, (nome, valor))

        conn.commit()

    cursor.execute("SELECT * FROM insumos")
    lista = cursor.fetchall()

    conn.close()

    return render_template("insumos.html", lista=lista)


# -----------------------------
# RELATÓRIO MENSAL
# -----------------------------
@app.route("/relatorio")
def relatorio():

    if "user" not in session:
        return redirect("/login")

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT t.nome, t.funcao, t.valor,
    SUM(p.quantidade) as producao
    FROM producao p
    JOIN trabalhadores t
    ON p.trabalhador_id = t.id
    WHERE strftime('%Y-%m', p.data) = strftime('%Y-%m','now')
    GROUP BY t.id
    """)

    dados = cursor.fetchall()

    total_mes = 0

    for d in dados:
        total_mes += d["valor"] * d["producao"]

    conn.close()

    return render_template(
        "relatorio.html",
        dados=dados,
        total_mes=total_mes
    )


# -----------------------------
# RODAR SISTEMA
# -----------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)