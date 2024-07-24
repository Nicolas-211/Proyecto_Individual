from flask import Flask, render_template, session,request,url_for,redirect,send_file,flash,jsonify,make_response
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
from datetime import datetime
import uuid
import os
from flask_mail import Mail, Message
import secrets
from py.sql import get_user_id_by_email,get_tipo_ingreso,get_tipo_documento,get_origen,get_distribucion,insert_comentario_correspondencia,insert_comentario_cheque,existe_numero_documento_corres,existe_rit_corres,enviar_correo,consultar_correspondencia
from py.sql import insert_correspondencia,insert_cheque,obtener_resultados_correspondencia,obtener_resultados_cheque,existe_num_oficio,existe_serie,existe_rit_cheque,correo_existe,insert_reset_pass,is_valid_token,update_password,consultar_cheque
from py.sql import insert_usuario,grafico_barras,grafico_pie,enviar_correoCorres,grafico_barras_corres,grafico_line_corres,grafico_pie_corres,correo_del_usuario,Update_Correo,Update_Contrasena

app = Flask(__name__, static_folder='static', static_url_path='/static')

# Change this to your secret key (can be anything, it's for extra protection)
app.secret_key = '123'
app.config['MYSQL_HOST']='localhost'
app.config['MYSQL_USER']='root'
app.config['MYSQL_PASSWORD']='sE65]E7AV;-5'
app.config['MYSQL_DB']= 'proyecto_individual'


#app.config['MYSQL_HOST']='34.174.213.105'
#app.config['MYSQL_USER']='root'
#app.config['MYSQL_PASSWORD']='X,V-@2Rd)"$MB;]9'
#app.config['MYSQL_DB']= 'proyecto_individual'


mysql = MySQL(app)

#MAIL
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'juanperez.00a5@gmail.com'
app.config['MAIL_PASSWORD'] = 'nbbacdlwddjykxbi'
# Intialize Mail
mail = Mail(app)


# -----------------------------------------------------------------------------------------------------------------
# login
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        correo = request.form.get('correo')
        password = request.form.get('password')
        if 'password' in request.form and 'correo' in request.form and 'inciio' in request.form:
            if request.form['password'] and request.form['correo'] and request.form['inciio']:
                # Aquí puedes realizar acciones si los campos no están vacíos y contienen datos válidos
                cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                cursor.execute('SELECT * FROM usuario WHERE correo = %s AND contrasena = %s', (correo, password))
                account = cursor.fetchone()
                cur = mysql.connection.cursor()
                if account:
                    user_id = get_user_id_by_email(correo)
                    if user_id:
                        name = account['NOMBRE']
                        surname = account['APELLIDO']
                        full_name = name + ' ' + surname
                        session['nombre_usuario'] = full_name
                        session['user_id'] = user_id
                        session['loggedin'] = True
                        session['id'] = account['ID_USUARIO']       

                        cur.execute('SELECT id_tur FROM tribunal_usuario_rol WHERE id_usuario = %s AND FECHA_FIN IS NULL ', (user_id,))
                        result = cur.fetchone()
                        id_tur = result[0]
                        print(id_tur)
                        session['id_tur']=id_tur

                        cur.execute('SELECT ID_TRIBUNALES FROM tribunal_usuario_rol WHERE id_usuario = %s AND FECHA_FIN IS NULL ', (user_id,))
        
                        id_tribunales = [item[0] for item in cur.fetchall()]
                        session['id_tribunales'] = id_tribunales

                        cur.execute('SELECT id_rol FROM tribunal_usuario_rol WHERE ID_TUR = %s', (id_tur,))
                        admin = [item[0] for item in cur.fetchall()]

                        

                        session['admin'] = admin
                        
                        return redirect(url_for('home',admin=admin))
                else:
                    # Account doesnt exist or username/password incorrect
                    flash('Error en el usuario o contraseña!')
            elif not password or not correo:
                flash('Existen campos sin rellenar!')
                
    return render_template('login.html')



# -----------------------------------------------------------------------------------------------------------------
# registro usuario
@app.route('/registro',methods=['GET', 'POST'])
def registro():
    correo = request.form.get('correo')
    password = request.form.get('password')
    if request.method == 'POST' and 'password' and 'correo' in request.form:
        
        tribunales = request.form.get('tribunales')
        nombres = request.form.get('nombres')
        apellidos = request.form.get('apellidos')
        fecha_actual = datetime.now().strftime('%d/%m/%Y')
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM usuario WHERE correo = %s', (correo,))
        account = cursor.fetchone()
        cur = mysql.connection.cursor()

        if account:
            flash("Correo ya se encuentra registrado")
        elif not re.match(r'^[^@]+@pjud\.cl$', correo):
            flash("Correo invalido")
        elif not password or not correo or not nombres or not apellidos:
            flash('Existen campos sin rellenar!')
        elif not password or len(password) < 8:
            flash('La contraseña debe tener al menos 8 caracteres.')
        elif not any(char.isupper() for char in password):
            flash('La contraseña debe contener al menos una letra mayúscula.')
        elif sum(char.isdigit() for char in password) < 2:
            flash('La contraseña debe contener al menos dos números.')
        else:
                
                # Account doesnt exists and the form data is valid, now insert new account into accounts table
                insert_usuario(cur,nombres, apellidos,correo,password)
            
                cur.execute('SELECT id_usuario FROM usuario ORDER BY id_usuario DESC LIMIT 1;')
                id_usuario = [item[0] for item in cur.fetchall()]

                cur.execute('SELECT id_tur FROM tribunal_usuario_rol ORDER BY id_tur DESC LIMIT 1;')
                id_tur = [item[0] for item in cur.fetchall()]
                
                if id_tur == '0':
                   
                    cursor.execute('insert into tribunal_usuario_rol values(1,%s,%s,%s,%s,"")', (1,id_usuario,tribunales,fecha_actual))
                    mysql.connection.commit()
                else:
                    
                    cur.execute('SELECT id_tur FROM tribunal_usuario_rol ORDER BY id_tur DESC LIMIT 1;')
                    id_turr = [item[0] for item in cur.fetchall()]
                    idtur = id_turr[0] + 1
                    
                    cursor.execute('insert into tribunal_usuario_rol values(%s,%s,%s,%s,%s,"")', (idtur,2,id_usuario,tribunales,fecha_actual))
                    mysql.connection.commit()

                flash('Registrado correctamente!', 'success')
            
    cur = mysql.connection.cursor()
    cur.execute("select ID_TRIBUNALES,NOMBRE_TRIBUNALES from tribunales")
    tribunales = [(item[0], item[1]) for item in cur.fetchall()]
 
    return render_template('paginas/registro.html',tribunales=tribunales)


# -----------------------------------------------------------------------------------------------------------------
# Home
@app.route('/home')
def home():
    if 'loggedin' in session and session['loggedin']:
        
            admin = session['admin']
            nombre_usuario = session['nombre_usuario']
            cur = mysql.connection.cursor()
            
            cur.execute('call rol(%s)', (admin,))
            nombre_rol = [item[0] for item in cur.fetchall()]

            usuario = nombre_rol[0]

            return render_template('home.html',admin=admin,nombre_usuario=nombre_usuario,usuario=usuario) 
    else:
        # Usuario no ha iniciado sesión, redirigir al inicio de sesión
        return redirect(url_for('logout'))

# -----------------------------------------------------------------------------------------------------------------
# ingreso de correspondencia
@app.route('/ingreso/correspondencia', methods=['GET', 'POST'])
def ingresoCorrespondencia():
    if 'loggedin' in session and session['loggedin']:
        idtur = session.get('id_tur')
        admin = session.get('admin')
        fecha_actual = datetime.now().strftime('%d/%m/%Y')
        componentes_fecha = fecha_actual.split('/')
        año_actual = componentes_fecha[2]   
        cur = mysql.connection.cursor()
        idtribunales = session.get('id_tribunales')
        nombre_usuario = session['nombre_usuario']
        if request.method == 'POST':
            anio = año_actual
            tipo_ingr = request.form.get('tipo_ingreso')
            tipo_doc = request.form.get('tipo_documento')
            numero_doc = request.form.get('numero_doc')
            fecha_doc = request.form.get('fecha_doc')
            rit = request.form.get('rit')
            antecedentes = request.form.get('antecedentes')
            orige = request.form.get('origen')
            distri = request.form.get('distribucion')
            obs = request.form.get('obs')      
            archivo = request.files['pdf']
            nombre_archivo = str(uuid.uuid4()) + '.pdf'
            archivo.save(os.path.join('archivo', nombre_archivo))


            existe_numero_documento = existe_numero_documento_corres(numero_doc)
            existe_rit = existe_rit_corres(rit)
            if existe_rit or existe_numero_documento:
                flash('Correspondencia ya registrada en la BD!')
            else:    
                if admin[0] == 1:
                    indicaciones = request.form.get('indicaciones')
                    insert_correspondencia(cur, idtur, tipo_doc, orige, tipo_ingr, distri,
                                      anio, numero_doc, fecha_doc, antecedentes, obs,
                                      nombre_archivo, rit, fecha_actual)
                
                    cur.execute('SELECT ID_CORRESPONDENCIA FROM correspondencia where id_tur=%s ORDER BY ID_CORRESPONDENCIA DESC LIMIT 1;',(idtur))
                    id_corres = [item[0] for item in cur.fetchall()]
                    insert_comentario_correspondencia(idtur,id_corres,fecha_actual, indicaciones)
                    flash('Correspondencia ingresada correctamente', 'success')
                else:
                    insert_correspondencia(cur, idtur, tipo_doc, orige, tipo_ingr, distri,
                                      anio, numero_doc, fecha_doc, antecedentes, obs,
                                      nombre_archivo, rit, fecha_actual)
                    cur.execute('select correo from usuario inner join tribunal_usuario_rol on usuario.id_usuario = tribunal_usuario_rol.id_usuario inner join rol on tribunal_usuario_rol.ID_ROL = rol.id_rol where rol.id_rol=1 and FECHA_FIN IS NULL and id_tribunales=%s',(idtribunales))
                    correos_administradores = [item[0] for item in cur.fetchall()]
                    enviar_correoCorres(correos_administradores,nombre_usuario)
                    flash('Correspondencia ingresada correctamente', 'success')

        tipo_ingreso = get_tipo_ingreso(cur)
        tipo_documento = get_tipo_documento(cur)
        origen = get_origen(cur)
        distribucion = get_distribucion(cur)
        nombre_usuario = session['nombre_usuario']

        cur.execute('call rol(%s)', (admin,))
        nombre_rol = [item[0] for item in cur.fetchall()]

        usuario = nombre_rol[0]
        return render_template('paginas/ingresos/Correspondencia.html', año_actual=año_actual,tipo_ingreso=tipo_ingreso, tipo_documento=tipo_documento, origen=origen,
                               distribucion=distribucion,admin=admin,nombre_usuario=nombre_usuario,usuario=usuario)
    else:
        return redirect(url_for('logout')) 

# -----------------------------------------------------------------------------------------------------------------
# ingreso de cheque
@app.route("/ingreso/cheque", methods=['GET', 'POST'])
def ingresoCheque():
    if 'loggedin' in session and session['loggedin']:

        idtur = session.get('id_tur')
        admin = session.get('admin')
        fecha_actual = datetime.now().strftime('%d/%m/%Y')
        cur = mysql.connection.cursor()
        nombre_usuario = session['nombre_usuario']
        idtribunales = session.get('id_tribunales')

        if request.method == 'POST':
            
            numero_oficio = request.form.get('numero_oficio')
            fecha_cheque = request.form.get('fecha_doc')
            origen = request.form.get('Origen')
            serie = request.form.get('Serie')
            monto = request.form.get('Monto')
            if int(monto) >= 0:
                monto_num = float(monto)  # Convertir la cadena a número (puede ser int o float según tus necesidades)
                monto_formateado = "{:,.0f}".format(monto_num)
                ritc = request.form.get('ritc')
                archivo = request.files['pdf']
                nombre_archivo = str(uuid.uuid4()) + '.pdf'
                archivo.save(os.path.join('archivo', nombre_archivo))
                existe_numero_oficio = existe_num_oficio(numero_oficio)
                existe_Serie = existe_serie(serie)
                existe_ritc = existe_rit_cheque(ritc)
                
                if existe_numero_oficio or existe_Serie or existe_ritc :
                    flash('Cheque ya registrado en la BD!')
                else:
                    if admin[0] == 1:
                        indicaciones = request.form.get('indicaciones')
                        insert_cheque(cur, idtur,fecha_actual,serie,fecha_cheque,monto_formateado,origen,nombre_archivo,ritc,numero_oficio) 
                    
                        cur.execute('SELECT id_cheque FROM cheque where id_tur=%s ORDER BY id_cheque DESC LIMIT 1;',(idtur))
                        id_cheque = [item[0] for item in cur.fetchall()]
                        insert_comentario_cheque(idtur,id_cheque,fecha_actual, indicaciones)
                        flash('Cheque ingresado correctamente', 'success')
                    else:
                        insert_cheque(cur, idtur,fecha_actual,serie,fecha_cheque,monto_formateado,origen,nombre_archivo,ritc,numero_oficio) 
                        #envio correo a los admin avisando que se ingreso una nuvo cheque
                        cur.execute('select correo from usuario inner join tribunal_usuario_rol on usuario.id_usuario = tribunal_usuario_rol.id_usuario inner join rol on tribunal_usuario_rol.ID_ROL = rol.id_rol where rol.id_rol=1 and FECHA_FIN IS NULL and id_tribunales=%s',(idtribunales))
                        correos_administradores = [item[0] for item in cur.fetchall()]
                        enviar_correo(correos_administradores,nombre_usuario)
                        flash('Cheque ingresado correctamente', 'success')
            else:
                flash('numero de documento invalido')
        cur.execute('call rol(%s)', (admin,))
        nombre_rol = [item[0] for item in cur.fetchall()]

        usuario = nombre_rol[0]
        return render_template("paginas/ingresos/cheque.html",admin=admin,nombre_usuario=nombre_usuario,usuario=usuario)
    else:
        return redirect(url_for('logout')) 

    

# -----------------------------------------------------------------------------------------------------------------
# ver ingresos
@app.route('/ver', methods=['GET'])
def ver():
    if 'loggedin' in session and session['loggedin']:
        opcion = request.args.get('opcion')
        admin = session['admin']
        nombre_usuario = session['nombre_usuario']
        cur = mysql.connection.cursor()
        cur.execute('call rol(%s)', (admin,))
        nombre_rol = [item[0] for item in cur.fetchall()]

        usuario = nombre_rol[0]
        if opcion == 'correspondencia':
            # Lógica para mostrar correspondencia
            try:
                tipo_documento = get_tipo_documento(cur)
                tipo_ingreso = get_tipo_ingreso(cur)
                origen = get_origen(cur)
                distribucion = get_distribucion(cur)
                # Obtener los resultados cifrados
                resultados = obtener_resultados_correspondencia()

            # Descifrar los resultados
           
                return render_template('paginas/veringreso/correspondencia.html', admin=admin,nombre_usuario=nombre_usuario,usuario=usuario,tipo_documento=tipo_documento,tipo_ingreso=tipo_ingreso,origen=origen,distribucion=distribucion,resultados=resultados)
            except Exception as e:
             error_message = f"Error al obtener los resultados: {e}"
             return render_template('paginas/errores/error.html', error_message=error_message)
        elif opcion == 'cheque':
            # Lógica para mostrar cheques
            try:
            
                resultados = obtener_resultados_cheque()
            

                print(resultados)
                return render_template('paginas/veringreso/cheque.html', admin=admin,nombre_usuario=nombre_usuario,usuario=usuario, resultados=resultados)
            except Exception as e:
                error_message = f"Error al obtener los resultados: {e}"
                return render_template('paginas/errores/error.html', error_message=error_message)
        else:
            # Manejar opción no válida
            return render_template('paginas/errores/error.html', error_message='Opción no válida')
    else:
        return redirect(url_for('logout'))
    

# -----------------------------------------------------------------------------------------------------------------
# asignacion rol
@app.route('/rol',methods=['GET', 'POST'])
def rol():
    if 'loggedin' in session and session['loggedin']:
        cur = mysql.connection.cursor()
        nombre_usuario = session['nombre_usuario']
        
        if request.method == 'POST':
            id_usuario = request.form.get('usuario')
            print(id_usuario)
            rol = request.form.get('roles')
            tribunal = request.form.get('tribunales')
            fecha_actual = datetime.now().strftime('%d/%m/%Y')
            cur.execute('SELECT id_tur FROM tribunal_usuario_rol ORDER BY id_tur DESC LIMIT 1;')
            id_tur = [item[0] for item in cur.fetchall()]
            if id_tur == '0':
                
                print("agregar alguien")

            else:
                    cur.execute('UPDATE tribunal_usuario_rol SET fecha_fin = %s where id_usuario = %s ', (fecha_actual,id_usuario))
                    mysql.connection.commit() 

                    cur.execute('SELECT id_tur FROM tribunal_usuario_rol ORDER BY id_tur DESC LIMIT 1;')
                    id_turr = [item[0] for item in cur.fetchall()]
                    idtur = id_turr[0] + 1

                    cur.execute('insert into tribunal_usuario_rol values(%s,%s,%s,%s,%s,"")', (idtur,rol,id_usuario,tribunal,fecha_actual))
                    mysql.connection.commit()

                    flash("Se cambio el rol con exito")
        idtur = session.get('id_tur')
        cur.execute("select ID_TRIBUNALES,NOMBRE_TRIBUNALES from tribunales")
        tribunales = [(item[0], item[1]) for item in cur.fetchall()]

        cur.execute("select id_usuario, concat(nombre, ' ', apellido) as nombre_completo from  usuario")
        usuarios = [(item[0], item[1]) for item in cur.fetchall()]
        
        cur.execute("select id_rol,nombre_rol from rol")
        roles = [(item[0], item[1]) for item in cur.fetchall()]

        cur.execute('SELECT id_rol FROM tribunal_usuario_rol WHERE ID_TUR = %s', (idtur,))
        admin = [item[0] for item in cur.fetchall()]

        cur.execute('call rol(%s)', (admin,))
        nombre_rol = [item[0] for item in cur.fetchall()]

        usuario = nombre_rol[0]
        return render_template('rol.html',tribunales=tribunales,usuario=usuario,roles=roles,admin=admin,nombre_usuario = nombre_usuario,usuarios=usuarios)
    else:
        return redirect(url_for('logout'))

# -----------------------------------------------------------------------------------------------------------------
#Indicaciones
@app.route('/indicaciones', methods=['POST'])
def Indicaciones():    
    # Simula la detección de una infracción (puedes personalizar esto según tus necesidades)
    flash_message = 'Indicaciones'
    infraccion = True
    dato = request.form.get('dato')
    
    response_data = {
        'infraccion': infraccion,
        'flash_message': flash_message,
        'dato':dato
    }
    
    return jsonify(response_data)


# -----------------------------------------------------------------------------------------------------------------
#Editar corres
@app.route('/editarCorres', methods=['POST'])
def editarCorres():  
    # Simula la detección de una infracción (puedes personalizar esto según tus necesidades)
    flash_message = 'Editar'
    infraccion = True
    dato = request.form.get('dato')
    fechaingreso = request.form.get('fechaingreso')
    documento = request.form.get('documento')
    rit = request.form.get('rit')
    origen = request.form.get('origen')
    distribución = request.form.get('distribución')
    print(documento)
    
    response_data = {
        'infraccion': infraccion,
        'flash_message': flash_message,
        'dato':dato,
        'fechaingreso':fechaingreso,
        'documento':documento,
        'rit':rit,
        'origen':origen,
        'distribución':distribución
    }
    
    return jsonify(response_data)

# -----------------------------------------------------------------------------------------------------------------
# ruta y funcion para guardar las indicaciones
@app.route('/guardar_comentario', methods=['POST'])
def guardar_comentario():
    if request.method == 'POST':
        idcorres = request.form.get('ingreso_id')
        idcheque = request.form.get('cheque_id')
        indicaciones = request.form.get('comentario')
        fecha_actual = datetime.now().strftime('%d/%m/%Y')
        idtur = session.get('id_tur')
        cur = mysql.connection.cursor()
        if idcorres:
            # logica para guardar una indicaciones correspondiente a la correspondencia
            insert_comentario_correspondencia(idtur, idcorres, fecha_actual, indicaciones)
            return redirect(url_for('ver', opcion='correspondencia'))
        elif idcheque:
            # logica para guardar una indicaciones correspondiente al cheque
            insert_comentario_cheque(idtur, idcheque, fecha_actual, indicaciones)
            return redirect(url_for('ver', opcion='cheque'))
    
    # Devuelve una respuesta válida en caso de que no se cumplan las condiciones anteriores
    return "Solicitud POST incorrecta"
            
# -----------------------------------------------------------------------------------------------------------------
# ruta y funcion para descargar el archivo pdf
@app.route('/descargar_pdf/<string:filename>')
def descargar_pdf(filename):
    # Obtener la ruta completa del archivo en el servidor
    archivo_ruta = os.path.join('archivo', filename)

    # Enviar el archivo como respuesta
    return send_file(archivo_ruta, as_attachment=True)

# -----------------------------------------------------------------------------------------------------------------
# ruta y funcion para restablecer contraseña
@app.route('/restablecer_contrasena',methods=['GET', 'POST'])
def restablecer_contrasena():
    if request.method == 'POST':
        correo = request.form['correo']
        if correo_existe(correo):
            # Si existe, genera un token único y envía un correo
            token = secrets.token_urlsafe(32)  # Genera un token seguro

            #buscar id_usuario con el correo
            cur = mysql.connection.cursor()
            cur.execute("select id_usuario from usuario where correo= %s ;",(correo,))
            idusuario = cur.fetchall()
        
            #guardar el token en tu base de datos junto con el correo electrónico del usuario
            insert_reset_pass(cur,token,idusuario)
            flash('Se ha enviado un correo con las instrucciones para restablecer la contraseña.')

            # Envía el correo
            msg = Message('Restablecer Contraseña', sender='dstuhccclduvvocv', recipients=[correo])
            msg.body = f'Para restablecer tu contraseña, haz clic en el siguiente enlace: {url_for("reset_password", token=token, _external=True)}'
            mail.send(msg)
            return render_template('paginas/restablecer_contrasena/reset_pass_request.html')
        else:
            # El correo no existe en la base de datos, muestra un mensaje de error.
            flash('El correo electrónico no existe en nuestra base de datos.', 'error')
    return render_template ("paginas/restablecer_contrasena/reset_pass_request.html")

@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if not is_valid_token(token):
        flash('El token de restablecimiento de contraseña no es válido.', 'error')
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        new_password = request.form['new_password']
        confirm_password = request.form['confirm_password']
        if confirm_password == new_password:
            if not new_password or len(new_password) < 8:
                flash('La contraseña debe tener al menos 8 caracteres.')
            elif not any(char.isupper() for char in new_password):
                flash('La contraseña debe contener al menos una letra mayúscula.')
            elif sum(char.isdigit() for char in new_password) < 2:
                flash('La contraseña debe contener al menos dos números.')
            else:
                # Realiza la lógica para actualizar la contraseña del usuario
                update_password(token, new_password)
                flash('Contraseña restablecida con éxito. Puedes iniciar sesión con tu nueva contraseña.')
        

    return render_template('paginas/restablecer_contrasena/reset_password.html', token=token)

# -----------------------------------------------------------------------------------------------------------------
#informe correspondencia
@app.route('/InformeCorrespondencia', methods=['GET', 'POST'])
def informe():
    if 'loggedin' in session and session['loggedin']:
        admin = session['admin']
        nombre_usuario = session['nombre_usuario']
        cur = mysql.connection.cursor()
        cur.execute('call rol(%s)', (admin,))
        nombre_rol = [item[0] for item in cur.fetchall()]

        usuario = nombre_rol[0]
        tipo_documento = get_tipo_documento(cur)
        tipo_ingreso = get_tipo_ingreso(cur)
        origen = get_origen(cur)
        distribucion = get_distribucion(cur)
        # Obtener los resultados cifrados
        resultados = obtener_resultados_correspondencia()
        return render_template('paginas/informe/Correspondencia-informe.html', admin=admin,nombre_usuario=nombre_usuario,usuario=usuario,tipo_documento=tipo_documento,tipo_ingreso=tipo_ingreso,origen=origen,distribucion=distribucion,resultados=resultados)
    else:
        return redirect(url_for('logout')) 

# -----------------------------------------------------------------------------------------------------------------
#Informe Cheque
@app.route('/InformeCheque', methods=['GET', 'POST'])
def InformeCheque():
    if 'loggedin' in session and session['loggedin']:
        admin = session['admin']
        nombre_usuario = session['nombre_usuario']
        cur = mysql.connection.cursor()
        cur.execute('call rol(%s)', (admin,))
        nombre_rol = [item[0] for item in cur.fetchall()]

        usuario = nombre_rol[0]
        resultados = obtener_resultados_cheque()
        return render_template('paginas/informe/cheque-informe.html', admin=admin,nombre_usuario=nombre_usuario,usuario=usuario,resultados=resultados)
    else:
        return redirect(url_for('logout')) 

# -----------------------------------------------------------------------------------------------------------------
#Graficos Cheque
@app.route('/Graficoscheque', methods=['GET', 'POST'])
def Graficoscheque():
    if 'loggedin' in session and session['loggedin']:
        admin = session['admin']
        nombre_usuario = session['nombre_usuario']
        cur = mysql.connection.cursor()
        cur.execute('call rol(%s)', (admin,))
        nombre_rol = [item[0] for item in cur.fetchall()]

        #grafico line 
        cur = mysql.connection.cursor()
        cur.execute("SELECT origen, COUNT(*) AS cantidad FROM cheque GROUP BY origen ORDER BY origen")
        datos = cur.fetchall()
        cur.close()

        labels = [row[0] for row in datos]  # Extraer los orígenes
        values = [row[1] for row in datos]  # Extraer las cantidades
    

        #grafico de barras
        resultados = grafico_barras()
        nombres_meses = {
            '01': 'Enero',
            '02': 'Febrero',
            '03': 'Marzo',
            '04': 'Abril',
            '05': 'Mayo',
            '06': 'Junio',
            '07': 'Julio',
            '08': 'Agosto',
            '09': 'Septiembre',
            '10': 'Octubre',
            '11': 'Noviembre',
            '12': 'Diciembre'
        }
        labels2 = [nombres_meses.get(str(row[0]), 'Desconocido') for row in resultados]
        values2 = [row[1] for row in resultados]


        
        #doughnut
        resultados2 = grafico_pie()
        labels3 = [row[0] for row in resultados2]  # Extraer los monto
        values3 = [row[1] for row in resultados2]  # Extraer las cantidades

        print(labels3)
        print(values3)

        usuario = nombre_rol[0]
        return render_template('paginas/estadistica/cheque-esta.html', labels=labels, values=values,labels2=labels2, values2=values2,labels3=labels3, values3=values3,admin=admin,nombre_usuario=nombre_usuario,usuario=usuario)
    else:
        return redirect(url_for('logout')) 
# -----------------------------------------------------------------------------------------------------------------
#Graficos Correspondencia
@app.route('/GraficosCorrespondencia', methods=['GET', 'POST'])
def graficosCorrespondencia():
    if 'loggedin' in session and session['loggedin']:
        admin = session['admin']
        nombre_usuario = session['nombre_usuario']
        cur = mysql.connection.cursor()
        cur.execute('call rol(%s)', (admin,))
        nombre_rol = [item[0] for item in cur.fetchall()]
        usuario = nombre_rol[0]

        datos = grafico_line_corres()
        labels = [row[0] for row in datos]  # Extraer los orígenes
        values = [row[1] for row in datos]  # Extraer las cantidades

        #grafico de barras
        resultados = grafico_barras_corres()
        nombres_meses = {
            '01': 'Enero',
            '02': 'Febrero',
            '03': 'Marzo',
            '04': 'Abril',
            '05': 'Mayo',
            '06': 'Junio',
            '07': 'Julio',
            '08': 'Agosto',
            '09': 'Septiembre',
            '10': 'Octubre',
            '11': 'Noviembre',
            '12': 'Diciembre'
        }
        labels2 = [nombres_meses.get(str(row[0]), 'Desconocido') for row in resultados]
        values2 = [row[1] for row in resultados]
        
        #pie
        resultados2 = grafico_pie_corres()
        labels3 = [row[0] for row in resultados2]  # Extraer los monto
        values3 = [row[1] for row in resultados2]  # Extraer las cantidades


        return render_template('paginas/estadistica/correspondencia-esta.html',labels=labels, values=values,labels2=labels2, values2=values2,labels3=labels3, values3=values3,admin=admin,nombre_usuario=nombre_usuario,usuario=usuario)
    else:
        return redirect(url_for('logout')) 



# -----------------------------------------------------------------------------------------------------------------
@app.route('/consultar_datos', methods=['POST'])
def consultar_datos():
    fecha = request.form['fecha']
    eleccion = request.form['eleccion']
    fecha_datetime = datetime.strptime(fecha, "%Y-%m-%d")
    fecha_formateada = fecha_datetime.strftime("%d/%m/%Y")
    if eleccion== "cheque":
        resultados = consultar_cheque(fecha_formateada)

        # Ordena los resultados en el orden deseado (cambia los índices según sea necesario)
        resultados_ordenados = [(
            row[2],  # Fecha Recepcion
            row[9], # Fecha de Cheque
            row[6],  # N° OFICIO
            row[5],  # ORIGEN
            row[3], # Serie
            row[4],  # MONTO
            row[8],  # RIT
            row[7],  # Adjunto
            row[1]   # Indicaciones
        ) for row in resultados]
        return jsonify(resultados_ordenados)
    else:
        
        # Obtén los resultados de la base de datos
        resultados = consultar_correspondencia(fecha_formateada)

        # Ordena los resultados en el orden deseado (cambia los índices según sea necesario)
        resultados_ordenados = [(
            row[4],  # Tipo Ingreso
            row[11], # Fecha de Ingreso
            row[0],  # Tipo Documento
            row[6],  # N° Documento
            row[10], # RIT
            row[7],  # Antecedentes
            row[3],  # Origen
            row[8],  # Observaciones
            row[5],  # Distribución
            row[9],  # Adjunto
            row[2]   # Indicaciones
        ) for row in resultados]
        return jsonify(resultados_ordenados)


@app.route('/test', methods=['GET'])
def test():
    return render_template('test.html')

# -----------------------------------------------------------------------------------------------------------------
# Profile
@app.route('/Profile', methods=['GET','POST'])
def Profile():
    if 'loggedin' in session and session['loggedin']:
        admin = session['admin']
        nombre_usuario = session['nombre_usuario']
        cur = mysql.connection.cursor()
        cur.execute('call rol(%s)', (admin,))
        nombre_rol = [item[0] for item in cur.fetchall()]
        correo = correo_del_usuario(nombre_usuario)
        correo_ususario = correo[0]
        usuario = nombre_rol[0]
        return render_template('paginas/User_Profile/profile.html',admin=admin,nombre_usuario=nombre_usuario,usuario=usuario,correo_ususario=correo_ususario)
    else:
        return redirect(url_for('logout')) 

# -----------------------------------------------------------------------------------------------------------------
# Actualizar correo
@app.route('/cambiarCorreo', methods=['POST'])
def cambiarCorreo():
    admin = session['admin']
    nombre_usuario = session['nombre_usuario']
    cur = mysql.connection.cursor()
    cur.execute('call rol(%s)', (admin,))
    nombre_rol = [item[0] for item in cur.fetchall()]
    correo_user = correo_del_usuario(nombre_usuario)
    correo_ususario = correo_user[0]
    usuario = nombre_rol[0]
    if request.method == 'POST':
        correo_confirmado = request.form.get('confirm_correo')
        correo = request.form.get('newcorreo')
        if correo==correo_confirmado:
            if correo_existe(correo_confirmado):
                flash('Este correo ya existe!',)
            elif not re.match(r'^[^@]+@pjud\.cl$', correo_confirmado):
                flash("Correo invalido")
            else:  
                Update_Correo(cur,correo_confirmado,nombre_usuario) 
                flash('Correo Cambiado correctamente.', 'success')
                return render_template('paginas/User_Profile/profile.html',admin=admin,nombre_usuario=nombre_usuario,usuario=usuario,correo_ususario=correo_ususario)
        else:
            flash('Los campos no son iguales. Por favor, verifíquelos.!')
    return render_template('paginas/User_Profile/profile.html',admin=admin,nombre_usuario=nombre_usuario,usuario=usuario,correo_ususario=correo_ususario)



# -----------------------------------------------------------------------------------------------------------------
# Actualizar contraseña
@app.route('/CambiarContra', methods=['POST'])
def CambiarContra():
    admin = session['admin']
    nombre_usuario = session['nombre_usuario']
    cur = mysql.connection.cursor()
    cur.execute('call rol(%s)', (admin,))
    nombre_rol = [item[0] for item in cur.fetchall()]
    correo_user = correo_del_usuario(nombre_usuario)
    correo_ususario = correo_user[0]
    usuario = nombre_rol[0]
    if request.method == 'POST':
            pasword = request.form.get('newcontraseña')
            pasword_confirmada = request.form.get('confirm_password')
            if pasword==pasword_confirmada:
                if not pasword or len(pasword) < 8:
                    flash('La contraseña debe tener al menos 8 caracteres.')
                elif not any(char.isupper() for char in pasword):
                    flash('La contraseña debe contener al menos una letra mayúscula.')
                elif sum(char.isdigit() for char in pasword) < 2:
                    flash('La contraseña debe contener al menos dos números.')
                else:
                    Update_Contrasena(cur,pasword_confirmada,nombre_usuario) 
                    flash('Contraseña Cambiada Con Exito.', 'success')
                    return render_template('paginas/User_Profile/profile.html',admin=admin,nombre_usuario=nombre_usuario,usuario=usuario,correo_ususario=correo_ususario)
            else:
                flash('Los campos no son iguales. Por favor, verifíquelos.!')
    return render_template('paginas/User_Profile/profile.html',admin=admin,nombre_usuario=nombre_usuario,usuario=usuario,correo_ususario=correo_ususario)
               
# -----------------------------------------------------------------------------------------------------------------
# cierre 
@app.route('/logout', methods=['POST'])
def logout():  
    # Simula la detección de una infracción (puedes personalizar esto según tus necesidades)
    flash_message = '¿Estás seguro de que deseas cerrar sesión?'
    infraccion = True
    
    response_data = {
        'infraccion': infraccion,
        'flash_message': flash_message
    }
    
    return jsonify(response_data)


@app.route('/cerrarsesion', methods=['GET'])
def cerrarsesion():
    # Eliminar las variables de sesión
    session.clear()
    session.pop('loggedin', None)
    session.pop('id', None)
    
    # Eliminar la cookie de 'remember_me'
    response = redirect('/')
    response.delete_cookie('remember_me')  # Borra la cookie en el lado del cliente
    return response

# -----------------------------------------------------------------------------------------------------------------
# cancelar el cierre de la sesion

@app.route('/cancelar')
def cancelar():
   
    # Redirigir a la página en la que estaba antes de hacer clic en "logout"
    return redirect(request.referrer)



def pagina_no_encontrada(error):
    return render_template('paginas/errores/404.html'), 404

if __name__ == '__main__':
    app.register_error_handler(404, pagina_no_encontrada)
    app.run(host='0.0.0.0',port=5000,debug=True)



