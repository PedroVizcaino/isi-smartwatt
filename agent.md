# 🏗️ SmartWatt - Plano Maestro del Proyecto

Este archivo actúa como los "planos" de la casa SmartWatt. Proporciona una visión técnica completa de la estructura, tecnologías y flujos del sistema para facilitar el desarrollo y el mantenimiento por parte de agentes de IA y desarrolladores.

---

## 1. 🛠️ Stack Tecnológico (Los Cimientos)

- **Backend**: [Flask (Python 3.9)](https://flask.palletsprojects.com/) - Servidor de API y lógica de negocio en contenedor.
- **Frontend**: [Vanilla JS, HTML5, CSS3](https://developer.mozilla.org/es/docs/Web/JavaScript) - Servido por Nginx.
- **Base de Datos**: [MySQL 8.0](https://www.mysql.com/) - Persistencia robusta en volumen Docker.
- **IA (Cerebro)**: [Ollama](https://ollama.ai/) con el modelo `gemma2:2b` - Puerto **11435** (Modo Host).
- **Proxy/Web Server**: [Nginx](https://nginx.org/) - Puerto **80** (Modo Host).

---

## 2. 📂 Estructura del Proyecto (La Distribución)

```text
/
├── app.py                  # API Server. Rutas de negocio y orquestación de IA.
├── backend/                # Lógica interna y conectores.
│   ├── database.py         # Conector MySQL (Conecta a 127.0.0.1:3307).
│   ├── precio_kw.py        # Scraper de precios PVPC.
│   └── tiempo.py           # Conector OpenWeather (Lee de .env).
├── frontend/               # Interfaz de usuario (Servida por Nginx).
├── .env                    # Configuración real (SECRET_KEY, OPENWEATHER_API_KEY).
├── .env.example            # Plantilla de configuración.
├── docker-compose.yml      # Configurado en 'network_mode: host' para estabilidad TLS.
├── Makefile                # Comandos simplificados.
└── agent.md                # Este documento (El Plano Maestro).
```

---

## 3. 🐳 Arquitectura de Red (Modo Host)

Para evitar problemas de certificados SSL/TLS y DNS que ocurren en algunos entornos con el "Bridge" de Docker, SmartWatt utiliza el **Modo Host**. Los contenedores comparten la pila de red del sistema operativo.

| Servicio | Función | Modo de Red | Puerto (Host) |
| :--- | :--- | :--- | :--- |
| **Frontend** | Nginx / UI | `host` | `80` |
| **Backend** | Flask API | `host` | `5000` |
| **Database** | MySQL | `bridge` | `3307` |
| **Ollama** | Servidor IA | `host` | `11435` |

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

1.  **`install`**: Instala Docker y Docker Compose en el sistema (solo necesario una vez).
2.  **`run`**: Levanta todo el sistema. Si hay cambios en el código, los reconstruye automáticamente.
3.  **`logs`**: Muestra qué está pasando. Vital para ver el progreso de descarga de la IA.
4.  **`stop`**: Apaga los motores.
5.  **`clean`**: Borra todo (imágenes y datos) para un inicio desde cero absoluto.

---

> [!IMPORTANT]
> **Persistencia**: Los datos de la BBDD y los modelos de IA se guardan en **volúmenes de Docker** (`mysql-data` y `ollama-data`), por lo que no se pierden al apagar los contenedores.
