# 🏗️ SmartWatt - Plano Maestro del Proyecto

Este archivo actúa como los "planos" de la casa SmartWatt. Proporciona una visión técnica completa de la estructura, tecnologías y flujos del sistema para facilitar el desarrollo y el mantenimiento por parte de agentes de IA y desarrolladores.

---

## 1. 🛠️ Stack Tecnológico (Los Cimientos)

- **Backend**: [Flask (Python 3.9)](https://flask.palletsprojects.com/) - Servidor de API y lógica de negocio en contenedor.
- **Frontend**: [Vanilla JS, HTML5, CSS3](https://developer.mozilla.org/es/docs/Web/JavaScript) - Servido por Nginx.
- **Base de Datos**: [MySQL 8.0](https://www.mysql.com/) - Persistencia robusta en volumen Docker.
- **IA (Cerebro)**: [Ollama](https://ollama.ai/) con el modelo `gemma2:2b` - Asistente inteligente local y privado.
- **Proxy/Web Server**: [Nginx](https://nginx.org/) - Orquestador de rutas y servidor de archivos estáticos.

---

## 2. 📂 Estructura del Proyecto (La Distribución)

```text
/
├── app.py                  # API Server. Rutas de negocio y orquestación de IA.
├── backend/                # Lógica interna y conectores.
│   ├── database.py         # Conector MySQL con lógica de reintento (Docker-ready).
│   ├── mysql_manager.py    # Gestión avanzada de la BBDD.
│   ├── precio_kw.py        # Scraper de precios PVPC.
│   └── tiempo.py           # Conector OpenWeather API.
├── frontend/               # Interfaz de usuario (Servida por Nginx).
│   ├── dashboard.html      # Panel principal con validación de sesión activa.
│   └── login.html          # Sistema de acceso y registro.
├── Dockerfile              # Instrucciones de construcción para el Backend.
├── docker-compose.yml      # El "Director de Orquesta" de los 5 contenedores.
├── nginx.conf              # Configuración de rutas y proxy inverso.
├── Makefile                # Comandos simplificados (start, run, logs, clean).
├── schema_mysql.sql        # Esquema inicial de la base de datos.
├── requirements.txt        # Dependencias Python.
└── agent.md                # Este documento (El Plano Maestro).
```

---

## 3. 🐳 Arquitectura de Contenedores (Docker)

El sistema se divide en **5 servicios independientes** que se comunican entre sí:

| Servicio | Función | Imagen | Puerto (Host) |
| :--- | :--- | :--- | :--- |
| **Frontend** | Servidor Web y Proxy | `nginx:alpine` | `80` |
| **Backend** | Lógica y API | `python:3.9-slim` | `5000` (interno) |
| **Database** | Almacenamiento MySQL | `mysql:8.0` | `3307` |
| **Ollama** | Servidor de IA | `ollama/ollama` | `11434` (interno) |
| **Pull-Model** | Descargador de IA | `ollama/ollama` | N/A |

---

## 4. 🔄 Flujos Principales (Funcionamiento)

### A. Autenticación y Sesión
El sistema utiliza **Flask Sessions** con cookies. Nginx actúa como puente, asegurando que las cookies de sesión se transmitan correctamente entre el frontend (`/`) y el backend (`/api`).

### B. Asistente IA (Consultas)
El endpoint `/api/chat` utiliza el modelo **gemma2:2b**. 
- **Autocuración**: Si el modelo no está presente, el Backend inicia automáticamente la descarga y avisa al usuario.
- **Contexto**: Se envían datos reales de consumo y clima para que la IA dé consejos precisos.

---

## 5. 🚀 Guía de Mantenimiento (Comandos Rápidos)

Desde la raíz del proyecto, usa `sudo make` seguido de:

1.  **`run`**: Levanta todo el sistema. Si hay cambios en el código, los reconstruye automáticamente.
2.  **`logs`**: Muestra qué está pasando. Vital para ver el progreso de descarga de la IA.
3.  **`stop`**: Apaga los motores.
4.  **`clean`**: Borra todo (imágenes y datos) para un inicio desde cero absoluto.

---

> [!IMPORTANT]
> **Persistencia**: Los datos de la BBDD y los modelos de IA se guardan en **volúmenes de Docker** (`mysql-data` y `ollama-data`), por lo que no se pierden al apagar los contenedores.
