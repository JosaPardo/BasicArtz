from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, FileField, SelectField, SubmitField
from wtforms.validators import DataRequired
from flask_wtf.file import FileAllowed
import sqlite3

class ProductForm(FlaskForm):
    nombre = StringField('Nombre del Producto', validators=[DataRequired()])
    precio = FloatField('Precio', validators=[DataRequired()])
    imagen = FileField('Imagen', validators=[FileAllowed(['jpg', 'png', 'jpeg'], 'Solo imágenes permitidas')])
    categoria = SelectField('Categoría', choices=[], validators=[DataRequired()])
    submit = SubmitField('Agregar Producto')

    def cargar_categorias(self):
        conn = sqlite3.connect('user.db')
        cursor = conn.cursor()
        cursor.execute("SELECT nombre FROM categorias")
        categorias = cursor.fetchall()
        self.categoria.choices = [(categoria[0], categoria[0]) for categoria in categorias]
        conn.close()
