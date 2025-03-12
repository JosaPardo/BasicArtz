from flask import render_template, request, session, redirect, url_for, flash
import sqlite3
from app import app

@app.route('/agregar_al_carrito/<int:producto_id>', methods=['POST'])
def agregar_al_carrito(producto_id):
    if 'user_id' not in session:
        flash('Debes iniciar sesión.', 'danger')
        return redirect(url_for('login'))
    user_id = session['user_id']
    cantidad = int(request.form.get('cantidad', 1))
    conn = sqlite3.connect('user.db')
    cursor = conn.cursor()
    cursor.execute("SELECT cantidad FROM carrito WHERE user_id = ? AND producto_id = ?", (user_id, producto_id))
    existente = cursor.fetchone()
    if existente:
        nueva_cantidad = existente[0] + cantidad
        cursor.execute("UPDATE carrito SET cantidad = ? WHERE user_id = ? AND producto_id = ?", (nueva_cantidad, user_id, producto_id))
    else:
        cursor.execute("INSERT INTO carrito (user_id, producto_id, cantidad) VALUES (?, ?, ?)", (user_id, producto_id, cantidad))
    conn.commit()
    conn.close()
    flash('Producto agregado al carrito.', 'success')
    return redirect(url_for('index'))
