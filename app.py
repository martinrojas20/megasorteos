from flask import Flask, render_template,request, redirect, url_for, flash
from flask_mysqldb import MySQL
import ast
from sentry_sdk.integrations.flask import FlaskIntegration
import sentry_sdk
import yagmail
# SDK de Mercado Pago
import mercadopago
# Agrega credenciales
sdk = mercadopago.SDK("TEST-7183075445093520-031512-4db473f3ba21a52c851431cee8f021b1-1330610285")

sentry_sdk.init(
    dsn="https://c2b4c3f97a8b4b7cb89f6ab14760aefe@o4505001801547776.ingest.sentry.io/4505001805414400",
    integrations=[
        FlaskIntegration(),
    ],

    # Set traces_sample_rate to 1.0 to capture 100%
    # of transactions for performance monitoring.
    # We recommend adjusting this value in production.
    traces_sample_rate=0.6)

app = Flask(__name__)



# Mercadopago ************************
    # Agrega credenciales    


#Configuracion de conexion

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'mern1980'
app.config['MYSQL_DB'] = 'sorteos'

conexionsor = MySQL(app)

app.secret_key = 'mysecretkey'


    

@app.route('/')
def index():    
    data = {
        'titulo': 'Index',
        'bienvenida': 'Bienvenidos a MegaSorteos'                
    }
    return render_template('index.html', data=data)


    

@app.route('/exito/<string:documento>/<string:numeros>')
def exito(documento, numeros):     
    payment_id = request.args.get('payment_id')   
    status = request.args.get('status')
    payment_type = request.args.get('payment_type')
    
    if status == 'approved':
        try:
                cursor = conexionsor.connection.cursor()
                cursor.execute('call sp_insertar_compra(%s, %s, %s, %s)', (payment_id, numeros, payment_type, documento))
                conexionsor.connection.commit()
                cursor.close()
                flash('¡Su registro fué exitoso!, te enviamos un email con la informacón de tú compra.')                
        except Exception as e:
                flash('No se pudo realizar el registro')
        try:
            cursor = conexionsor.connection.cursor()
            cursor.execute(f'SELECT email, nombres FROM clientes WHERE id_cliente = {documento}')
            data = cursor.fetchall()
            cursor.close()            
            email_dest = data[0][0]
            nombre = data[0][1]
            email = 'maemroni@gmail.com'
            asunto = 'Información compra MegaSorteos'
            mensaje = f'Gracias por tu compra {nombre}, te deseamos mucha suerte!'
            mensaje1 = f'Estos fuerón sus números comprados: {numeros}'
            password = 'nubilcmdjgkoejig'
            print('Cliente: ',nombre, email_dest)            
            yag = yagmail.SMTP(user=email, password=password)
            yag.send(email_dest, asunto, [mensaje, mensaje1])
            
        except Exception:
            flash('No hemos podido enviarte el correo, por favor ponte en contacto con nosotros.')

        try:
            print('NUMEROS: ', type(numeros))
            for numero in numeros.split(','):
                cursor = conexionsor.connection.cursor()
                cursor.execute(f'DELETE FROM numeros_disponibles where numero = {numero}')
                conexionsor.connection.commit()
                cursor.close()                
        except Exception as e:
            flash('Ocurrió un error...')           
        return render_template('exito.html') 
          
    








@app.route('/pagar/<string:id>/<string:num>')
def pagar(id, num):     
            
    return render_template('pagar.html', id=id, numeros=num)



    

@app.route('/add_registro', methods=['POST', 'GET'])
def registro():
    if request.method == 'POST':        
        documento = request.form['documento']        
        nombres = request.form['nombres']
        apellidos = request.form['apellidos']
        email = request.form['email']
        telefono = request.form['telefono'] 
        
        try:
            cursor = conexionsor.connection.cursor()
            cursor.execute('call sp_insertar_cliente(%s, %s, %s, %s, %s)', (documento, nombres, apellidos, email, telefono))
            conexionsor.connection.commit()
            flash('¡Su registro fué exitoso!, puede continuar con tú proceso de compra..')
        except Exception :
            flash('No se pudo realizar el registro')
    return redirect(url_for('sorteo1'))




@app.route('/buscar', methods=['POST','GET'])

def buscar(): 
         
    try:
        cursor = conexionsor.connection.cursor()
        cursor.execute('SELECT numero FROM numeros_disponibles')
        data_sorteos = cursor.fetchall()
        cursor.close()        
    except:
        flash('Algo salió mal')  
    numeros = []
    for numero in data_sorteos:
        numeros.append(numero[0])
    if request.method == 'POST': 
        req_data = request.get_data()       
        dict_str = req_data.decode("UTF-8")
        mydata = ast.literal_eval(dict_str)  
        numero = mydata['numero']
        documento = mydata['documento']
        try:
            cursor = conexionsor.connection.cursor()
            cursor.execute(f'SELECT verificar_numero_d({numero})')
            resp = cursor.fetchall()
            cursor.close()       
        except:
            flash('Algo salió mal')  
    
        if resp[0][0] == 1:        
            url = "http://localhost:5000/"+ url_for('exito', documento=documento, numeros=numero)       
            preference_data = {'items': [
                                    {                    
                                    "title": 'R-Hammer',
                                    "quantity": 1,                                
                                    "currency_id": "COP",
                                    "unit_price": 30000}
                                    ],
                                    'back_urls': {
                                        "success": url,
                                        "failure": "http://localhost:8080/feedback",
                                        
                                    },
                                    
                                    'auto_return': "approved",
                                    'binary_mode': True}
                                    
                
            preference_response = sdk.preference().create(preference_data)
            preference = preference_response["response"]

            return  redirect(url_for('pagar', id=preference['id'], num=numero))
        else:             
            
            data = {'titulo': 'Sorteo1',
                    'bienvenida': 'MegaSorteos',
                    'mensaje': 'El número no está disponible.'  }           
            return render_template('sorteo1.html', data=data,numeros=numeros)



@app.route('/sorteo1', methods=['POST','GET'])
def sorteo1():          
    data = {'titulo': 'Sorteo1',
            'bienvenida': 'MegaSorteos'
            }  
    
    try:
        cursor = conexionsor.connection.cursor()
        cursor.execute('SELECT numero FROM numeros_disponibles')
        data_sorteos = cursor.fetchall()
        cursor.close()        
    except:
        flash('Algo salió mal')  
    numeros = []
    for numero in data_sorteos:
        numeros.append(numero[0])

    if request.method == 'POST': 
        data = {'titulo': 'pay',
            'bienvenida': 'MegaSorteos'
            }  
        
        req_data = request.get_data()       
        dict_str = req_data.decode("UTF-8")
        mydata = ast.literal_eval(dict_str)  
        quantity = int(mydata['cantidad'])
        document = mydata['documento'] 
        numbers = str(mydata['numeros'])                
        url = "http://localhost:5000/"+ url_for('exito', documento=document, numeros=numbers)       
        preference_data = {'items': [
                                {                    
                                "title": 'R-Hammer',
                                "quantity": quantity,                                
                                "currency_id": "COP",
                                "unit_price": 30000}
                                ],
                                'back_urls': {
                                    "success": url,
                                    "failure": "http://localhost:8080/feedback",
                                    
                                },
                                
                                'auto_return': "approved",
                                'binary_mode': True}
                                  
            
        preference_response = sdk.preference().create(preference_data)
        preference = preference_response["response"]                                         
        return  redirect(url_for('pagar', id=preference['id'], num=numbers))   
        
    return render_template('sorteo1.html', data=data,numeros=numeros)    
    

# Sorteo2


@app.route('/sorteo2', methods=['POST','GET'])
def sorteo2():          
    data = {'titulo': 'Sorteo2',
            'bienvenida': 'MegaSorteos'
            }  
    
    try:
        cursor = conexionsor.connection.cursor()
        cursor.execute('SELECT numero FROM numeros_disponibles2')
        data_sorteos = cursor.fetchall()
        cursor.close()        
    except:
        flash('Algo salió mal')  
    numeros = []
    for numero in data_sorteos:
        numeros.append(numero[0])

    if request.method == 'POST': 
        data = {'titulo': 'pay',
            'bienvenida': 'MegaSorteos'
            }  
        
        req_data = request.get_data()       
        dict_str = req_data.decode("UTF-8")
        mydata = ast.literal_eval(dict_str)  
        quantity = int(mydata['cantidad'])
        document = mydata['documento'] 
        numbers = str(mydata['numeros'])                
        url = "http://localhost:5000/"+ url_for('exito', documento=document, numeros=numbers)       
        preference_data = {'items': [
                                {                    
                                "title": 'Equinox',
                                "quantity": quantity,                                
                                "currency_id": "COP",
                                "unit_price": 50000}
                                ],
                                'back_urls': {
                                    "success": url,
                                    "failure": "http://localhost:8080/feedback",
                                    
                                },
                                
                                'auto_return': "approved",
                                'binary_mode': True}
                                  
            
        preference_response = sdk.preference().create(preference_data)
        preference = preference_response["response"]                                         
        return  redirect(url_for('pagar', id=preference['id'], num=numbers))   
        
    return render_template('sorteo2.html', data=data,numeros=numeros)



@app.route('/add_registro2', methods=['POST', 'GET'])
def registro2():
    if request.method == 'POST':        
        documento = request.form['documento']        
        nombres = request.form['nombres']
        apellidos = request.form['apellidos']
        email = request.form['email']
        telefono = request.form['telefono'] 
        
        try:
            cursor = conexionsor.connection.cursor()
            cursor.execute('call sp_insertar_cliente2(%s, %s, %s, %s, %s)', (documento, nombres, apellidos, email, telefono))
            conexionsor.connection.commit()
            flash('¡Su registro fué exitoso!, puede continuar con tú proceso de compra..')
        except Exception :
            print(Exception)
            flash('No se pudo realizar el registro')
    return redirect(url_for('sorteo2'))



@app.route('/buscar2', methods=['POST','GET'])

def buscar2(): 
         
    try:
        cursor = conexionsor.connection.cursor()
        cursor.execute('SELECT numero FROM numeros_disponibles2')
        data_sorteos = cursor.fetchall()
        cursor.close()        
    except:
        flash('Algo salió mal')  
    numeros = []
    for numero in data_sorteos:
        numeros.append(numero[0])
    if request.method == 'POST': 
        req_data = request.get_data()       
        dict_str = req_data.decode("UTF-8")
        mydata = ast.literal_eval(dict_str)  
        numero = mydata['numero']
        documento = mydata['documento']
        try:
            cursor = conexionsor.connection.cursor()
            cursor.execute(f'SELECT verificar_numero_d2({numero})')
            resp = cursor.fetchall()
            cursor.close()       
        except:
            flash('Algo salió mal')  
    
        if resp[0][0] == 1:        
            url = "http://localhost:5000/"+ url_for('exito', documento=documento, numeros=numero)       
            preference_data = {'items': [
                                    {                    
                                    "title": 'Equinox',
                                    "quantity": 1,                                
                                    "currency_id": "COP",
                                    "unit_price": 50000}
                                    ],
                                    'back_urls': {
                                        "success": url,
                                        "failure": "http://localhost:8080/feedback",
                                        
                                    },
                                    
                                    'auto_return': "approved",
                                    'binary_mode': True}
                                    
                
            preference_response = sdk.preference().create(preference_data)
            preference = preference_response["response"]
            print('HOLAAAAAAAA')
            return  redirect(url_for('pagar', id=preference['id'], num=numero))
        else:             
            
            data = {'titulo': 'Sorteo2',
                    'bienvenida': 'MegaSorteos',
                    'mensaje': 'El número no está disponible.'  }           
            return render_template('sorteo2.html', data=data,numeros=numeros)


@app.route('/exito2/<string:documento>/<string:numeros>')
def exito2(documento, numeros):     
    payment_id = request.args.get('payment_id')   
    status = request.args.get('status')
    payment_type = request.args.get('payment_type')
    
    if status == 'approved':
        try:
                cursor = conexionsor.connection.cursor()
                cursor.execute('call sp_insertar_compra2(%s, %s, %s, %s)', (payment_id, numeros, payment_type, documento))
                conexionsor.connection.commit()
                cursor.close()
                flash('¡Su registro fué exitoso!, te enviamos un email con la informacón de tú compra.')                
        except Exception as e:
                flash('No se pudo realizar el registro')
        try:
            cursor = conexionsor.connection.cursor()
            cursor.execute(f'SELECT email, nombres FROM clientes2 WHERE id_cliente = {documento}')
            data = cursor.fetchall()
            cursor.close()            
            email_dest = data[0][0]
            nombre = data[0][1]
            email = 'maemroni@gmail.com'
            asunto = 'Información compra MegaSorteos'
            mensaje = f'Gracias por tu compra {nombre}, te deseamos mucha suerte!'
            mensaje1 = f'Estos fuerón sus números comprados: {numeros}'
            password = 'nubilcmdjgkoejig'
            print('Cliente: ',nombre, email_dest)            
            yag = yagmail.SMTP(user=email, password=password)
            yag.send(email_dest, asunto, [mensaje, mensaje1])
            
        except Exception:
            flash('No hemos podido enviarte el correo, por favor ponte en contacto con nosotros.')

        try:
            
            for numero in numeros.split(','):
                cursor = conexionsor.connection.cursor()
                cursor.execute(f'DELETE FROM numeros_disponibles2 where numero = {numero}')
                conexionsor.connection.commit()
                cursor.close()                
        except Exception as e:
            flash('Ocurrió un error...')           
        return render_template('exito2.html') 
          
    



app.route('/')
def pagina_no_encontrada(error):
   # return render_template('404.html'), 404
   return redirect(url_for('index'))






if __name__== '__main__':
    app.register_error_handler(404, pagina_no_encontrada) 
    app.run(debug=True)
