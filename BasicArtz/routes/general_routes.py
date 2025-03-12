import os
import random
import sqlite3
import string
import bcrypt
from flask import request, session, redirect, url_for, flash, render_template
from flask_mail import Message
from app import app, mail
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash




@app.route('/')
def index():
    conn = sqlite3.connect('user.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM productos WHERE estado = 'activo'")
    productos = cursor.fetchall()
    cursor.execute("SELECT DISTINCT categoria FROM productos")
    categorias = cursor.fetchall()
    conn.close()
    return render_template('index.html', productos=productos, categorias= categorias)

@app.route('/register')
def register():
    return render_template('register.html')

def generar_codigo_verificacion():
    """Genera un código de verificación aleatorio de 6 dígitos."""
    return ''.join(random.choices(string.digits, k=6))

# Registro del usuario con verificacion_1 en False
@app.route('/submit', methods=['POST'])
def submit():
    print("Solicitud recibida en /submit")
    # Datos del formulario
    nombre = request.form.get('txtName')
    apellido = request.form.get('txtSurname')
    dni = request.form.get('txtDNI')
    user_mail = request.form.get('txtMail')
    contraseña = request.form.get('txtPassword')
    print(f"Datos recibidos: Nombre={nombre}, Apellido={apellido}, DNI={dni}, Mail={user_mail}")
    if not (nombre and apellido and dni and user_mail and contraseña):
        print("Faltan datos en el formulario")
        flash("Todos los campos son obligatorios", "danger")
        return redirect(url_for('register'))
    hashed_password = generate_password_hash(contraseña).encode('utf-8')


    try:
        conn = sqlite3.connect('user.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM usuarios WHERE dni = ? OR mail = ?", (dni, user_mail))
        existing_user = cursor.fetchone()
        if existing_user:
            print("El usuario ya está registrado")
            flash('El DNI o el correo ya están registrados', 'danger')
            return redirect(url_for('register'))

        cursor.execute(
            'INSERT INTO usuarios (nombre, apellido, dni, mail, password, rol, verificacion_1, verificacion_2) VALUES (?,?,?,?,?,?,?,?)',
            (nombre, apellido, dni, user_mail, hashed_password, "user", False, False)
        )
        conn.commit()
        conn.close()
        print("Usuario registrado con éxito")
        codigo_verificacion = generar_codigo_verificacion()
        # Almacenar el código en la sesión (temporalmente)
        session['codigo_verificacion'] = codigo_verificacion
        session['usuario_mail'] = user_mail
        print(f"Código de verificación: {codigo_verificacion}")
        # Enviar el código por correo electrónico
        msg = Message('Código de verificación', recipients=[user_mail])
        msg.body = f'Este es tu código de verificación: {codigo_verificacion}'
        mail.send(msg)
        print(f"Correo enviado a {user_mail}")
        flash('Registro exitoso. Revisa tu correo para verificar tu cuenta.', 'success')
        return redirect(url_for('register'))

    except Exception as e:
        print(f"Error al registrar: {e}")
        flash(f'Error al registrar: {e}', 'danger')
        return redirect(url_for('register'))

@app.route('/BasicArtz')
def basic_artz():
    return render_template('contacto.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Has cerrado sesión.', 'success')
    return redirect(url_for('index'))

@app.route('/verificar_codigo', methods=['POST', 'GET'])
def verificar_codigo():
    codigo_ingresado = request.form.get('codigo_verificacion')
    user_mail = session.get('usuario_mail')

    try:
        codigo_sesion = session.get('codigo_verificacion')
        if not codigo_sesion:
            flash("El código de verificación ha expirado o no se ha generado correctamente.", "danger")
            return redirect(url_for('index'))  

        if codigo_ingresado == codigo_sesion:
            conn = sqlite3.connect('user.db')
            cursor = conn.cursor()
            cursor.execute("UPDATE usuarios SET verificacion_1 = 1 WHERE mail = ?", (user_mail,))
            conn.commit()
            conn.close()
            flash("Correo verificado con éxito. Ahora puedes iniciar sesión.", "success")
            return redirect(url_for('login'))
        else:
            flash("El código es incorrecto.", "danger")
            return redirect(url_for('verificar_codigo'))  

    except Exception as e:
        print(f"Error al verificar el código: {e}")
        flash(f'Error al verificar el código: {e}', 'danger')
        return redirect(url_for('verificar_codigo'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['txtMail']
        password = request.form['txtPassword']
        conn = sqlite3.connect('user.db')
        cursor = conn.cursor()
        cursor.execute("SELECT id, nombre, apellido, password, rol, mail, verificacion_1 FROM usuarios WHERE mail = ?", (username,))
        usuario = cursor.fetchone()
        conn.close()

        if usuario:
            user_id, nombre, apellido, hashed_password, user_role, user_mail, verificacion_1 = usuario
            if isinstance(hashed_password, bytes):
                hashed_password = hashed_password.decode('utf-8')
                
            if check_password_hash(hashed_password, password):
                # Verificar si el usuario ha verificado su correo (comprobar verificacion_1)
                if not verificacion_1:
                    flash('Debes verificar tu correo antes de iniciar sesión.', 'danger')
                    return redirect(url_for('login'))  
                # Si la verificación es exitosa, guardar la sesión
                session['user_id'] = user_id  
                session['user_nombre'] = nombre  
                session['user_apellido'] = apellido 
                session['user_role'] = user_role 
                print(f"Usuario {session['user_nombre']} {session['user_apellido']} ha iniciado sesión con rol: {session['user_role']}")
                flash('Inicio de sesión exitoso.', 'success')
                return redirect(url_for('index'))  
            else:
                flash('Contraseña incorrecta.', 'danger')
        else:
            flash('Usuario no encontrado.', 'danger')

    return render_template('login.html')


@app.route('/perfil')
def perfil():
    # Verificar si el usuario está logueado
    if 'user_id' not in session:
        flash('Debes iniciar sesión para ver tu perfil.', 'danger')
        return redirect(url_for('login'))
    user_id = session['user_id']
    conn = sqlite3.connect('user.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, nombre, apellido, dni, mail, verificacion_2 FROM usuarios WHERE id = ?", (user_id,))
    usuario = cursor.fetchone()
    conn.close()

    if not usuario:
        flash('Usuario no encontrado.', 'danger')
        return redirect(url_for('index'))
    # Determinar el estado de validación
    if usuario[5] == 1:
        estado_validacion = "Verificado"
    elif usuario[5] == 0:
        estado_validacion = "Pendiente"
    elif usuario[5] == 3:
        estado_validacion = "Rechazado"
    return render_template('perfil.html', usuario=usuario, estado_validacion=estado_validacion)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    # Verifica la extensión del archivo
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS






@app.route('/validar_usuario_admin/<int:user_id>', methods=['POST'])
def validar_usuario_admin(user_id):
    conn = sqlite3.connect('user.db')
    cursor = conn.cursor()
    # Actualizar el estado de validación
    cursor.execute("""
        UPDATE usuarios 
        SET verificacion_2 = 1 
        WHERE id = ?
    """, (user_id,))
    conn.commit()
    conn.close()
    # Obtener los datos del usuario (nombre, correo)
    conn = sqlite3.connect('user.db')
    cursor = conn.cursor()
    cursor.execute("SELECT nombre, mail FROM usuarios WHERE id = ?", (user_id,))
    usuario = cursor.fetchone()
    conn.close()
    if usuario:
        nombre, user_mail = usuario
        # Enviar correo de validación exitosa
        msg = Message('Cuenta verificada con éxito',
                      recipients=[user_mail])
        msg.body = f'Hola {nombre},\n\nTu cuenta ha sido verificada exitosamente.\n\nSaludos,\nEl equipo de Basic Artz Estudio.'
        mail.send(msg)
        flash('Usuario validado exitosamente. Se ha enviado una notificación por correo.', 'success')
    else:
        flash('No se encontró al usuario.', 'danger')
    return redirect(url_for('ver_validaciones'))

@app.route('/rechazar_validacion/<int:user_id>', methods=['POST'])
def rechazar_validacion(user_id):
    conn = sqlite3.connect('user.db')
    cursor = conn.cursor()
    # Actualizar el estado de validación a rechazado
    cursor.execute("""
        UPDATE usuarios 
        SET verificacion_2 = 3 
        WHERE id = ?
    """, (user_id,))
    conn.commit()
    conn.close()
    # Obtener los datos del usuario (nombre, correo)
    conn = sqlite3.connect('user.db')
    cursor = conn.cursor()
    cursor.execute("SELECT nombre, mail FROM usuarios WHERE id = ?", (user_id,))
    usuario = cursor.fetchone()
    conn.close()
    if usuario:
        nombre, user_mail = usuario
        # Enviar correo de rechazo de validación
        msg = Message('Verificación de cuenta rechazada',
                      recipients=[user_mail])
        msg.body = f'Hola {nombre},\n\nLamentablemente, tu cuenta no ha sido verificada con exito. Por favor, revisa los requisitos y vuelve a intentarlo más tarde.\n\nSaludos,\nEl equipo de Basic Artz Estudio.'
        mail.send(msg)
        flash('Verificación rechazada. El usuario ha sido notificado por correo.', 'danger')
    else:
        flash('No se encontró al usuario.', 'danger')
    return redirect(url_for('ver_validaciones'))

@app.route('/carrito')
def carrito():
    if 'user_id' not in session:
        flash('Debes iniciar sesión para ver tu carrito.', 'danger')
        return redirect(url_for('login'))
    user_id = session['user_id']
    conn = sqlite3.connect('user.db')
    cursor = conn.cursor()
    cursor.execute("""
        SELECT productos.id, productos.nombre, productos.precio, carrito.cantidad
        FROM carrito
        JOIN productos ON carrito.producto_id = productos.id
        WHERE carrito.user_id = ?
    """, (user_id,))
    productos_carrito = cursor.fetchall()
    cursor.execute("SELECT DISTINCT categoria FROM productos")
    categorias = cursor.fetchall()
    conn.close()
    conn.close()
    total = sum(p[2] * p[3] for p in productos_carrito)  # Precio * cantidad
    return render_template('carrito.html', productos=productos_carrito, total=total, categorias= categorias)

@app.route('/eliminar_del_carrito/<int:producto_id>', methods=['POST'])
def eliminar_del_carrito(producto_id):
    if 'user_id' not in session:
        flash('Debes iniciar sesión.', 'danger')
        return redirect(url_for('login'))
    user_id = session['user_id']
    conn = sqlite3.connect('user.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM carrito WHERE user_id = ? AND producto_id = ?", (user_id, producto_id))
    conn.commit()
    conn.close()
    flash('Producto eliminado del carrito.', 'success')
    return redirect(url_for('carrito'))

@app.route('/categoria/<categoria>', methods=['GET'])
def mostrar_categoria(categoria):
    conn = sqlite3.connect('user.db')
    cursor = conn.cursor()    
    # Filtrar productos por categoría
    cursor.execute("SELECT * FROM productos WHERE categoria = ?", (categoria,))
    productos = cursor.fetchall()  
    cursor.execute("SELECT DISTINCT categoria FROM productos")
    categorias = cursor.fetchall()
    conn.close()
    conn.close()
    return render_template('categorias.html', categoria=categoria, productos=productos, categorias= categorias)

