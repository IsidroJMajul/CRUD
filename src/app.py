# Controlador

# from crypt import methods
import email
from email.mime import image
from optparse import Values
from flask import Flask, jsonify, redirect, url_for, send_from_directory, jsonify
import os

# RENDER: construccion de algo. Una vista
# REQUEST: recibe las peticiones del usuario
from flask import render_template, request

# DATETIME: importa librería para agregarle fecha a lor archivos adjuntos, y así evitar que se sobreescriban en caso que coincidan los nombres de los archivos
from datetime import datetime

from flaskext.mysql import MySQL

# DICCIONARIO: Para trabajar de forma asociativa. Para configurar el cursor.
from pymysql.cursors import DictCursor

# Importa las variables de entorno
from dotenv import load_dotenv
from flask_cors import CORS

from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
CORS(app)
mysql = MySQL()

NOMBRE_TABLA = 'empleados'

# Auth

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        conn = mysql.connect()
        cursor = conn.cursor(DictCursor)

        email= request.form['email']
        password= generate_password_hash (request.form['password'])

        sql = 'INSERT INTO usuarios (email, password) VALUES (%s, %s)'
        values = [email, password]

        cursor.execute(sql, values)

        conn.commit()

        return redirect(url_for('index'))
    else:
        return render_template('auth/register.html')

@app.route('')

# API CRUD

@app.route('/api/empleados')
def api_empleados():
    # JSON
    conn = mysql.connect()
    cursor = conn.cursor(DictCursor)

    cursor.execute('SELECT * FROM empleados')
    empleados = cursor.fetchall()

    # print (empleados)
    
    return jsonify (empleados)

# Web CRUD

# IMAGEN: ruta para que nos devuelva la imagen mediante un LINK
@app.route('/uploads/<path:imagen>')
def uploads(imagen):
    return send_from_directory(os.path.join('../uploads'), imagen)

# '/' es la RUTA PRINCIPAL
@app.route('/')
def index():
    conn = mysql.connect()
    cursor = conn.cursor(DictCursor)

    cursor.execute('SELECT * FROM empleados')
    empleados = cursor.fetchall()

    print (empleados)

    mensaje = 'Listado de empleados'
    return render_template('index.html', mensaje=mensaje, empleados=empleados)

@app.route('/create')
# Generalmente la FUNCION tiene el mismo nombre que la RUTA
def create():
    return render_template('create.html')

@app.route('/store', methods=['POST'])
def store():
    print(request.form)
    print(request.files)

    # return 'Ok'

    conn = mysql.connect()
    cursor = conn.cursor()

    nombre = request.form['nombre']
    correo = request.form['email']

    if request.files['imagen'].filename != '': 

        imagen = request.files['imagen']

        now = datetime.now()
        time = now.strftime('%Y%m%d%H%M%S')

        nombre_imagen = time + '_' + imagen.filename

        imagen.save('uploads/' + nombre_imagen)

        sql = 'INSERT INTO empleados (nombre, correo, imagen) VALUES (%s, %s, %s)'
        values = (nombre, correo, nombre_imagen)
    else:
        # BASE DE DATOS: para subir con campos vacíos, importante verificar que el campo permita NULL.
        sql = 'INSERT INTO empleados (nombre, correo) VALUES (%s, %s)'
        values = (nombre, correo)

    cursor.execute(sql, values)

# Importante agregar el COMMIT para que los datos insertados impacten en la BD
    conn.commit()

    # return 'OK' 
    return redirect(url_for('index'))

# UPDATE: ruta para editar/actualizar los datos
@app.route('/edit/<int:id>')
def edit(id):
    sql = 'SELECT * FROM empleados WHERE id = %s'
    # Con TUPLAS, no funciona cuando pasa un solo valor. Más fácil hacer una LISTA de un solo elemento
    values = [id]

    conn = mysql.connect()
    cursor = conn.cursor(DictCursor)

    cursor.execute(sql, values)
    empleado = cursor.fetchone()

    # print(empleados)

    return render_template('edit.html', empleado=empleado)

@app.route('/update', methods=['POST'])
def update():
    print(request.form)
    print(request.files)

    conn = mysql.connect()
    cursor = conn.cursor(DictCursor)

    id = request.form['id']
    nombre = request.form['nombre']
    correo = request.form['email']

    if request.files['imagen'].filename != '':
        sql = 'SELECT imagen FROM empleados WHERE id = %s'
        values = [id]

        cursor.execute(sql, values)
        empleado = cursor.fetchone()

        if empleado['imagen'] != None:
            # EXCEPCION al borrado: desde la carpeta de 'uploads'
            try:
                os.remove(os.path.join('uploads', empleado['imagen']))
            except:
                pass

        imagen = request.files['imagen']

        now = datetime.now()
        time = now.strftime('%Y%m%d%H%M%S')

        nombre_imagen = time + '_' + imagen.filename

        imagen.save('uploads/' + nombre_imagen)

        sql = 'UPDATE empleados SET nombre = %s, correo = %s, imagen = %s WHERE id = %s'
        values = [nombre, correo, nombre_imagen, id]
    else:
        # BASE DE DATOS: para subir con campos vacíos, importante verificar que el campo permita NULL.
        sql = 'UPDATE empleados SET nombre = %s, correo = %s WHERE id = %s'
        values = [nombre, correo, id]

    # sql = 'UPDATE empleados SET nombre = %s, correo = %s WHERE id = %s'
    # values = [nombre, correo, id]

    cursor.execute(sql, values)

    conn.commit()

    return redirect(url_for('index'))

@app.route('/delete/<int:id>')
def delete(id):
    conn = mysql.connect()
    cursor = conn.cursor(DictCursor)

    sql = 'SELECT imagen FROM empleados WHERE id = %s'
    values = [id]

    cursor.execute(sql, values)
    empleado = cursor.fetchone()

    if empleado['imagen'] != None:
        # EXCEPCION al borrado: desde la carpeta de 'uploads'
        try:
            os.remove(os.path.join('uploads', empleado['imagen']))
        except:
            pass

    sql = 'DELETE FROM empleados WHERE id = %s'
    values = [id]

    cursor.execute(sql, values)

    conn.commit()

    return redirect(url_for('index'))

# Siempre se agrega para ejecutar
# DEBUG: para modo desarrollo. Permite cambios en el momento.
if __name__ == '__main__':
    load_dotenv()

    app.config['MYSQL_DATABASE_HOST'] = os.getenv('MYSQL_HOST')
    app.config['MYSQL_DATABASE_USER'] = os.getenv('MYSQL_USER')
    app.config['MYSQL_DATABASE_PASSWORD'] = os.getenv('MYSQL_PASS')
    app.config['MYSQL_DATABASE_DB'] = os.getenv('MYSQL_DB')

    mysql.init_app(app)

    app.run(debug=True)