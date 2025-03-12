from flask import render_template, request, session, redirect, url_for, flash
from helpers import allowed_file
import sqlite3
from werkzeug.utils import secure_filename
from app import app, mail
from flask_mail import Message

@app.route('/subir_imagenes/<int:user_id>', methods=['GET', 'POST'])
def subir_imagenes(user_id):
    if request.method == 'POST':
        imagen1 = request.files['imagen1']
        imagen2 = request.files['imagen2']
        if imagen1 and allowed_file(imagen1.filename):
            imagen1_filename = secure_filename(f"imagen1_{user_id}.jpg")
            imagen1.save(f'static/uploads/{imagen1_filename}')
        else:
            flash('La imagen 1 no es válida.', 'danger')
            return redirect(request.url)
        if imagen2 and allowed_file(imagen2.filename):
            imagen2_filename = secure_filename(f"imagen2_{user_id}.jpg")
            imagen2.save(f'static/uploads/{imagen2_filename}')
        else:
            flash('La imagen 2 no es válida.', 'danger')
            return redirect(request.url)
        conn = sqlite3.connect('user.db')
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE usuarios 
            SET imagen1 = ?, imagen2 = ?, verificacion_2 = 0 
            WHERE id = ?
        """, (imagen1_filename, imagen2_filename, user_id))
        conn.commit()
        conn.close()
        flash('Imágenes subidas con éxito.', 'success')
        return redirect(url_for('perfil'))
    return render_template('subir_imagenes.html', user_id=user_id)
