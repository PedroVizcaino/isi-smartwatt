import requests
from datetime import datetime

def obtener_precios_corregido():
    hoy = datetime.now().strftime('%Y-%m-%d')
    url = "https://apidatos.ree.es/es/datos/mercados/precios-mercados-tiempo-real"
    params = {
        'start_date': f'{hoy}T00:00',
        'end_date': f'{hoy}T23:59',
        'time_trunc': 'hour',
        'geo_limit': 'peninsular',
        'geo_ids': '8741'
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 500:
            return obtener_precio_alternativo()
        response.raise_for_status()
        datos = response.json()
        pvpc_bloque = next(item for item in datos['included'] if item['id'] == '1001')
        valores = pvpc_bloque['attributes']['values']
        
        resultado = []
        for entrada in valores:
            hora = datetime.fromisoformat(entrada['datetime']).strftime('%H:%M')
            precio = entrada['value'] / 1000
            resultado.append({'hora': hora, 'precio': precio})
        return resultado

    except Exception as e:
        print(f"⚠️ Error en REE: {e}")
        return obtener_precio_alternativo()

def obtener_precio_alternativo():
    
    try:
        res = requests.get("https://api.preciodelaluz.org/v1/prices/all?zone=PCB")
        data = res.json()
        resultado = []
        for hora, info in data.items():
            resultado.append({'hora': hora, 'precio': info['price']/1000})
        # Ordenamos por hora para consistencia
        resultado.sort(key=lambda x: x['hora'])
        return resultado
    except Exception as e:
        print(f"⚠️ Error en API alternativa: {e}")
        return []

if __name__ == "__main__":
    precios = obtener_precios_corregido()
    for p in precios:
        print(f"Hora: {p['hora']} -> {p['precio']:.5f} €/kWh")

