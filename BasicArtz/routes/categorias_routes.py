from flask import render_template
import sqlite3
from app import app

@app.route('/categoria/<categoria>', methods=['GET'])
def categoria(categoria):
    conn = sqlite3.connect('user.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM productos WHERE categoria = ?", (categoria,))
    productos = cursor.fetchall()
    cursor.execute("SELECT DISTINCT categoria FROM productos")
    categorias = cursor.fetchall()
    conn.close()
    return render_template('categorias.html', categoria=categoria, productos=productos, categorias=categorias)
