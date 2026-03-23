# SmartWatt - Guía de Contexto del Proyecto (Sprint 2 & 3)

Este archivo sirve como fuente de contexto principal para asistentes de IA que trabajen en este repositorio. Resume la arquitectura, tecnologías y el estado actual del desarrollo.

## 1. Resumen del Proyecto
**SmartWatt** es una aplicación de monitoreo energético doméstico que permite a los usuarios visualizar precios de la luz en tiempo real (PVPC), datos meteorológicos y simular consumos de dispositivos para optimizar el ahorro.

## 2. Arquitectura Técnica
El proyecto sigue un modelo Cliente-Servidor desacoplado:

- **Backend**: Flask (Python). Centraliza la lógica de negocio y consumo de APIs externas.
- **Frontend**: Single Page Application (SPA) servida estáticamente desde `/frontend`.
- **Integraciones**:
  - **PVPC (Red Eléctrica)**: Obtención de precios reales por hora.
  - **OpenWeather**: Datos meteorológicos locales (viento, sol, nubes).
- **Persistencia**: SQLite con SQLAlchemy (en implementación para Sprint 3).

## 3. Estructura de Directorios
```text
/
├── app.py                # Punto de entrada de la aplicación Flask y rutas API
├── backend/              # Lógica de negocio y scrapers/parsers
│   ├── precio_kw.py    # Gestión de precios PVPC
│   └── tiempo.py       # Gestión de meteorología
├── frontend/             # Archivos de interfaz de usuario
│   └── dashboard.html  # UI principal con Chart.js y vanilla JS
├── test/                 # Pruebas unitarias y de integración
├── requirements.txt      # Dependencias del proyecto
└── agent.md              # Este archivo de contexto
```

## 4. API Endpoints (Contrato de Datos)
| Endpoint | Método | Respuesta / Funcionalidad |
| :--- | :--- | :--- |
| `/api/precio` | GET | `{ "actual": float, "historico": [...] }` |
| `/api/tiempo` | GET | `{ "temp": float, "viento_vel": float, "nubes": int }` |
| `/api/consumo`| GET | KPIs de balance (Solar, Eólica, Red) y evolución horaria. |
| `/api/chat`   | POST | Enlace con modelo de IA para consejos de ahorro. |

## 5. Estado del Desarrollo (Sprint 2/3)
- [x] **Sprint 2 (Completado)**: Integración de APIs PVPC/Weather, Dashboard funcional y API básica.
- [ ] **Sprint 3 (En curso)**:
  - [ ] Implementación de base de datos para histórico de consumos.
  - [ ] Integración de asistente inteligente basado en **Gemma 3 1B**.
  - [ ] Refactorización a React completa (actualmente híbrida/vanilla).

## 6. Instrucciones para la IA
Cuando trabajes en este proyecto:
1.  Prioriza la eficiencia energética en las sugerencias del `/api/chat`.
2.  Mantén el backend modular en la carpeta `/backend`.
3.  Asegúrate de que las APIs externas manejen errores (timeout/no data).

