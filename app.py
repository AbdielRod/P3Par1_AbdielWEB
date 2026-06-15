from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import psycopg2
import re
import os

app = Flask(__name__)
app.secret_key = 'P3Par1_Abdiel_SecretKey_2024'

# Inicializar BD al arrancar
with app.app_context():
    try:
        from init_db import init
        init()
    except Exception as e:
        print(f"Error al inicializar BD: {e}")

# Conexión a PostgreSQL
def conectar():
    return psycopg2.connect(os.environ.get('DATABASE_URL'))

# Expresiones regulares
REGEX_USUARIO = r'^[A-Za-z0-9]{2}_\d{2}#$'
REGEX_PASSWORD = r'^@\d{2}#[A-Za-z]{2}#$'

def login_requerido(f):
    from functools import wraps
    @wraps(f)
    def decorador(*args, **kwargs):
        if 'usuario' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorador

# ── LOGIN ──
@app.route('/', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        usuario = request.form.get('usuario', '')
        password = request.form.get('password', '')

        if not re.match(REGEX_USUARIO, usuario):
            error = 'Usuario inválido. Formato: LL_NN#'
        elif not re.match(REGEX_PASSWORD, password):
            error = 'Password inválido. Formato: @NN#LL#'
        else:
            try:
                con = conectar()
                cur = con.cursor()
                cur.execute("SELECT usuario, password FROM clientes WHERE usuario=%s AND password=%s",
                            (usuario, password))
                row = cur.fetchone()
                con.close()
                if row:
                    session['usuario'] = usuario
                    return redirect(url_for('menu'))
                else:
                    error = 'Usuario o password incorrectos'
            except Exception as e:
                error = f'Error de conexión: {e}'
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# ── MENÚ ──
@app.route('/menu')
@login_requerido
def menu():
    return render_template('menu.html', usuario=session['usuario'])

# ════════════════════════════════
# CLIENTES
# ════════════════════════════════
@app.route('/clientes/altas', methods=['GET', 'POST'])
@login_requerido
def clientes_altas():
    error = None
    exito = None
    if request.method == 'POST':
        nombre     = request.form.get('nombre', '').strip()
        ap_paterno = request.form.get('ap_paterno', '').strip()
        ap_materno = request.form.get('ap_materno', '').strip()
        sexo       = request.form.get('sexo', '')
        telefono   = request.form.get('telefono', '').strip()

        REGEX_NOMBRE   = r'^[A-Za-zÁÉÍÓÚáéíóúÑñ][A-Za-zÁÉÍÓÚáéíóúÑñ ]*$'
        REGEX_TELEFONO = r'^\d{10}$'

        if not re.match(REGEX_NOMBRE, nombre):
            error = 'Nombre inválido.'
        elif not re.match(REGEX_NOMBRE, ap_paterno):
            error = 'Apellido Paterno inválido.'
        elif not re.match(REGEX_NOMBRE, ap_materno):
            error = 'Apellido Materno inválido.'
        elif not re.match(REGEX_TELEFONO, telefono):
            error = 'Teléfono inválido (10 dígitos).'
        else:
            try:
                con = conectar()
                cur = con.cursor()
                cur.execute("SELECT COALESCE(MAX(no_cliente), 0) + 1 FROM clientes")
                no = cur.fetchone()[0]
                cur.execute("""
                    INSERT INTO clientes (no_cliente, nombre, ap_paterno, ap_materno, sexo, telefono)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (no, nombre.upper(), ap_paterno.upper(), ap_materno.upper(), sexo, telefono))
                con.commit()
                con.close()
                exito = f'Cliente registrado con No. {no}'
            except Exception as e:
                error = f'Error: {e}'
    return render_template('clientes_altas.html', error=error, exito=exito)

@app.route('/clientes/consultas')
@login_requerido
def clientes_consultas():
    clientes = []
    try:
        con = conectar()
        cur = con.cursor()
        cur.execute("SELECT no_cliente, nombre, ap_paterno, ap_materno, sexo, telefono FROM clientes ORDER BY no_cliente")
        clientes = cur.fetchall()
        con.close()
    except Exception as e:
        pass
    return render_template('clientes_consultas.html', clientes=clientes)

@app.route('/clientes/modificaciones', methods=['GET', 'POST'])
@login_requerido
def clientes_modificaciones():
    error = None
    exito = None
    clientes = []
    try:
        con = conectar()
        cur = con.cursor()
        cur.execute("SELECT no_cliente, nombre, ap_paterno, ap_materno, sexo, telefono FROM clientes ORDER BY no_cliente")
        clientes = cur.fetchall()
        con.close()
    except:
        pass

    if request.method == 'POST':
        no         = request.form.get('no_cliente', '')
        nombre     = request.form.get('nombre', '').strip()
        ap_paterno = request.form.get('ap_paterno', '').strip()
        ap_materno = request.form.get('ap_materno', '').strip()
        sexo       = request.form.get('sexo', '')
        telefono   = request.form.get('telefono', '').strip()

        REGEX_NOMBRE   = r'^[A-Za-zÁÉÍÓÚáéíóúÑñ][A-Za-zÁÉÍÓÚáéíóúÑñ ]*$'
        REGEX_TELEFONO = r'^\d{10}$'

        if not re.match(REGEX_NOMBRE, nombre):
            error = 'Nombre inválido.'
        elif not re.match(REGEX_NOMBRE, ap_paterno):
            error = 'Apellido Paterno inválido.'
        elif not re.match(REGEX_NOMBRE, ap_materno):
            error = 'Apellido Materno inválido.'
        elif not re.match(REGEX_TELEFONO, telefono):
            error = 'Teléfono inválido (10 dígitos).'
        else:
            try:
                con = conectar()
                cur = con.cursor()
                cur.execute("""
                    UPDATE clientes SET nombre=%s, ap_paterno=%s, ap_materno=%s, sexo=%s, telefono=%s
                    WHERE no_cliente=%s
                """, (nombre.upper(), ap_paterno.upper(), ap_materno.upper(), sexo, telefono, int(no)))
                con.commit()
                cur.execute("SELECT no_cliente, nombre, ap_paterno, ap_materno, sexo, telefono FROM clientes ORDER BY no_cliente")
                clientes = cur.fetchall()
                con.close()
                exito = 'Cliente actualizado correctamente.'
            except Exception as e:
                error = f'Error: {e}'
    return render_template('clientes_modificaciones.html', error=error, exito=exito, clientes=clientes)

@app.route('/clientes/bajas', methods=['GET', 'POST'])
@login_requerido
def clientes_bajas():
    error = None
    exito = None
    clientes = []
    try:
        con = conectar()
        cur = con.cursor()
        cur.execute("SELECT no_cliente, nombre, ap_paterno, ap_materno, sexo, telefono FROM clientes ORDER BY no_cliente")
        clientes = cur.fetchall()
        con.close()
    except:
        pass

    if request.method == 'POST':
        no = request.form.get('no_cliente', '')
        try:
            con = conectar()
            cur = con.cursor()
            cur.execute("DELETE FROM ventas WHERE no_cliente=%s", (int(no),))
            cur.execute("DELETE FROM clientes WHERE no_cliente=%s", (int(no),))
            con.commit()
            cur.execute("SELECT no_cliente, nombre, ap_paterno, ap_materno, sexo, telefono FROM clientes ORDER BY no_cliente")
            clientes = cur.fetchall()
            con.close()
            exito = f'Cliente {no} eliminado correctamente.'
        except Exception as e:
            error = f'Error: {e}'
    return render_template('clientes_bajas.html', error=error, exito=exito, clientes=clientes)

# ════════════════════════════════
# PRODUCTOS
# ════════════════════════════════
@app.route('/productos/altas', methods=['GET', 'POST'])
@login_requerido
def productos_altas():
    error = None
    exito = None
    if request.method == 'POST':
        descripcion = request.form.get('descripcion', '').strip()
        p_unitario  = request.form.get('p_unitario', '').strip()
        existencias = request.form.get('existencias', '').strip()

        REGEX_DESC = r'^[A-Za-zÁÉÍÓÚáéíóúÑñ0-9][A-Za-zÁÉÍÓÚáéíóúÑñ0-9 ]*$'
        REGEX_PRECIO = r'^\d+(\.\d{1,2})?$'
        REGEX_EXIST  = r'^\d+$'

        if not re.match(REGEX_DESC, descripcion):
            error = 'Descripción inválida.'
        elif not re.match(REGEX_PRECIO, p_unitario):
            error = 'Precio unitario inválido.'
        elif not re.match(REGEX_EXIST, existencias):
            error = 'Existencias inválidas.'
        else:
            try:
                con = conectar()
                cur = con.cursor()
                cur.execute("SELECT COALESCE(MAX(clave), 0) + 1 FROM productos")
                clave = cur.fetchone()[0]
                cur.execute("""
                    INSERT INTO productos (clave, descripcion, p_unitario, existencias)
                    VALUES (%s, %s, %s, %s)
                """, (clave, descripcion.upper(), float(p_unitario), int(existencias)))
                con.commit()
                con.close()
                exito = f'Producto registrado con Clave {clave}'
            except Exception as e:
                error = f'Error: {e}'
    return render_template('productos_altas.html', error=error, exito=exito)

@app.route('/productos/consultas')
@login_requerido
def productos_consultas():
    productos = []
    try:
        con = conectar()
        cur = con.cursor()
        cur.execute("SELECT clave, descripcion, p_unitario, existencias FROM productos ORDER BY clave")
        productos = cur.fetchall()
        con.close()
    except:
        pass
    return render_template('productos_consultas.html', productos=productos)

@app.route('/productos/modificaciones', methods=['GET', 'POST'])
@login_requerido
def productos_modificaciones():
    error = None
    exito = None
    productos = []
    try:
        con = conectar()
        cur = con.cursor()
        cur.execute("SELECT clave, descripcion, p_unitario, existencias FROM productos ORDER BY clave")
        productos = cur.fetchall()
        con.close()
    except:
        pass

    if request.method == 'POST':
        clave       = request.form.get('clave', '')
        descripcion = request.form.get('descripcion', '').strip()
        p_unitario  = request.form.get('p_unitario', '').strip()
        existencias = request.form.get('existencias', '').strip()

        REGEX_DESC   = r'^[A-Za-zÁÉÍÓÚáéíóúÑñ0-9][A-Za-zÁÉÍÓÚáéíóúÑñ0-9 ]*$'
        REGEX_PRECIO = r'^\d+(\.\d{1,2})?$'
        REGEX_EXIST  = r'^\d+$'

        if not re.match(REGEX_DESC, descripcion):
            error = 'Descripción inválida.'
        elif not re.match(REGEX_PRECIO, p_unitario):
            error = 'Precio unitario inválido.'
        elif not re.match(REGEX_EXIST, existencias):
            error = 'Existencias inválidas.'
        else:
            try:
                con = conectar()
                cur = con.cursor()
                cur.execute("""
                    UPDATE productos SET descripcion=%s, p_unitario=%s, existencias=%s
                    WHERE clave=%s
                """, (descripcion.upper(), float(p_unitario), int(existencias), int(clave)))
                con.commit()
                cur.execute("SELECT clave, descripcion, p_unitario, existencias FROM productos ORDER BY clave")
                productos = cur.fetchall()
                con.close()
                exito = 'Producto actualizado correctamente.'
            except Exception as e:
                error = f'Error: {e}'
    return render_template('productos_modificaciones.html', error=error, exito=exito, productos=productos)

@app.route('/productos/bajas', methods=['GET', 'POST'])
@login_requerido
def productos_bajas():
    error = None
    exito = None
    productos = []
    try:
        con = conectar()
        cur = con.cursor()
        cur.execute("SELECT clave, descripcion, p_unitario, existencias FROM productos ORDER BY clave")
        productos = cur.fetchall()
        con.close()
    except:
        pass

    if request.method == 'POST':
        clave = request.form.get('clave', '')
        try:
            con = conectar()
            cur = con.cursor()
            cur.execute("DELETE FROM ventas WHERE clave=%s", (int(clave),))
            cur.execute("DELETE FROM productos WHERE clave=%s", (int(clave),))
            con.commit()
            cur.execute("SELECT clave, descripcion, p_unitario, existencias FROM productos ORDER BY clave")
            productos = cur.fetchall()
            con.close()
            exito = f'Producto {clave} eliminado correctamente.'
        except Exception as e:
            error = f'Error: {e}'
    return render_template('productos_bajas.html', error=error, exito=exito, productos=productos)

# ════════════════════════════════
# VENTAS
# ════════════════════════════════
@app.route('/ventas/altas', methods=['GET', 'POST'])
@login_requerido
def ventas_altas():
    error = None
    exito = None
    if request.method == 'POST':
        no_cliente = request.form.get('no_cliente', '').strip()
        clave      = request.form.get('clave', '').strip()
        cantidad   = request.form.get('cantidad', '').strip()

        REGEX_NUM = r'^\d+$'
        if not re.match(REGEX_NUM, no_cliente):
            error = 'No. Cliente inválido.'
        elif not re.match(REGEX_NUM, clave):
            error = 'Clave inválida.'
        elif not re.match(REGEX_NUM, cantidad):
            error = 'Cantidad inválida.'
        else:
            try:
                con = conectar()
                cur = con.cursor()
                cur.execute("SELECT p_unitario FROM productos WHERE clave=%s", (int(clave),))
                row = cur.fetchone()
                if not row:
                    error = 'Producto no encontrado.'
                else:
                    subtotal = float(row[0]) * int(cantidad)
                    iva      = subtotal * 0.16
                    total    = subtotal + iva
                    cur.execute("SELECT COALESCE(MAX(folio), 0) + 1 FROM ventas")
                    folio = cur.fetchone()[0]
                    cur.execute("""
                        INSERT INTO ventas (folio, no_cliente, clave, cantidad, subtotal, iva, total)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """, (folio, int(no_cliente), int(clave), int(cantidad), subtotal, iva, total))
                    con.commit()
                    con.close()
                    exito = f'Venta registrada con Folio {folio}. Total: ${total:.2f}'
            except Exception as e:
                error = f'Error: {e}'
    return render_template('ventas_altas.html', error=error, exito=exito)

@app.route('/ventas/consultas')
@login_requerido
def ventas_consultas():
    ventas = []
    try:
        con = conectar()
        cur = con.cursor()
        cur.execute("SELECT folio, no_cliente, clave, cantidad, subtotal, iva, total FROM ventas ORDER BY folio")
        ventas = cur.fetchall()
        con.close()
    except:
        pass
    return render_template('ventas_consultas.html', ventas=ventas)

@app.route('/ventas/modificaciones', methods=['GET', 'POST'])
@login_requerido
def ventas_modificaciones():
    error = None
    exito = None
    ventas = []
    try:
        con = conectar()
        cur = con.cursor()
        cur.execute("SELECT folio, no_cliente, clave, cantidad, subtotal, iva, total FROM ventas ORDER BY folio")
        ventas = cur.fetchall()
        con.close()
    except:
        pass

    if request.method == 'POST':
        folio      = request.form.get('folio', '')
        no_cliente = request.form.get('no_cliente', '').strip()
        clave      = request.form.get('clave', '').strip()
        cantidad   = request.form.get('cantidad', '').strip()

        REGEX_NUM = r'^\d+$'
        if not re.match(REGEX_NUM, no_cliente):
            error = 'No. Cliente inválido.'
        elif not re.match(REGEX_NUM, clave):
            error = 'Clave inválida.'
        elif not re.match(REGEX_NUM, cantidad):
            error = 'Cantidad inválida.'
        else:
            try:
                con = conectar()
                cur = con.cursor()
                cur.execute("SELECT p_unitario FROM productos WHERE clave=%s", (int(clave),))
                row = cur.fetchone()
                if not row:
                    error = 'Producto no encontrado.'
                else:
                    subtotal = float(row[0]) * int(cantidad)
                    iva      = subtotal * 0.16
                    total    = subtotal + iva
                    cur.execute("""
                        UPDATE ventas SET no_cliente=%s, clave=%s, cantidad=%s, subtotal=%s, iva=%s, total=%s
                        WHERE folio=%s
                    """, (int(no_cliente), int(clave), int(cantidad), subtotal, iva, total, int(folio)))
                    con.commit()
                    cur.execute("SELECT folio, no_cliente, clave, cantidad, subtotal, iva, total FROM ventas ORDER BY folio")
                    ventas = cur.fetchall()
                    con.close()
                    exito = 'Venta actualizada correctamente.'
            except Exception as e:
                error = f'Error: {e}'
    return render_template('ventas_modificaciones.html', error=error, exito=exito, ventas=ventas)

@app.route('/ventas/bajas', methods=['GET', 'POST'])
@login_requerido
def ventas_bajas():
    error = None
    exito = None
    ventas = []
    try:
        con = conectar()
        cur = con.cursor()
        cur.execute("SELECT folio, no_cliente, clave, cantidad, subtotal, iva, total FROM ventas ORDER BY folio")
        ventas = cur.fetchall()
        con.close()
    except:
        pass

    if request.method == 'POST':
        folio = request.form.get('folio', '')
        try:
            con = conectar()
            cur = con.cursor()
            cur.execute("DELETE FROM ventas WHERE folio=%s", (int(folio),))
            con.commit()
            cur.execute("SELECT folio, no_cliente, clave, cantidad, subtotal, iva, total FROM ventas ORDER BY folio")
            ventas = cur.fetchall()
            con.close()
            exito = f'Venta {folio} eliminada correctamente.'
        except Exception as e:
            error = f'Error: {e}'
    return render_template('ventas_bajas.html', error=error, exito=exito, ventas=ventas)

@app.route('/precio/<int:clave>')
@login_requerido
def get_precio(clave):
    try:
        con = conectar()
        cur = con.cursor()
        cur.execute("SELECT p_unitario FROM productos WHERE clave=%s", (clave,))
        row = cur.fetchone()
        con.close()
        if row:
            return jsonify({'precio': float(row[0])})
        return jsonify({'error': 'No encontrado'})
    except Exception as e:
        return jsonify({'error': str(e)})

if __name__ == '__main__':
    app.run(debug=True)
