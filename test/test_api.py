import requests

def test_backend_api():
    print("\n--- Test: Backend API (Flask) ---")
    url = "http://backend:5000"
    
    try:
        # Intentamos conectar al endpoint raíz o de salud
        response = requests.get(f"{url}/", timeout=5)
        
        if response.status_code == 200:
            print("✅ El Backend está funcionando correctamente.")
            print(f"📡 Respuesta: {response.text[:50]}...")
        else:
            print(f"⚠️ El Backend respondió con código: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Error: No se puede conectar al Backend en http://localhost:5000")
        print("¿Has ejecutado 'make run'?")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")

if __name__ == "__main__":
    test_backend_api()
