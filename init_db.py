import psycopg2
import os

def init():
    con = psycopg2.connect(os.environ.get('DATABASE_URL'))
    cur = con.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS clientes (
            no_cliente SERIAL PRIMARY KEY,
            nombre VARCHAR(50) NOT NULL,
            ap_paterno VARCHAR(50) NOT NULL,
            ap_materno VARCHAR(50) NOT NULL,
            sexo CHAR(1) NOT NULL,
            telefono VARCHAR(15) NOT NULL,
            usuario VARCHAR(20),
            password VARCHAR(20)
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS productos (
            clave SERIAL PRIMARY KEY,
            descripcion VARCHAR(100) NOT NULL,
            p_unitario DECIMAL(10,2) NOT NULL,
            existencias INTEGER NOT NULL
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS ventas (
            folio SERIAL PRIMARY KEY,
            no_cliente INTEGER NOT NULL REFERENCES clientes(no_cliente),
            clave INTEGER NOT NULL REFERENCES productos(clave),
            cantidad INTEGER NOT NULL,
            subtotal DECIMAL(10,2) NOT NULL,
            iva DECIMAL(10,2) NOT NULL,
            total DECIMAL(10,2) NOT NULL
        )
    """)

    cur.execute("""
        INSERT INTO clientes (nombre, ap_paterno, ap_materno, sexo, telefono, usuario, password)
        SELECT 'MARIA','MARTINEZ','PEREZ','F','5523456789','AV_12#','@12#Av#'
        WHERE NOT EXISTS (SELECT 1 FROM clientes WHERE usuario='AV_12#')
    """)

    con.commit()
    con.close()
    print("Base de datos inicializada correctamente.")

if __name__ == '__main__':
    init()
