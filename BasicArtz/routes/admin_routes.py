from functools import wraps
from flask import render_template, request, redirect, url_for, flash, session
from werkzeug.utils import secure_filename
import sqlite3
from forms import ProductForm
from helpers import allowed_file
from app import app, mail
from flask_mail import Message

def admin_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'user_role' not in session or session['user_role'] != 'admin':
            flash('Acceso denegado. Solo administradores pueden entrar.', 'danger')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return wrap

@app.route('/admin')
@admin_required
def admin_panel():
    conn = sqlite3.connect('user.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, nombre, precio, imagen, estado FROM productos")
    productos = cursor.fetchall()
    conn.close()
    return render_template('admin_panel.html', productos=productos)

@app.route('/admin/add_product', methods=['GET', 'POST'])
@admin_required
def add_product():
    form = ProductForm()
    form.cargar_categorias()
    if form.validate_on_submit():
        nombre = form.nombre.data
        precio = form.precio.data
        imagen_file = form.imagen.data
        categoria = form.categoria.data
        if imagen_file:
            filename = secure_filename(imagen_file.filename)
            imagen_file.save(f'static/uploads/{filename}')
        else:
            filename = ''
        conn = sqlite3.connect('user.db')
        cursor = conn.cursor()
        cursor.execute("INSERT INTO productos (nombre, precio, imagen, categoria) VALUES (?, ?, ?, ?)", 
                       (nombre, precio, filename, categoria))
        conn.commit()
        conn.close()
        flash('Producto agregado exitosamente.', 'success')
        return redirect(url_for('admin_panel'))
    return render_template('add_product.html', form=form)

@app.route('/admin/add_category', methods=['POST'])
@admin_required
def add_category():
    category_name = request.form['category_name']
    conn = sqlite3.connect('user.db')
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM categorias WHERE nombre = ?", (category_name,))
    existing_category = cursor.fetchone()[0]
    if existing_category == 0:
        cursor.execute("INSERT INTO categorias (nombre) VALUES (?)", (category_name,))
        conn.commit()
        flash('Categoría agregada exitosamente', 'success')
    else:
        flash('La categoría ya existe', 'danger')
    conn.close()
    return redirect(url_for('admin_panel'))

@app.route('/admin/pausar_producto/<int:producto_id>')
@admin_required
def pausar_producto(producto_id):
    conn = sqlite3.connect('user.db')
    cursor = conn.cursor()
    cursor.execute("SELECT estado FROM productos WHERE id = ?", (producto_id,))
    estado_actual = cursor.fetchone()[0]
    nuevo_estado = 'pausado' if estado_actual == 'activo' else 'activo'
    cursor.execute("UPDATE productos SET estado = ? WHERE id = ?", (nuevo_estado, producto_id))
    conn.commit()
    conn.close()
    flash(f'Producto {"pausado" if nuevo_estado == "pausado" else "activado"} exitosamente.', 'success')
    return redirect(url_for('admin_panel'))

@app.route('/admin/eliminar_producto/<int:producto_id>')
@admin_required
def eliminar_producto(producto_id):
    conn = sqlite3.connect('user.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM productos WHERE id = ?", (producto_id,))
    conn.commit()
    conn.close()
    flash('Producto eliminado exitosamente.', 'danger')
    return redirect(url_for('admin_panel'))

@app.route('/validaciones', methods=['GET'])
@admin_required
def ver_validaciones():
    conn = sqlite3.connect('user.db')
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, nombre, apellido, dni, imagen1, imagen2, verificacion_2 FROM usuarios
    """)
    usuarios = cursor.fetchall()
    conn.close()
    # Separar usuarios en tres listas: pendientes, validados y rechazados
    pendientes = [usuario for usuario in usuarios if usuario[6] == 0]  # Usuarios pendientes (verificacion_2 == 0)
    validados = [usuario for usuario in usuarios if usuario[6] == 1]  # Usuarios validados (verificacion_2 == 1)
    rechazados = [usuario for usuario in usuarios if usuario[6] == 3]  # Usuarios rechazados (verificacion_2 == 3)
    # Pasar las listas al template
    return render_template('validaciones.html', pendientes=pendientes, validados=validados, rechazados=rechazados)