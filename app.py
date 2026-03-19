import os
import random
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from backend.precio_kw import obtener_precios_corregido
from backend.tiempo import obtener_datos_completos, MI_API_KEY, CIUDAD

app = Flask(__name__)
CORS(app)

# Servir archivos estáticos del frontend
@app.route('/')
def index():
    return send_from_directory('frontend', 'dashboard.html')

@app.route('/api/precio')
def get_precio():
    precios = obtener_precios_corregido()
    if not precios:
        return jsonify({"error": "No se pudieron obtener los precios"}), 500
    
    # Obtener el precio actual based on the current hour
    from datetime import datetime
    ahora = datetime.now().strftime('%H:00')
    precio_actual = next((p['precio'] for p in precios if p['hora'] == ahora), precios[0]['precio'])
    
    return jsonify({
        "actual": precio_actual,
        "historico": precios
    })

@app.route('/api/tiempo')
def get_tiempo():
    datos = obtener_datos_completos(CIUDAD, MI_API_KEY)
    if "error" in datos:
        return jsonify(datos), 500
    return jsonify(datos)

@app.route('/api/consumo')
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

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    mensaje = data.get('mensaje', '').lower()
    
    # Lógica simple de chatbot enriquecida con datos
    precios = obtener_precios_corregido()
    datos_tiempo = obtener_datos_completos(CIUDAD, MI_API_KEY)
    
    if 'lavadora' in mensaje:
        # Buscar hora más barata
        hora_barata = min(precios, key=lambda x: x['precio'])
        respuesta = f"Te sugiero poner la lavadora a las {hora_barata['hora']}h. El precio será de {hora_barata['precio']:.5f} €/kWh, el más bajo de hoy."
    elif 'solar' in mensaje or 'paneles' in mensaje:
        nubes = datos_tiempo.get('nubes', 0)
        if nubes < 20:
            respuesta = "Hoy es un día excelente para la energía solar. Tienes menos del 20% de nubes."
        else:
            respuesta = f"Hoy hay un {nubes}% de nubes, la producción solar será moderada."
    elif 'precio' in mensaje:
        ahora = datetime.now().strftime('%H:00')
        p_actual = next((p['precio'] for p in precios if p['hora'] == ahora), 0)
        respuesta = f"El precio actual de la luz es de {p_actual:.5f} €/kWh."
    else:
        respuesta = "Interesante pregunta. Estoy monotorizando tus datos en tiempo real para darte el mejor consejo energético pronto."
        
    return jsonify({"respuesta": respuesta})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
