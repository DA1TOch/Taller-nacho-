from flask import Flask, render_template, request, redirect, url_for, send_file
from config import Config
from database.models import db, Usuario, Inventario, Cliente, Orden, Proveedor
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
import matplotlib.pyplot as plt
import os
from datetime import datetime
import shutil

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)

login_manager = LoginManager(app)
login_manager.login_view = "login"

@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))

with app.app_context():
    db.create_all()

# ---------- LOGIN ----------
@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        user = Usuario.query.filter_by(username=request.form["username"]).first()
        if user and user.password == request.form["password"]:
            login_user(user)
            return redirect(url_for("dashboard"))
    return render_template("login.html")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))

# ---------- DASHBOARD ----------
@app.route("/")
@login_required
def dashboard():
    total_productos = Inventario.query.count()
    total_clientes = Cliente.query.count()
    ventas = db.session.query(db.func.sum(Orden.total)).scalar() or 0
    stock_bajo = Inventario.query.filter(Inventario.cantidad < 5).count()
    return render_template("dashboard.html",
                           productos=total_productos,
                           clientes=total_clientes,
                           ventas=ventas,
                           stock_bajo=stock_bajo)

# ---------- INVENTARIO ----------
@app.route("/inventario", methods=["GET","POST"])
@login_required
def inventario():
    if request.method=="POST":
        nuevo = Inventario(
            nombre=request.form["nombre"],
            marca=request.form["marca"],
            cantidad=request.form["cantidad"],
            precio=request.form["precio"]
        )
        db.session.add(nuevo)
        db.session.commit()
    productos = Inventario.query.all()
    return render_template("inventario.html", productos=productos)

# ---------- CLIENTES ----------
@app.route("/clientes", methods=["GET","POST"])
@login_required
def clientes():
    if request.method=="POST":
        nuevo = Cliente(
            nombre=request.form["nombre"],
            telefono=request.form["telefono"]
        )
        db.session.add(nuevo)
        db.session.commit()
    lista = Cliente.query.all()
    return render_template("clientes.html", clientes=lista)

# ---------- ORDENES ----------
@app.route("/ordenes", methods=["GET","POST"])
@login_required
def ordenes():
    if request.method=="POST":
        nueva = Orden(
            cliente_id=request.form["cliente_id"],
            trabajo=request.form["trabajo"],
            total=request.form["total"]
        )
        db.session.add(nueva)
        db.session.commit()
    lista = Orden.query.all()
    clientes = Cliente.query.all()
    return render_template("ordenes.html", ordenes=lista, clientes=clientes)

# ---------- FACTURA PDF ----------
@app.route("/factura/<int:id>")
@login_required
def factura(id):
    orden = Orden.query.get(id)
    archivo = f"factura_{id}.pdf"
    doc = SimpleDocTemplate(archivo)
    styles = getSampleStyleSheet()
    elements = []
    elements.append(Paragraph("Taller Nacho", styles["Title"]))
    elements.append(Spacer(1, 12))
    elements.append(Paragraph(f"Trabajo: {orden.trabajo}", styles["Normal"]))
    elements.append(Paragraph(f"Total: ${orden.total}", styles["Normal"]))
    doc.build(elements)
    return send_file(archivo, as_attachment=True)

# ---------- BACKUP AUTOMÁTICO ----------
@app.route("/backup")
@login_required
def backup():
    fecha = datetime.now().strftime("%Y%m%d%H%M%S")
    destino = f"backups/backup_{fecha}.db"
    shutil.copy("taller.db", destino)
    return "Backup creado correctamente"

if __name__ == "__main__":
    app.run(debug=True)
