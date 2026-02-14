from flask import Flask, request, redirect, send_file, render_template_string
import sqlite3
import pandas as pd
from datetime import datetime

app = Flask(__name__)
APP_NAME = "Taller Nacho – Sistema de Gestión"

# ---------- BASE DE DATOS ----------
def db():
    conn = sqlite3.connect("taller.db")
    return conn, conn.cursor()

def init_db():
    conn, c = db()
    c.execute("CREATE TABLE IF NOT EXISTS inventario(id INTEGER PRIMARY KEY, nombre TEXT, marca TEXT, cantidad INTEGER, precio INTEGER)")
    c.execute("CREATE TABLE IF NOT EXISTS clientes(id INTEGER PRIMARY KEY, nombre TEXT, telefono TEXT)")
    c.execute("CREATE TABLE IF NOT EXISTS ordenes(id INTEGER PRIMARY KEY, cliente TEXT, trabajo TEXT, total INTEGER, fecha TEXT)")
    conn.commit()
    conn.close()

init_db()

# ---------- PLANTILLA ----------
def pagina(titulo, contenido):
    return f"""
<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{titulo} | {APP_NAME}</title>
<link rel="icon" href="data:image/svg+xml,
<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'>
<text y='0.9em' font-size='90'>🏍️</text>
</svg>">
<style>
body {{font-family:Arial;background:#f4f4f4;padding:15px}}
header {{background:#111;color:white;padding:12px;text-align:center;font-size:20px}}
a {{display:block;margin:8px 0;color:#0066cc}}
.card {{background:white;padding:15px;border-radius:6px;margin-bottom:10px}}
input,button {{width:100%;padding:10px;margin:5px 0}}
</style>
</head>
<body>
<header>🏍️ {APP_NAME}</header>
<div class="card">
{contenido}
</div>
</body>
</html>
"""

# ---------- RUTAS ----------
@app.route("/")
def inicio():
    return pagina("Inicio", """
<a href="/inventario">📦 Inventario</a>
<a href="/clientes">👥 Clientes</a>
<a href="/ordenes">🧰 Órdenes de trabajo</a>
<a href="/exportar">📊 Exportar inventario a Excel</a>
""")

@app.route("/inventario", methods=["GET","POST"])
def inventario():
    conn, c = db()
    if request.method=="POST":
        c.execute("INSERT INTO inventario VALUES(NULL,?,?,?,?)",
                  (request.form["n"],request.form["m"],request.form["c"],request.form["p"]))
        conn.commit()
    items=""
    for r in c.execute("SELECT * FROM inventario"):
        items+=f"<p>{r[1]} | {r[2]} | Cant: {r[3]} | ${r[4]:,} COP</p>"
    conn.close()
    return pagina("Inventario", f"""
<h3>Inventario</h3>
<form method="post">
<input name="n" placeholder="Nombre">
<input name="m" placeholder="Marca">
<input name="c" type="number" placeholder="Cantidad">
<input name="p" type="number" placeholder="Precio COP">
<button>Agregar</button>
</form>
<hr>{items}
<a href="/">Volver</a>
""")

@app.route("/clientes", methods=["GET","POST"])
def clientes():
    conn,c=db()
    if request.method=="POST":
        c.execute("INSERT INTO clientes VALUES(NULL,?,?)",(request.form["n"],request.form["t"]))
        conn.commit()
    lista=""
    for r in c.execute("SELECT * FROM clientes"):
        lista+=f"<p>{r[1]} - {r[2]}</p>"
    conn.close()
    return pagina("Clientes", f"""
<h3>Clientes</h3>
<form method="post">
<input name="n" placeholder="Nombre">
<input name="t" placeholder="Teléfono">
<button>Agregar</button>
</form>
<hr>{lista}
<a href="/">Volver</a>
""")

@app.route("/ordenes", methods=["GET","POST"])
def ordenes():
    conn,c=db()
    if request.method=="POST":
        c.execute("INSERT INTO ordenes VALUES(NULL,?,?,?,?)",
                  (request.form["c"],request.form["t"],request.form["v"],datetime.now().strftime("%d/%m/%Y")))
        conn.commit()
    lista=""
    for r in c.execute("SELECT * FROM ordenes"):
        lista+=f"<p>{r[1]} | {r[2]} | ${r[3]:,} COP | {r[4]}</p>"
    conn.close()
    return pagina("Órdenes", f"""
<h3>Órdenes de trabajo</h3>
<form method="post">
<input name="c" placeholder="Cliente">
<input name="t" placeholder="Trabajo realizado">
<input name="v" type="number" placeholder="Total COP">
<button>Guardar</button>
</form>
<hr>{lista}
<a href="/">Volver</a>
""")

@app.route("/exportar")
def exportar():
    conn=sqlite3.connect("taller.db")
    df=pd.read_sql("SELECT * FROM inventario",conn)
    archivo="inventario.xlsx"
    df.to_excel(archivo,index=False)
    return send_file(archivo,as_attachment=True)

# ---------- EJECUCIÓN ----------
if __name__ == "__main__":
    app.run(debug=False, use_reloader=False)
