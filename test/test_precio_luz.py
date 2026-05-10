import requests
from datetime import datetime

def obtener_precios_dia():
    fecha_hoy = datetime.now().strftime("%Y-%m-%d")
    # Archivo 70: Precio voluntario para el pequeño consumidor (PVPC)
    url = f"https://api.esios.ree.es/archives/70/download_json?locale=es&date={fecha_hoy}"
    
    print(f"--- Consultando precios para el día: {fecha_hoy} ---")
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        precios_24h = []
        
        # Recorremos los datos de la API (vienen las 24 horas en el campo 'PVPC')
        for item in data["PVPC"]:
            hora = item["Hora"] # Ejemplo: "00-01"
            # El precio viene en €/MWh, lo pasamos a €/kWh dividiendo por 1000
            precio_kwh = float(item["PCB"].replace(',', '.')) / 1000
            
            precios_24h.append({
                "hora": hora,
                "precio": round(precio_kwh, 5)
            })
            
        return precios_24h

    except Exception as e:
        print(f"❌ Error al obtener datos: {e}")
        return []

# Ejecución y visualización en tabla
precios = obtener_precios_dia()

if precios:
    print(f"{'HORA':<10} | {'PRECIO (€/kWh)':<15}")
    print("-" * 30)
    for p in precios:
        # Resaltamos horas baratas (ej: menos de 0.10)
        aviso = "🟢 BARATA" if p['precio'] < 0.10 else ""
        print(f"{p['hora']:<10} | {p['precio']:<15} {aviso}")