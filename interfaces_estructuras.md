## 📂 Interfaces y Estructuras de Datos

Este apartado define el "contrato" técnico de comunicación entre los módulos de **SmartWatt**, garantizando la correcta integración de sistemas externos y la persistencia local.

### 1. Interfaces (API REST Endpoints)
El Frontend (React) interactúa con el Backend (Flask) mediante los siguientes puntos de entrada asíncronos:

| Endpoint | Método | Descripción |
| :--- | :--- | :--- |
| `/api/precio` | **GET** | Obtiene la curva de precios PVPC (24h) y el valor actual en €/kWh. |
| `/api/consumo` | **GET** | Retorna el balance energético (Solar, Eólica, Red) y KPIs de eficiencia. |
| `/api/tiempo` | **GET** | Proporciona datos meteorológicos actuales (Temp, Viento, Nubes). |
| `/api/chat` | **POST** | Envía consultas al modelo **Gemma 3 1b** para obtener consejos de ahorro. |

---

### 2. Estructuras de Datos (Formato JSON)
La comunicación se realiza exclusivamente mediante objetos **JSON** para asegurar la interoperabilidad.

#### **A. Respuesta de Precios (Curva Diaria)**
```json
{
  "actual": 0.1145,
  "historico": [
    {"hora": "00-01", "precio": 0.102},
    {"hora": "01-02", "precio": 0.098}
  ]
}
