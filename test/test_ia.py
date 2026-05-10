import requests

def test_ollama_ia():
    print("\n--- Test: Inteligencia Artificial (Ollama) ---")
    url = "http://ollama:11434/api/tags"
    
    try:
        response = requests.get(url, timeout=5)
        
        if response.status_code == 200:
            print("✅ Ollama está encendido y accesible.")
            models = response.json().get('models', [])
            if models:
                print(f"🤖 Modelos descargados ({len(models)}):")
                for m in models:
                    print(f"   - {m['name']}")
            else:
                print("⚠️ Ollama funciona, pero todavía no se ha descargado ningún modelo.")
        else:
            print(f"⚠️ Ollama respondió con código inesperado: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Error: No se puede conectar con Ollama en el puerto 11434.")
        print("Esto es normal si el contenedor todavía está arrancando o descargando la IA.")
    except Exception as e:
        print(f"❌ Error al conectar con la IA: {e}")

if __name__ == "__main__":
    test_ollama_ia()
