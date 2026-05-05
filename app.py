import os
import random
import functools
import requests
from datetime import datetime
from dotenv import load_dotenv
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


def login_required(f):
    @functools.wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            if request.path.startswith('/api/'):
                return jsonify({'error': 'No autenticado'}), 401
            return redirect(url_for('login_page'))
        return f(*args, **kwargs)
    return decorated

# Servir archivos estáticos del frontend
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
    return jsonify({'mensaje': 'Sesión iniciada', 'nombre': usuario['nombre']})


@app.route('/api/auth/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'mensaje': 'Sesión cerrada'})


@app.route('/api/auth/me')
@login_required
def me():
    usuario = obtener_usuario_por_id(session['user_id'])
    if not usuario:
        session.clear()
        return jsonify({'error': 'Usuario no encontrado'}), 404
    return jsonify(usuario)

@app.route('/api/precio')
@login_required
def get_precio():
    precios = obtener_precios_corregido()
    if not precios:
        return jsonify({"error": "No se pudieron obtener los precios"}), 500
    
    ahora = datetime.now().strftime('%H:00')
    precio_actual = next((p['precio'] for p in precios if p['hora'] == ahora), precios[0]['precio'])
    
    return jsonify({
        "actual": precio_actual,
        "historico": precios
    })

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
    # Generar datos simulados de consumo y producción basados en el tiempo actual
    # En un caso real, esto vendría de sensores o una base de datos
    datos_tiempo = obtener_datos_completos(CIUDAD, MI_API_KEY)
    
    # Simulación básica
    is_day = 7 <= int(random.randint(0, 23)) <= 20 # Simplificado
    nubes = datos_tiempo.get('nubes', 50)
    viento = datos_tiempo.get('viento_vel', 5)
    
    prod_solar = max(0.0, float((1 - nubes/100) * 8)) if is_day else 0.0
    prod_eolica = viento * 2
    consumo = random.uniform(1.5, 4.5)
    
    balance = (prod_solar + prod_eolica) - consumo
    
    # Generar evolución horaria (simulada para 24h)
    evolucion = []
    for h in range(24):
        hora_str = f"{h:02d}:00"
        c = random.uniform(1, 4)
        s = max(0, (1 - nubes/100) * 10 * (1 - abs(13-h)/7)**2) if 6 <= h <= 20 else 0
        e = viento * random.uniform(0.5, 1.5)
        evolucion.append({
            "hora": hora_str,
            "consumo": c,
            "solar": s,
            "eolica": e
        })
        
    return jsonify({
        "kpis": {
            "consumo_total": 24.5 + random.uniform(-2, 2), # Acumulado simulado
            "prod_solar": 18.2 + random.uniform(-1, 1),
            "prod_eolica": 12.4 + random.uniform(-1, 1),
            "balance_neto": balance
        },
        "evolucion": evolucion
    })

def consultar_ollama(mensaje_usuario, contexto_extra):
    """Consulta a Ollama usando el modelo gemma3:1b"""
    url = "http://localhost:11434/api/chat"
    
    prompt_sistema = f"""Eres un asistente experto en gestión energética para el sistema ISI-SmartWatt. 
Tu objetivo es ayudar al usuario a optimizar su consumo eléctrico y maximizar el uso de energías renovables.
DISPONES DE LOS SIGUIENTES DATOS EN TIEMPO REAL:
{contexto_extra}

Instrucciones:
1. Sé conciso y directo.
2. Usa los datos proporcionados para dar consejos específicos (ej: 'Pon la lavadora ahora porque el precio es bajo').
3. Si te preguntan algo fuera del tema energético, responde amablemente pero intenta reconducir la charla hacia el ahorro de energía.
4. Responde siempre en español.
"""

    payload = {
        "model": "gemma3:1b",
        "messages": [
            {"role": "system", "content": prompt_sistema},
            {"role": "user", "content": mensaje_usuario}
        ],
        "stream": False
    }

    try:
        response = requests.post(url, json=payload, timeout=60)
        if response.status_code == 200:
            return response.json().get('message', {}).get('content', 'Lo siento, he tenido un problema procesando tu respuesta.')
        else:
            return "Lo siento, el servicio de IA no está disponible en este momento."
    except Exception as e:
        print(f"Error consultando Ollama: {e}")
        return "No he podido conectar con mi cerebro de IA. ¿Está Ollama ejecutándose?"

@app.route('/api/chat', methods=['POST'])
@login_required
def chat():
    data = request.json
    mensaje = data.get('mensaje', '')
    
    # Obtener datos reales para el contexto
    precios = obtener_precios_corregido()
    datos_tiempo = obtener_datos_completos(CIUDAD, MI_API_KEY)
    
    # Preparar resumen de contexto para la IA
    ahora = datetime.now().strftime('%H:00')
    p_actual = next((p['precio'] for p in precios if p['hora'] == ahora), 0)
    
    contexto = f"- Hora actual: {ahora}\n"
    contexto += f"- Precio actual de la luz: {p_actual:.5f} €/kWh\n"
    if precios:
        min_p = min(precios, key=lambda x: x['precio'])
        contexto += f"- Hora más barata hoy: {min_p['hora']}h ({min_p['precio']:.5f} €/kWh)\n"
    
    contexto += f"- Clima en {CIUDAD}: {datos_tiempo.get('temp', 'N/A')}°C, {datos_tiempo.get('nubes', 0)}% de nubes, viento de {datos_tiempo.get('viento_vel', 0)} m/s.\n"

    respuesta = consultar_ollama(mensaje, contexto)
        
    return jsonify({"respuesta": respuesta})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
