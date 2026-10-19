"""Encuesta Turismax: formulario web para clientes y viajeros.

- Guarda cada respuesta en PostgreSQL (variable DATABASE_URL) o, si no existe, en SQLite local.
- /resultados (protegido con usuario y clave) muestra el conteo y permite descargar el Excel.
"""
import hmac
import io
import os
import sqlite3
from datetime import datetime, timezone

from flask import Flask, Response, abort, make_response, redirect, render_template, request, send_file, url_for
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill

from preguntas import COLUMNAS, NO_APLICA, PREGUNTAS, SECCIONES

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 64 * 1024  # un formulario nunca pesa más que esto

DATABASE_URL = os.environ.get("DATABASE_URL", "")
ADMIN_USER = os.environ.get("ADMIN_USER", "admin")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "")
SQLITE_PATH = os.environ.get("SQLITE_PATH", "respuestas.db")
MAX_COMENTARIO = 1000

# ---------------------------------------------------------------- base de datos
USA_POSTGRES = DATABASE_URL.startswith(("postgres://", "postgresql://"))
if USA_POSTGRES:
    import psycopg

    _URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)


def conectar():
    if USA_POSTGRES:
        return psycopg.connect(_URL)
    return sqlite3.connect(SQLITE_PATH)


PH = "%s" if USA_POSTGRES else "?"  # marcador de parámetros según el motor


def crear_tabla():
    id_col = "SERIAL PRIMARY KEY" if USA_POSTGRES else "INTEGER PRIMARY KEY AUTOINCREMENT"
    cols = ", ".join(f'"{c}" TEXT' for c in COLUMNAS)
    with conectar() as con:
        con.execute(f'CREATE TABLE IF NOT EXISTS respuestas (id {id_col}, fecha_utc TEXT NOT NULL, {cols})')


def guardar(fila):
    nombres = ", ".join(['fecha_utc'] + [f'"{c}"' for c in COLUMNAS])
    marcas = ", ".join([PH] * (len(COLUMNAS) + 1))
    valores = [datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")] + [fila.get(c) for c in COLUMNAS]
    with conectar() as con:
        con.execute(f"INSERT INTO respuestas ({nombres}) VALUES ({marcas})", valores)


def leer_todo():
    with conectar() as con:
        cur = con.execute(f'SELECT id, fecha_utc, {", ".join(chr(34) + c + chr(34) for c in COLUMNAS)} FROM respuestas ORDER BY id')
        return cur.fetchall()


def contar():
    with conectar() as con:
        return con.execute("SELECT COUNT(*) FROM respuestas").fetchone()[0]


crear_tabla()


# ---------------------------------------------------------------- validación
def seccion_activa(sec_id, form):
    sec = next(s for s in SECCIONES if s["id"] == sec_id)
    if not sec["mostrar_si"]:
        return True
    col, valor = sec["mostrar_si"]
    return form.get(col) == valor


def validar(form):
    """Devuelve (fila, errores). Las preguntas de secciones ocultas se guardan como 'No aplica'."""
    fila, errores = {}, {}
    if form.get("consentimiento") != "si":
        errores["consentimiento"] = "Debe aceptar el tratamiento de datos para enviar la encuesta."
    for p in PREGUNTAS:
        col = p["col"]
        if not seccion_activa(p["sec"], form):
            fila[col] = None if p["tipo"] == "escala" else NO_APLICA
            continue
        if p["tipo"] == "uno":
            v = form.get(col, "")
            if v not in p["opciones"]:
                errores[col] = "Seleccione una opción."
            fila[col] = v
        elif p["tipo"] == "escala":
            v = form.get(col, "")
            if v not in {"1", "2", "3", "4", "5"}:
                errores[col] = "Seleccione un valor de 1 a 5."
            fila[col] = v
        elif p["tipo"] == "varios":
            vs = [v for v in form.getlist(col) if v in p["opciones"]]
            vs = [o for o in p["opciones"] if o in vs]  # orden fijo y sin duplicados
            if not vs:
                errores[col] = "Marque al menos una opción."
            elif p.get("maximo") and len(vs) > p["maximo"]:
                errores[col] = f"Marque como máximo {p['maximo']} opciones."
            elif p.get("exclusiva") in vs and len(vs) > 1:
                errores[col] = f"«{p['exclusiva']}» no se puede combinar con otras opciones."
            fila[col] = "; ".join(vs)
        elif p["tipo"] == "texto":
            fila[col] = form.get(col, "").strip()[:MAX_COMENTARIO]
    return fila, errores


# ---------------------------------------------------------------- rutas públicas
@app.get("/")
def formulario():
    if request.cookies.get("turismax_respondio") == "1":
        return render_template("gracias.html", repetido=True)
    return render_template("formulario.html", secciones=SECCIONES, preguntas=PREGUNTAS, datos={}, errores={})


@app.post("/enviar")
def enviar():
    if request.form.get("sitio_web"):  # campo trampa invisible: solo lo llenan los bots
        return redirect(url_for("gracias"))
    fila, errores = validar(request.form)
    if errores:
        datos = {p["col"]: request.form.getlist(p["col"]) for p in PREGUNTAS}
        datos["consentimiento"] = request.form.get("consentimiento")
        return render_template("formulario.html", secciones=SECCIONES, preguntas=PREGUNTAS,
                               datos=datos, errores=errores), 400
    guardar(fila)
    resp = make_response(redirect(url_for("gracias")))
    resp.set_cookie("turismax_respondio", "1", max_age=60 * 60 * 24 * 90, samesite="Lax", secure=request.is_secure)
    return resp


@app.get("/gracias")
def gracias():
    return render_template("gracias.html", repetido=False)


@app.get("/salud")
def salud():
    return "ok"


# ---------------------------------------------------------------- rutas protegidas
def autorizado():
    auth = request.authorization
    return bool(ADMIN_PASSWORD) and auth is not None and \
        hmac.compare_digest(auth.username or "", ADMIN_USER) and \
        hmac.compare_digest(auth.password or "", ADMIN_PASSWORD)


def pedir_clave():
    return Response("Se requiere usuario y clave.", 401, {"WWW-Authenticate": 'Basic realm="Resultados Turismax"'})


@app.get("/resultados")
def resultados():
    if not ADMIN_PASSWORD:
        abort(404)  # sin clave configurada, los resultados no existen públicamente
    if not autorizado():
        return pedir_clave()
    return render_template("resultados.html", total=contar())


@app.get("/resultados/excel")
def excel():
    if not ADMIN_PASSWORD:
        abort(404)
    if not autorizado():
        return pedir_clave()
    wb = Workbook()
    ws = wb.active
    ws.title = "Respuestas"
    encabezado = ["ID", "Fecha_UTC"] + COLUMNAS
    ws.append(encabezado)
    for c in ws[1]:
        c.font = Font(bold=True, color="FFFFFF")
        c.fill = PatternFill("solid", fgColor="1F4E79")
    escalas = {p["col"] for p in PREGUNTAS if p["tipo"] == "escala"}
    for fila in leer_todo():
        fila = list(fila)
        for i, col in enumerate(COLUMNAS, start=2):
            if col in escalas and fila[i] not in (None, ""):
                fila[i] = int(fila[i])
        ws.append(fila)
    for col_cells in ws.columns:
        ws.column_dimensions[col_cells[0].column_letter].width = max(12, min(40, len(str(col_cells[0].value)) + 4))
    ws.freeze_panes = "C2"
    buf = io.BytesIO()
    wb.save(buf)
    buf.seek(0)
    nombre = f"respuestas_turismax_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx"
    return send_file(buf, as_attachment=True, download_name=nombre,
                     mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")


if __name__ == "__main__":
    app.run(debug=True, port=int(os.environ.get("PORT", 5000)))
