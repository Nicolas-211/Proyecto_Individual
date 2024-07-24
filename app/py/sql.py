from flask import Flask, render_template, session, request, url_for, redirect, send_file, flash, jsonify, json
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
from datetime import datetime
import base64
import uuid
import os
from flask_mail import Mail, Message
from json import JSONDecodeError


app = Flask(__name__, static_folder='static', static_url_path='/static')


# Change this to your secret key (can be anything, it's for extra protection)
app.secret_key = '123'
#app.config['MYSQL_HOST']='localhost'
#app.config['MYSQL_USER']='root'
#app.config['MYSQL_PASSWORD']='4]aUvoL4|j`f.8D<'
#app.config['MYSQL_DB']= 'proyecto_individual'


app.config['MYSQL_HOST']='35.238.85.190'
app.config['MYSQL_USER']='root'
app.config['MYSQL_PASSWORD']='X,V-@2Rd)"$MB;]9'
app.config['MYSQL_DB']= 'proyecto_individual'


mysql = MySQL(app)

# MAIL
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'juanperez.00a5@gmail.com'
app.config['MAIL_PASSWORD'] = 'nbbacdlwddjykxbi'
# Intialize Mail
mail = Mail(app)


# -----------------------FUNCIONES-----------------------------------------------------
def get_user_id_by_email(email):
    cur = mysql.connection.cursor()
    cur.execute('call usuario(%s)', (email,))
    user_id = cur.fetchone()
    cur.close()
    return user_id[0] if user_id else None


def get_tipo_ingreso(cur):
    cur.execute("call tipo_ingreso();")
    return [(item[0], item[1]) for item in cur.fetchall()]


def get_tipo_documento(cur):
    cur.execute("call tipo_documento();")
    return [(item[0], item[1]) for item in cur.fetchall()]


def get_origen(cur):
    cur.execute("call origen();")
    return [(item[0], item[1]) for item in cur.fetchall()]


def get_distribucion(cur):
    cur.execute("SELECT id_distribucion, NOMBRE_DISTRIBUCION FROM distribucion")
    return [(item[0], item[1]) for item in cur.fetchall()]


def insert_comentario_correspondencia(idtur, id_corres, fecha, contenido):
    cur = mysql.connection.cursor()
    cur.execute('INSERT INTO com_corres (id_tur,id_correspondencia,fecha_com_corres, comentario_corres) VALUES (%s,%s,%s, %s);',
                (idtur, id_corres, fecha, contenido))
    mysql.connection.commit()
    cur.close()


def insert_comentario_cheque(idtur, id_cheque, fecha_actual, contenido):
    cur = mysql.connection.cursor()
    cur.execute('INSERT INTO com_che(id_tur,id_cheque,fecha_com_che, comentario_che) VALUES (%s,%s,%s,%s);',
                (idtur, id_cheque, fecha_actual, contenido))
    mysql.connection.commit()
    cur.close()


def insert_correspondencia(cur, idtur, tipo_doc, orige, tipo_ingr, distri,
                           anio, numero_doc, fecha_formateada, antecedentes, obs,
                           nombre_archivo, rit, fecha_actual):
    cur.execute('INSERT INTO correspondencia (id_tur,id_tipo_doc,id_origen,'
                'tipo_ingreso_id_,id_distribucion,anio,numero_archivo,fecha_archivo,antecedentes,'
                'observaciones,archivo_adjunto_corres,rit,fecha_ingreso) '
                'VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);',
                (idtur, tipo_doc, orige, tipo_ingr, distri, anio, numero_doc,
                 fecha_formateada, antecedentes, obs, nombre_archivo, rit, fecha_actual))
    mysql.connection.commit()


def insert_cheque(cur, idtur, fecha_actual, serie, fecha_cheque, monto, origen, nombre_archivo, ritc, numero_oficio):
    cur.execute(
        'INSERT INTO cheque (id_tur, fecha_recepcion, serie, fecha_cheque, monto, origen, archivo_adjunto_che, ritc, numero_oficio)'
        'VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s);',
        (idtur, fecha_actual, serie, fecha_cheque, monto, origen, nombre_archivo, ritc, numero_oficio))
    mysql.connection.commit()


def obtener_resultados_correspondencia():
    cur = mysql.connection.cursor()
    cur.execute("call resultados_correspondencia();")
    resultados = cur.fetchall()

    return resultados


def obtener_resultados_cheque():
    cur = mysql.connection.cursor()

    cur.execute("call resultados_cheque();")
    resultados = cur.fetchall()
    return resultados


# Funciones para saber si ciertos datos existen en la base de datos en la tabla de cheque
def existe_num_oficio(numero_oficio):
    cur = mysql.connection.cursor()
    cur.execute('call existe_num_oficio(%s)', (numero_oficio,))
    resultados = cur.fetchone()
    if resultados:
        return True
    else:
        return False


def existe_serie(serie):
    cur = mysql.connection.cursor()
    cur.execute('call existe_serie(%s) ', (serie,))
    resultados = cur.fetchone()
    if resultados:
        return True
    else:
        return False


def existe_rit_cheque(ritc):
    cur = mysql.connection.cursor()
    cur.execute('call existe_rit_cheque(%s)', (ritc,))
    resultados = cur.fetchone()
    if resultados:
        return True
    else:
        return False


def existe_numero_documento_corres(numero_documento):
    cur = mysql.connection.cursor()
    cur.execute('call existe_numero_documento_corres(%s)', (numero_documento,))
    resultados = cur.fetchone()
    if resultados:
        return True
    else:
        return False


def existe_rit_corres(rit):
    cur = mysql.connection.cursor()
    cur.execute('call existe_rit_corres(%s)', (rit,))
    resultados = cur.fetchone()
    if resultados:
        return True
    else:
        return False


def correo_existe(correo):
    cur = mysql.connection.cursor()
    cur.execute("call correo_existe(%s)", (correo,))
    resultado = cur.fetchone()
    return resultado is not None


def insert_reset_pass(cur, token, id_usuario):
  cur.execute("insert into reset_pass (token,usuario_ID_USUARIO) values(%s,%s);",
              (token, id_usuario))
  mysql.connection.commit()


def is_valid_token(token):
    cur = mysql.connection.cursor()
    cur.execute("SELECT token FROM reset_pass WHERE token = %s", (token,))
    resultado = cur.fetchone()
    return resultado is not None


def update_password(token, new_pass):
    cur = mysql.connection.cursor()
    cur.execute(''' UPDATE usuario AS u INNER JOIN reset_pass AS rp ON u.id_usuario = rp.usuario_ID_USUARIO 
                    SET u.contrasena = %s WHERE rp.token = %s; ''', (new_pass, token))
    mysql.connection.commit()


def enviar_correo(correos_administradores, nombre_usuario):
    mensaje = f"{nombre_usuario} ha ingresado un nuevo cheque."
    msg = Message('Notificación de Cheque', sender='nbbacdlwddjykxbi',
                  recipients=correos_administradores)
    msg.body = mensaje
    mail.send(msg)

def enviar_correoCorres(correos_administradores, nombre_usuario):
    mensaje = f"{nombre_usuario} ha ingresado una nueva correspondencia."
    msg = Message('Notificación de Correspondencia', sender='nbbacdlwddjykxbi',
                  recipients=correos_administradores)
    msg.body = mensaje
    mail.send(msg)

def consultar_correspondencia(fecha):
    cur = mysql.connection.cursor()
    cur.execute('''SELECT tipo_documento.nombre_tipo_doc AS tipo_documento,
	    correspondencia.ID_CORRESPONDENCIA,
        com_corres.comentario_corres,
        origen.nombre_origen,
        tipo_ingreso.NOMBRE_TIPO_INGRESO,
        distribucion.NOMBRE_DISTRIBUCION,
        correspondencia.numero_archivo,
        correspondencia.antecedentes,
        correspondencia.observaciones,
        correspondencia.archivo_adjunto_corres,
        correspondencia.rit,
        correspondencia.fecha_ingreso
        FROM correspondencia
        inner JOIN tipo_documento ON correspondencia.id_tipo_doc = tipo_documento.id_tipo_doc
        LEFT JOIN com_corres ON correspondencia.ID_CORRESPONDENCIA = com_corres.ID_CORRESPONDENCIA
        LEFT JOIN origen ON correspondencia.id_origen = origen.id_origen
        LEFT JOIN tipo_ingreso ON correspondencia.tipo_ingreso_id_ = tipo_ingreso.tipo_ingreso_id_
        LEFT JOIN distribucion ON correspondencia.id_distribucion = distribucion.id_distribucion
        where correspondencia.fecha_ingreso =%s;''', (fecha,))
    resultados = cur.fetchall()
    return resultados


def consultar_cheque(fecha_formateada):
    cur = mysql.connection.cursor()

    cur.execute(''' SELECT cheque.ID_CHEQUE,
       com_che.comentario_che,
       cheque.FECHA_RECEPCION,
       cheque.SERIE,
       cheque.MONTO,
       cheque.ORIGEN,
       cheque.NUMERO_OFICIO,
       cheque.archivo_adjunto_che,
       cheque.ritc,
       cheque.FECHA_CHEQUE 
       FROM cheque
       LEFT JOIN com_che ON cheque.ID_CHEQUE = com_che.ID_CHEQUE
        where cheque.FECHA_RECEPCION =%s;''', (fecha_formateada,))
    resultados = cur.fetchall()
    return resultados


def insert_usuario(cur, nombres, apellidos, correo, password):
   cur.execute('insert into usuario values(null,%s,%s,%s,%s)',
               (nombres, apellidos, correo, password))
   mysql.connection.commit()


def consultar_correspondencia_informe(fecha):
    cur = mysql.connection.cursor()
    cur.execute('''SELECT tipo_documento.nombre_tipo_doc AS tipo_documento,
        com_corres.comentario_corres,
        origen.nombre_origen,
        tipo_ingreso.NOMBRE_TIPO_INGRESO,
        distribucion.NOMBRE_DISTRIBUCION,
        correspondencia.numero_archivo,
        correspondencia.antecedentes,
        correspondencia.observaciones,
        correspondencia.rit,
        correspondencia.fecha_ingreso
        FROM correspondencia
        inner JOIN tipo_documento ON correspondencia.id_tipo_doc = tipo_documento.id_tipo_doc
        LEFT JOIN com_corres ON correspondencia.ID_CORRESPONDENCIA = com_corres.ID_CORRESPONDENCIA
        LEFT JOIN origen ON correspondencia.id_origen = origen.id_origen
        LEFT JOIN tipo_ingreso ON correspondencia.tipo_ingreso_id_ = tipo_ingreso.tipo_ingreso_id_
        LEFT JOIN distribucion ON correspondencia.id_distribucion = distribucion.id_distribucion
        where correspondencia.fecha_ingreso =%s;''', (fecha,))
    resultados = cur.fetchall()
    return resultados


def procesar_datos(datos, eleccion):
    # Aquí puedes realizar cualquier procesamiento adicional necesario para tus datos
    # Devuelve cabeceras y datos para el ejemplo, ajusta según tus necesidades
    if eleccion == "correspondencia":
        return ["Tipo Ingreso", "Fecha de Ingreso", "Tipo Documento", "N° Documento", "RIT", "Antecedentes", "Origen", "Observaciones", "Distribución", "Adjunto", "Indicaciones"], datos


def grafico_barras():
    cur = mysql.connection.cursor()
    cur.execute('''SELECT
    CONCAT(SUBSTRING_INDEX(SUBSTRING_INDEX(fecha_recepcion, '/', 2), '/', -1)) AS mes,
    COUNT(*) AS cantidad
    FROM
    cheque
    WHERE
    fecha_recepcion LIKE '%/2024%'  -- Ajusta el año según tus necesidades
    GROUP BY
    mes
    ORDER BY
    mes;''')
    resultado = [(item[0], item[1]) for item in cur.fetchall()]
    return resultado

def grafico_pie():
    cur = mysql.connection.cursor()
    cur.execute('''select monto,count(*) as cantidad from cheque WHERE fecha_recepcion LIKE '%/2024%' GROUP BY monto ORDER BY monto;''')
    resultado = [(item[0], item[1]) for item in cur.fetchall()]
    return resultado


def grafico_barras_corres():
    cur = mysql.connection.cursor()
    cur.execute('''SELECT
    CONCAT(SUBSTRING_INDEX(SUBSTRING_INDEX(FECHA_INGRESO, '/', 2), '/', -1)) AS mes,
    COUNT(*) AS cantidad
    FROM
    correspondencia
    WHERE
    FECHA_INGRESO LIKE '%/2024%'  -- Ajusta el año según tus necesidades
    GROUP BY
    mes
    ORDER BY
    mes;''')
    resultado = [(item[0], item[1]) for item in cur.fetchall()]
    return resultado

def grafico_line_corres():
    cur = mysql.connection.cursor()
    cur.execute('''SELECT NOMBRE_ORIGEN, COUNT(*) AS cantidad FROM origen 
                   inner join correspondencia on correspondencia.ID_ORIGEN = origen.ID_ORIGEN
                   GROUP BY NOMBRE_ORIGEN ORDER BY NOMBRE_ORIGEN; ''')
    resultado = [(item[0], item[1]) for item in cur.fetchall()]
    return resultado

def grafico_pie_corres():
    cur = mysql.connection.cursor()
    cur.execute('''SELECT NOMBRE_DISTRIBUCION, COUNT(*) AS cantidad FROM distribucion 
                   inner join correspondencia on correspondencia.ID_DISTRIBUCION = distribucion.ID_DISTRIBUCION
                   GROUP BY NOMBRE_DISTRIBUCION ORDER BY NOMBRE_DISTRIBUCION; ''')
    resultado = [(item[0], item[1]) for item in cur.fetchall()]
    return resultado

def correo_del_usuario(nombre_usuario):
    cur = mysql.connection.cursor()
    cur.execute("SELECT correo FROM usuario WHERE CONCAT(nombre, ' ', apellido) = %s",(nombre_usuario,))
    resultado = [(item[0]) for item in cur.fetchall()]
    return resultado



def Update_Correo(cur, correo_confirmado, nombre_usuario):
    cur.execute("UPDATE usuario SET correo = %s WHERE CONCAT(nombre, ' ', apellido) = %s;",
                (correo_confirmado, nombre_usuario))
    mysql.connection.commit()


def Update_Contrasena(cur, pasword_confirmada, nombre_usuario):
    cur.execute("UPDATE usuario SET CONTRASENA = %s WHERE CONCAT(nombre, ' ', apellido) = %s;",
                (pasword_confirmada, nombre_usuario))
    mysql.connection.commit()