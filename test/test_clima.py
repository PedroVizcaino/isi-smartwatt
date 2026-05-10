import requests
import os


# Cargamos variables de entorno para seguridad


def test_weather_connection():
    print("\n--- Test: API Clima (OpenWeather) ---")
    api_key = "<YOUR_API_KEY>"  # Reemplaza con tu clave real
    ciudad = "Madrid" # Puedes cambiarla por tu ubicación
    url = f"http://api.openweathermap.org/data/2.5/weather?q={ciudad}&appid={api_key}&units=metric"
    
    if not api_key:
        print("❌ Error: No se encontró OPENWEATHER_API_KEY en el archivo .env")
        return

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        # Validamos campos clave para SmartWatt
        temp = data['main']['temp']
        nubes = data['clouds']['all']
        print(f"✅ Conexión exitosa con {ciudad}.")
        print(f"☁️ Estado: {temp}°C y {nubes}% de nubosidad.")
        
    except Exception as e:
        print(f"❌ Error en el test: {e}")

if __name__ == "__main__":
    test_weather_connection()