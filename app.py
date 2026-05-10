import os
import random
import functools
import requests  # Importante para Ollama
from datetime import datetime
# pyrefly: ignore [missing-import]
from dotenv import load_dotenv
# pyrefly: ignore [missing-import]
from flask import Flask, jsonify, request, send_from_directory, session, redirect, url_for
from flask_cors import CORS
from backend.precio_kw import obtener_precios_corregido
from backend.tiempo import obtener_datos_completos, MI_API_KEY, CIUDAD
from backend.database import init_db, crear_usuario, verificar_usuario, obtener_usuario_por_id

load_dotenv()

app = Flask(__name__)
_secret = os.environ.get('SECRET_KEY')
if not _secret:
    import warnings
    warnings.warn(
        "SECRET_KEY no está configurada. Se usará una clave de desarrollo insegura. "
        "Establece la variable de entorno SECRET_KEY en producción.",
        stacklevel=2
    )
    _secret = 'smartwatt-dev-secret-key-2024'
app.secret_key = _secret
CORS(app, supports_credentials=True)

# Inicializar base de datos al arrancar
init_db()

# --- Decorador de Seguridad ---

def login_required(f):
    @functools.wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            if request.path.startswith('/api/'):
                return jsonify({'error': 'No autenticado'}), 401
            return redirect(url_for('login_page'))
            
        # Verificar que el usuario todavía existe en la BBDD
        from backend.database import obtener_usuario_por_id
        if not obtener_usuario_por_id(session['user_id']):
            session.clear()
            if request.path.startswith('/api/'):
                return jsonify({'error': 'Sesión inválida, usuario no encontrado'}), 401
            return redirect(url_for('login_page'))
            
        return f(*args, **kwargs)
    return decorated

# --- Rutas de Frontend ---

@app.route('/')
@login_required
def index():
    return send_from_directory('frontend', 'dashboard.html')


@app.route('/login')
def login_page():
    if 'user_id' in session:
        return redirect(url_for('index'))
    return send_from_directory('frontend', 'login.html')


# --- Endpoints de Autenticación ---

@app.route('/api/auth/register', methods=['POST'])
def register():
    data = request.json or {}
    nombre = (data.get('nombre') or '').strip()
    email = (data.get('email') or '').strip().lower()
    password = data.get('password') or ''

    if not nombre or not email or not password:
        return jsonify({'error': 'Todos los campos son obligatorios'}), 400
    if len(password) < 8:
        return jsonify({'error': 'La contraseña debe tener al menos 8 caracteres'}), 400

    user_id = crear_usuario(nombre, email, password)
    if user_id is None:
        return jsonify({'error': 'El email ya está registrado'}), 409

    session['user_id'] = user_id
    return jsonify({'mensaje': 'Usuario registrado correctamente', 'nombre': nombre}), 201


@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.json or {}
    email = (data.get('email') or '').strip().lower()
    password = data.get('password') or ''

    if not email or not password:
        return jsonify({'error': 'Email y contraseña son obligatorios'}), 400

    usuario = verificar_usuario(email, password)
    if not usuario:
        return jsonify({'error': 'Credenciales incorrectas'}), 401

    session['user_id'] = usuario['id']
    print(f"DEBUG: Login exitoso para {usuario['nombre']}. Session set: {session['user_id']}")
    return jsonify({'mensaje': 'Sesión iniciada', 'nombre': usuario['nombre']})


@app.route('/api/auth/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'mensaje': 'Sesión cerrada'})


@app.route('/api/auth/me')
def me():
    print(f"DEBUG: Comprobando sesión. session content: {list(session.keys())}")
    if 'user_id' not in session:
        return jsonify({'error': 'No autenticado'}), 401
        
    usuario = obtener_usuario_por_id(session['user_id'])
    if not usuario:
        session.clear()
        return jsonify({'error': 'Usuario no encontrado'}), 404
    return jsonify(usuario)

# --- Endpoints de Datos Energéticos (MySQL) ---

@app.route('/api/precio')
@login_required
def get_precio():
    from backend.database import get_db
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute('''
            SELECT DATE_FORMAT(fecha, '%H:00') as hora, precio_kwh as precio
            FROM historico_precios
            WHERE DATE(fecha) = CURDATE()
            ORDER BY fecha
        ''')
        precios = cursor.fetchall()
        
        if len(precios) < 24:
            precios_api = obtener_precios_corregido()
            if precios_api:
                for p in precios_api:
                    cursor.execute('''
                        INSERT INTO historico_precios (fecha, precio_kwh)
                        VALUES (CONCAT(CURDATE(), ' ', %s, ':00'), %s)
                        ON DUPLICATE KEY UPDATE precio_kwh = VALUES(precio_kwh)
                    ''', (p['hora'].split(':')[0], p['precio']))
                conn.commit()
                precios = precios_api
            else:
                return jsonify({"error": "No hay precios en la BBDD ni en la API para hoy"}), 404
        else:
            for p in precios:
                p['precio'] = float(p['precio'])
            
        ahora = datetime.now().strftime('%H:00')
        precio_actual = next((p['precio'] for p in precios if p['hora'] == ahora), precios[0]['precio'])
        
        return jsonify({
            "actual": precio_actual,
            "historico": precios
        })
    except Exception as e:
        print(f"Error en /api/precio: {e}")
        return jsonify({"error": "Error interno del servidor"}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/api/tiempo')
@login_required
def get_tiempo():
    datos = obtener_datos_completos(CIUDAD, MI_API_KEY)
    if "error" in datos:
        return jsonify(datos), 500
    return jsonify(datos)

@app.route('/api/consumo')
@login_required
def get_consumo():
    user_id = session['user_id']
    from backend.database import get_db
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute('''
            SELECT 
                SUM(consumo_total) as consumo_total,
                SUM(produccion_total) as produccion_total,
                SUM(balance_neto) as balance_neto
            FROM balance_energetico
            WHERE usuario_id = %s AND DATE(fecha_hora) = CURDATE()
        ''', (user_id,))
        kpis = cursor.fetchone()
        
        cursor.execute('''
            SELECT 
                SUM(produccion_solar_kwh) as prod_solar,
                SUM(produccion_eolica_kwh) as prod_eolica
            FROM perfil_produccion
            WHERE usuario_id = %s AND DATE(fecha_hora) = CURDATE()
        ''', (user_id,))
        prod_kpis = cursor.fetchone()
        
        cursor.execute('''
            SELECT 
                DATE_FORMAT(b.fecha_hora, '%H:00') as hora,
                b.consumo_total as consumo,
                p.produccion_solar_kwh as solar,
                p.produccion_eolica_kwh as eolica
            FROM balance_energetico b
            LEFT JOIN perfil_produccion p ON b.usuario_id = p.usuario_id AND b.fecha_hora = p.fecha_hora
            WHERE b.usuario_id = %s AND DATE(b.fecha_hora) = CURDATE()
            ORDER BY b.fecha_hora
        ''', (user_id,))
        evolucion_db = cursor.fetchall()
        
        evolucion = []
        for row in evolucion_db:
            evolucion.append({
                "hora": row['hora'],
                "consumo": float(row['consumo']) if row['consumo'] is not None else 0.0,
                "solar": float(row['solar']) if row['solar'] is not None else 0.0,
                "eolica": float(row['eolica']) if row['eolica'] is not None else 0.0
            })
            
        consumo_total = float(kpis['consumo_total']) if kpis and kpis['consumo_total'] is not None else 0.0
        produccion_total = float(kpis['produccion_total']) if kpis and kpis['produccion_total'] is not None else 0.0
        balance_neto = float(kpis['balance_neto']) if kpis and kpis['balance_neto'] is not None else 0.0
        prod_solar = float(prod_kpis['prod_solar']) if prod_kpis and prod_kpis['prod_solar'] is not None else 0.0
        prod_eolica = float(prod_kpis['prod_eolica']) if prod_kpis and prod_kpis['prod_eolica'] is not None else 0.0
        
        if not evolucion:
            datos_tiempo = obtener_datos_completos(CIUDAD, MI_API_KEY)
            nubes = datos_tiempo.get('nubes', 50) if isinstance(datos_tiempo, dict) and "error" not in datos_tiempo else 50
            viento = datos_tiempo.get('viento_vel', 5) if isinstance(datos_tiempo, dict) and "error" not in datos_tiempo else 5
            hoy_str = datetime.now().strftime('%Y-%m-%d')
            
            for h in range(24):
                hora_str = f"{h:02d}:00"
                fecha_hora_str = f"{hoy_str} {hora_str}:00"
                c = random.uniform(1, 4)
                s = max(0, (1 - nubes/100) * 10 * (1 - abs(13-h)/7)**2) if 6 <= h <= 20 else 0
                e = viento * random.uniform(0.5, 1.5)
                
                cursor.execute('''
                    INSERT INTO perfil_produccion (usuario_id, fecha_hora, produccion_solar_kwh, produccion_eolica_kwh, tipo_medicion)
                    VALUES (%s, %s, %s, %s, 'estimado')
                ''', (user_id, fecha_hora_str, s, e))
                
                balance = (s + e) - c
                cursor.execute('''
                    INSERT INTO balance_energetico (usuario_id, fecha_hora, consumo_total, produccion_total, balance_neto)
                    VALUES (%s, %s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE consumo_total = VALUES(consumo_total), produccion_total = VALUES(produccion_total), balance_neto = VALUES(balance_neto)
                ''', (user_id, fecha_hora_str, c, (s+e), balance))
                
                evolucion.append({"hora": hora_str, "consumo": c, "solar": s, "eolica": e})
                consumo_total += c
                produccion_total += (s + e)
                balance_neto += balance
                prod_solar += s
                prod_eolica += e
            conn.commit()
                
        return jsonify({
            "kpis": {
                "consumo_total": consumo_total,
                "prod_solar": prod_solar,
                "prod_eolica": prod_eolica,
                "balance_neto": balance_neto
            },
            "evolucion": evolucion
        })
    except Exception as e:
        print(f"Error en /api/consumo: {e}")
        return jsonify({"error": "Error interno leyendo BBDD"}), 500
    finally:
        cursor.close()
        conn.close()

# --- Nueva Funcionalidad: Consultas Específicas ---

@app.route('/api/consultas/<tipo>')
@login_required
def get_consultas(tipo):
    user_id = session['user_id']
    from backend.database import get_db
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    try:
        if tipo == 'perfil':
            cursor.execute('''
                SELECT id, nombre, email, ubicacion, tarifa_actual, creado_en 
                FROM usuarios 
                WHERE id = %s
            ''', (user_id,))
            datos = cursor.fetchall()
            for row in datos:
                if row.get('creado_en'):
                    row['creado_en'] = row['creado_en'].strftime('%Y-%m-%d %H:%M:%S')
            
        elif tipo == 'resumen':
            cursor.execute('''
                SELECT fecha, consumo_dia_kwh, produccion_dia_kwh, balance_dia_kwh, ahorro_dia_euros 
                FROM resumen_diario_usuario 
                WHERE usuario_id = %s
                ORDER BY fecha DESC 
            ''', (user_id,))
            datos = cursor.fetchall()
            for row in datos:
                if row.get('fecha'):
                    row['fecha'] = row['fecha'].strftime('%Y-%m-%d')
                for k, v in row.items():
                    if k != 'fecha' and v is not None:
                        row[k] = float(v)
            
        elif tipo == 'analisis_precios':
            cursor.execute('''
                SELECT fecha, precio_min, precio_max, precio_promedio 
                FROM analisis_precios 
                ORDER BY fecha DESC 
            ''')
            datos = cursor.fetchall()
            for row in datos:
                if row.get('fecha'):
                    row['fecha'] = row['fecha'].strftime('%Y-%m-%d')
                for k, v in row.items():
                    if k != 'fecha' and v is not None:
                        row[k] = float(v)
        else:
            return jsonify({"error": "Tipo de consulta no válido"}), 400
            
        return jsonify({"resultados": datos})
    except Exception as e:
        print(f"Error en /api/consultas/{tipo}: {e}")
        return jsonify({"error": "Error interno leyendo BBDD"}), 500
    finally:
        cursor.close()
        conn.close()

# --- Integración Inteligente con Ollama (Cerebro IA) ---

def consultar_ollama(mensaje_usuario, contexto_extra):
    """Consulta a Ollama usando el modelo gemma3:1b"""
    base_url = os.environ.get('OLLAMA_HOST', 'http://localhost:11434')
    url = f"{base_url}/api/chat"
    
    prompt_sistema = f"""Eres un asistente experto en gestión energética para el sistema ISI-SmartWatt. 
Tu objetivo es ayudar al usuario a optimizar su consumo eléctrico y maximizar el uso de energías renovables.
DISPONES DE LOS SIGUIENTES DATOS EN TIEMPO REAL:
{contexto_extra}

Instrucciones:
1. Sé conciso y directo.
2. Usa los datos proporcionados para dar consejos específicos.
3. Responde siempre en español.
"""

    payload = {
        "model": "gemma2:2b",
        "messages": [
            {"role": "system", "content": prompt_sistema},
            {"role": "user", "content": mensaje_usuario}
        ],
        "stream": False
    }

    try:
        response = requests.post(url, json=payload, timeout=60)
        
        # Si el modelo no existe, intentamos pedirle a Ollama que lo baje
        if response.status_code == 404:
            print("IA: Modelo no encontrado. Intentando descargar gemma2:2b...")
            requests.post(f"{base_url}/api/pull", json={"name": "gemma2:2b"}, timeout=5)
            return "Estoy descargando mi cerebro de IA (gemma2:2b). Por favor, espera un par de minutos e inténtalo de nuevo."

        if response.status_code == 200:
            return response.json().get('message', {}).get('content', 'Lo siento, he tenido un problema procesando tu respuesta.')
        else:
            return "Lo siento, el servicio de IA se está inicializando. Inténtalo en un momento."
    except Exception as e:
        print(f"Error consultando Ollama: {e}")
        return "No he podido conectar con mi cerebro de IA. ¿Está Ollama ejecutándose?"

@app.route('/api/chat', methods=['POST'])
@login_required
def chat():
    data = request.json
    mensaje = data.get('mensaje', '')
    
    # Obtener datos reales para el contexto de la IA
    precios = obtener_precios_corregido()
    datos_tiempo = obtener_datos_completos(CIUDAD, MI_API_KEY)
    
    ahora = datetime.now().strftime('%H:00')
    p_actual = next((p['precio'] for p in precios if p['hora'] == ahora), 0)
    
    contexto = f"- Hora actual: {ahora}\n"
    contexto += f"- Precio actual de la luz: {p_actual:.5f} €/kWh\n"
    if precios:
        min_p = min(precios, key=lambda x: x['precio'])
        contexto += f"- Hora más barata hoy: {min_p['hora']}h ({min_p['precio']:.5f} €/kWh)\n"
    
    contexto += f"- Clima en {CIUDAD}: {datos_tiempo.get('temp', 'N/A')}°C, {datos_tiempo.get('nubes', 0)}% de nubes.\n"

    # Llamada a la IA real (Ollama)
    respuesta = consultar_ollama(mensaje, contexto)
        
    return jsonify({"respuesta": respuesta})

if __name__ == '__main__':
    # Usamos host='0.0.0.0' para que sea accesible desde otros contenedores (Nginx)
    app.run(debug=True, host='0.0.0.0', port=5000)