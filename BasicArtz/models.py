import sqlite3

def init_db():
    conn = sqlite3.connect('user.db')
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            apellido TEXT NOT NULL,
            dni TEXT NOT NULL UNIQUE,
            mail TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            rol TEXT NOT NULL DEFAULT 'user',
            verificacion_1 BOOLEAN DEFAULT FALSE,
            verificacion_2 INTEGER DEFAULT 0,
            imagen1 TEXT,
            imagen2 TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS productos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            precio REAL NOT NULL,
            imagen TEXT NOT NULL,
            estado TEXT NOT NULL DEFAULT 'activo',
            categoria TEXT NOT NULL
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS carrito (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            producto_id INTEGER NOT NULL,
            cantidad INTEGER NOT NULL DEFAULT 1,
            FOREIGN KEY (user_id) REFERENCES usuarios(id),
            FOREIGN KEY (producto_id) REFERENCES productos(id)
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS categorias (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL UNIQUE
        )
    """)
    conn.commit()
    conn.close()

