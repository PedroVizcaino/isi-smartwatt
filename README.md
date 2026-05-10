# ⚡ ISI SmartWatt - Guía completa de instalación y uso

Esta guía explica paso a paso cómo preparar y ejecutar el proyecto correctamente.

---

## 📥 1. Clonar el repositorio

```bash
git clone https://github.com/PedroVizcaino/isi-smartwatt.git
cd isi-smartwatt
```

---

## 🌦️ 2. Obtener API Key de OpenWeather

Este proyecto usa datos meteorológicos, por lo que necesitas una API Key.

### Pasos:

1. Ir a: https://openweathermap.org/api
2. Crear una cuenta gratuita
3. Ir a tu perfil → **API Keys**
4. Copiar la clave

⚠️ Puede tardar unos minutos en activarse.

---

## 🔑 3. Añadir la API Key al proyecto

Busca en el código dónde se usa OpenWeather. Normalmente será algo como:

```python
API_KEY = "YOUR_API_KEY"
```

Y reemplázalo por:

```python
API_KEY = "tu_api_key_aqui"
```

---

### ✅ Recomendación (mejor práctica)

Usar variables de entorno:

Crear archivo `.env`:

```env
OPENWEATHER_API_KEY=tu_api_key_aqui
```

Y en Python:

```python
import os

API_KEY = os.getenv("OPENWEATHER_API_KEY")
```

---

## ⚙️ 4. Uso del Makefile

Este proyecto usa un `Makefile` para automatizar todo el flujo. Aquí tienes qué hace cada comando:

---

### 🟢 `make start` → Configuración completa

```bash
make start
```

🔧 Este comando:

* Crea un entorno virtual llamado `vens2` (si no existe)
* Instala `pip` actualizado
* Instala dependencias desde `requirements.txt`

📌 Internamente hace:

```bash
python3 -m venv vens2
vens2/bin/pip install -r requirements.txt
```

👉 Es el **primer comando que debes ejecutar siempre**

---

### ▶️ `make run` → Ejecutar la aplicación

```bash
make run
```

🚀 Ejecuta:

```bash
vens2/bin/python app.py
```

👉 Inicia el proyecto principal (`app.py`)

---

### 🧪 `make test` → Ejecutar tests

```bash
make test
```

🧪 Ejecuta pruebas usando `pytest`:

```bash
vens2/bin/python -m pytest test/
```

📌 Requisitos:

* Debe existir carpeta `test/`
* Debes tener `pytest` en `requirements.txt`

---

### 🧹 `make clean` → Limpiar el proyecto

```bash
make clean
```

🧽 Elimina:

* El entorno virtual `vens2`
* Carpetas `__pycache__`

📌 Internamente:

```bash
rm -rf vens2
find . -type d -name "__pycache__" -exec rm -rf {} +
```

👉 Útil si algo falla y quieres empezar limpio

---

## 🔄 5. Flujo completo recomendado

```bash
# 1. Clonar
git clone https://github.com/PedroVizcaino/isi-smartwatt.git
cd isi-smartwatt

# 2. Configurar entorno
make start

# 3. Añadir API Key (manual o .env)

# 4. Ejecutar app
make run
```

---

