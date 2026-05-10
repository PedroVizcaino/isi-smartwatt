# ⚡ ISI SmartWatt - Guía completa de instalación y uso

Esta guía explica paso a paso cómo preparar y ejecutar el proyecto correctamente.

---

## 📥 1. Clonar el repositorio

```bash
git clone https://github.com/PedroVizcaino/isi-smartwatt.git
cd isi-smartwatt
```

---

## 🔑 2. Configuración de variables de entorno (.env)

Este proyecto utiliza un archivo `.env` para gestionar claves y contraseñas de forma segura.

1.  Crea una copia del archivo de ejemplo:
    ```bash
    cp .env.example .env
    ```
2.  Abre el archivo `.env` y rellena los valores:
    - **OPENWEATHER_API_KEY:** Obtén tu clave gratuita en [OpenWeatherMap](https://openweathermap.org/api).
    - **SECRET_KEY:** Una clave aleatoria para proteger las sesiones de usuario.

---

## ⚙️ 3. Uso del Makefile (Docker)

Este proyecto está totalmente contenedorizado. El `Makefile` automatiza la instalación de Docker, la construcción de imágenes y la ejecución de tests.

### 🛠️ Gestión de contenedores

| Comando | Descripción |
| :--- | :--- |
| `make start` | **Primer paso:** Instala Docker (si no existe) y construye las imágenes. |
| `make run` | **Arrancar:** Levanta todos los servicios en segundo plano. |
| `make status` | **Estado:** Muestra si los contenedores están funcionando. |
| `make logs` | **Logs:** Muestra los mensajes de la App y la IA en tiempo real. |
| `make stop` | **Parar:** Detiene los servicios sin borrar nada. |
| `make restart` | **Reiniciar:** Reinicia todos los servicios. |
| `make clean` | **Limpieza:** Borra imágenes, volúmenes y contenedores (libera espacio). |

---

### 🧪 Tests de funcionalidad (Ejecutados dentro de Docker)

No necesitas instalar Python ni librerías en tu PC local. Los tests se ejecutan dentro del contenedor de la aplicación.

| Comando | Qué verifica |
| :--- | :--- |
| `make test-api` | Conectividad del Backend Flask. |
| `make test-db` | Conexión con MySQL y existencia de tablas. |
| `make test-ia` | Estado de Ollama y modelos descargados. |
| `make test-clima` | Conexión con la API de OpenWeather. |
| `make test-precio` | Conexión con la API de Precios de Luz. |
| `make test-all` | Ejecuta **toda** la suite de pruebas. |

---

## 🔄 5. Flujo completo recomendado

Si es la primera vez que ejecutas el proyecto en este PC:

```bash
# 1. Preparar Docker e imágenes (solo la primera vez)
sudo make start

# 2. Arrancar la aplicación
sudo make run

# 3. Verificar que todo está bien
make status
make test-all

# 4. Ver progreso de la descarga de la IA
make logs
```

🚀 **SmartWatt estará disponible en:**
*   Frontend: `http://localhost`
*   Backend API: `http://localhost:5000`
*   Ollama API: `http://localhost:11434`

