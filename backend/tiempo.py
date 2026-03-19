import requests
from datetime import datetime

def obtener_datos_completos(ciudad, api_key):
    url_actual = f"http://api.openweathermap.org/data/2.5/weather?q={ciudad}&appid={api_key}&units=metric&lang=es"
    
    try:
        res = requests.get(url_actual)
        d = res.json()

        if res.status_code != 200:
            return {"error": d.get('message')}

        nombre = d['name']
        estado = d['weather'][0]['description']
        id_clima = d['weather'][0]['id']
        nubes = d['clouds']['all']
        temp = d['main']['temp']
        visibilidad = d.get('visibility', 0) / 1000
        amanecer = datetime.fromtimestamp(d['sys']['sunrise']).strftime('%H:%M')
        atardecer = datetime.fromtimestamp(d['sys']['sunset']).strftime('%H:%M')
        viento_vel = d['wind']['speed']
        viento_dir = d['wind']['deg']
        viento_racha = d['wind'].get('gust', 'N/A')
        presion = d['main']['pressure']
        humedad = d['main']['humidity']

        recomendacion_eolica = ""
        if viento_vel > 25 or (isinstance(viento_racha, (int, float)) and viento_racha > 25):
            recomendacion_eolica = "🚨 ALERTA: Viento extremo detectado. Asegure equipos."
        elif viento_vel < 4:
            recomendacion_eolica = "🍃 Velocidad del viento insuficiente para la generación eólica."
        else:
            recomendacion_eolica = "💨 Viento óptimo para generación eólica."

        recomendacion_solar = ""
        if nubes >= 70:
            recomendacion_solar = "Estado: ☁️ BAJA | Consejo: Ahorro máximo. Producción solar insuficiente."
        elif nubes < 70 and nubes >= 15:
            recomendacion_solar = "Estado: ⛅ MEDIA | Consejo: Producción estable. Evita encender el horno."
        else:
            recomendacion_solar = "Estado: ☀️ ALTA | Consejo: Carga tus baterías ahora, la luz es gratis."

        return {
            "ciudad": nombre,
            "estado": estado,
            "id_clima": id_clima,
            "nubes": nubes,
            "temp": temp,
            "visibilidad": visibilidad,
            "amanecer": amanecer,
            "atardecer": atardecer,
            "viento_vel": viento_vel,
            "viento_dir": viento_dir,
            "viento_racha": viento_racha,
            "presion": presion,
            "humedad": humedad,
            "recomendacion_eolica": recomendacion_eolica,
            "recomendacion_solar": recomendacion_solar
        }

    except Exception as e:
        return {"error": str(e)}

# --- TU CONFIGURACIÓN ---
MI_API_KEY = "82d4149fee924c1ac0e31da6d5a27e06"
CIUDAD = "Ciudad Real,ES"

if __name__ == "__main__":
    datos = obtener_datos_completos(CIUDAD, MI_API_KEY)
    print(datos)

