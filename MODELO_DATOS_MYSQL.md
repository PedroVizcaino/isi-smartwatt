# Modelo de Datos MySQL - ISI-SmartWatt

## 📊 Descripción General

Este documento describe el modelo de datos diseñado en MySQL para almacenar el **histórico de precios de electricidad** y el **perfil de uso simulado del usuario** en el sistema ISI-SmartWatt.

## 🏗️ Arquitectura del Modelo

El modelo está compuesto por **9 tablas principales** organizadas en 3 módulos funcionales:

### 1️⃣ Módulo de Usuarios
- `usuarios` - Información de usuarios y configuración

### 2️⃣ Módulo de Datos Energéticos
- `historico_precios` - Precios históricos de electricidad
- `perfil_consumo` - Registro de consumo energético
- `perfil_produccion` - Registro de producción renovable
- `balance_energetico` - Balance neto consumo/producción

### 3️⃣ Módulo de Inteligencia y Recomendaciones
- `alertas_usuario` - Alertas y notificaciones
- `dispositivos_usuario` - Catálogo de dispositivos
- `recomendaciones_ia` - Recomendaciones de IA
- `patrones_consumo` - Patrones detectados

---

## 📋 Descripción Detallada de Tablas

### 1. **usuarios**
Almacena la información de los usuarios del sistema.

```sql
CREATE TABLE usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    ubicacion VARCHAR(100) DEFAULT 'Madrid',
    tarifa_actual VARCHAR(50) DEFAULT 'PVPC',
    preferencias JSON,
    creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    actualizado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
```

**Campos clave:**
- `ubicacion`: Ciudad del usuario para datos climáticos
- `tarifa_actual`: Tipo de tarifa eléctrica (PVPC, tarifa fija, etc.)
- `preferencias`: Configuración personalizada en JSON

---

### 2. **historico_precios**
Almacena el histórico completo de precios de electricidad por hora.

```sql
CREATE TABLE historico_precios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    fecha_hora DATETIME NOT NULL,
    precio_kwh DECIMAL(10, 6) NOT NULL,
    zona VARCHAR(50) DEFAULT 'ES',
    fuente VARCHAR(50) DEFAULT 'ESIOS',
    tipo_tarifa VARCHAR(50) DEFAULT 'PVPC',
    creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY unique_precio (fecha_hora, zona, tipo_tarifa)
);
```

**Casos de uso:**
- ✅ Análisis de tendencias de precios
- ✅ Identificación de horas valle/punta
- ✅ Predicción de precios futuros
- ✅ Cálculo de ahorros potenciales

**Índices:**
- `idx_fecha_hora`: Búsquedas por fecha/hora
- `idx_zona_fecha`: Búsquedas por zona y fecha

---

### 3. **perfil_consumo**
Registro detallado del consumo energético del usuario.

```sql
CREATE TABLE perfil_consumo (
    id INT AUTO_INCREMENT PRIMARY KEY,
    usuario_id INT NOT NULL,
    fecha_hora DATETIME NOT NULL,
    consumo_kwh DECIMAL(10, 4) NOT NULL,
    dispositivo VARCHAR(100) DEFAULT 'General',
    tipo_medicion ENUM('real', 'simulado', 'estimado') DEFAULT 'simulado',
    notas TEXT,
    metadata JSON,
    creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
);
```

**Características:**
- Soporte para consumo real, simulado o estimado
- Trazabilidad por dispositivo
- Metadatos extensibles en JSON
- Relación con usuario (CASCADE)

**Métricas que permite calcular:**
- 📈 Consumo horario, diario, mensual
- 📊 Patrones de uso por dispositivo
- 💡 Identificación de consumo anómalo

---

### 4. **perfil_produccion**
Registro de producción energética renovable (solar, eólica, otras).

```sql
CREATE TABLE perfil_produccion (
    id INT AUTO_INCREMENT PRIMARY KEY,
    usuario_id INT NOT NULL,
    fecha_hora DATETIME NOT NULL,
    produccion_solar_kwh DECIMAL(10, 4) DEFAULT 0,
    produccion_eolica_kwh DECIMAL(10, 4) DEFAULT 0,
    produccion_otras_kwh DECIMAL(10, 4) DEFAULT 0,
    tipo_medicion ENUM('real', 'simulado', 'estimado') DEFAULT 'simulado',
    condiciones_climaticas JSON,
    creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
);
```

**Datos almacenados en `condiciones_climaticas` (JSON):**
```json
{
  "temperatura": 22.5,
  "nubes": 30,
  "viento_vel": 12.3,
  "radiacion_solar": 850,
  "humedad": 65
}
```

---

### 5. **balance_energetico**
Tabla clave que calcula el balance neto entre consumo y producción.

```sql
CREATE TABLE balance_energetico (
    id INT AUTO_INCREMENT PRIMARY KEY,
    usuario_id INT NOT NULL,
    fecha_hora DATETIME NOT NULL,
    consumo_total DECIMAL(10, 4) NOT NULL,
    produccion_total DECIMAL(10, 4) NOT NULL,
    balance_neto DECIMAL(10, 4) NOT NULL,
    coste_estimado DECIMAL(10, 4),
    ahorro_estimado DECIMAL(10, 4),
    precio_medio_kwh DECIMAL(10, 6),
    creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE,
    UNIQUE KEY unique_balance (usuario_id, fecha_hora)
);
```

**Cálculos automáticos:**
- `balance_neto = produccion_total - consumo_total`
- `coste_estimado` si balance < 0 (compra de red)
- `ahorro_estimado` si balance > 0 (venta a red)

---

### 6. **alertas_usuario**
Sistema de notificaciones y alertas personalizadas.

```sql
CREATE TABLE alertas_usuario (
    id INT AUTO_INCREMENT PRIMARY KEY,
    usuario_id INT NOT NULL,
    tipo_alerta ENUM('precio_alto', 'precio_bajo', 'exceso_consumo', 'recomendacion', 'mantenimiento'),
    titulo VARCHAR(200) NOT NULL,
    mensaje TEXT NOT NULL,
    prioridad ENUM('baja', 'media', 'alta') DEFAULT 'media',
    leida BOOLEAN DEFAULT FALSE,
    fecha_alerta DATETIME NOT NULL,
    datos_adicionales JSON,
    creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
);
```

**Tipos de alertas:**
- 🔴 `precio_alto`: Precio supera umbral
- 🟢 `precio_bajo`: Precio óptimo para consumo
- ⚠️ `exceso_consumo`: Consumo anómalo
- 💡 `recomendacion`: Sugerencia de optimización
- 🔧 `mantenimiento`: Mantenimiento preventivo

---

### 7. **dispositivos_usuario**
Catálogo de dispositivos eléctricos del hogar.

```sql
CREATE TABLE dispositivos_usuario (
    id INT AUTO_INCREMENT PRIMARY KEY,
    usuario_id INT NOT NULL,
    nombre VARCHAR(100) NOT NULL,
    tipo VARCHAR(50) NOT NULL,
    potencia_watts INT NOT NULL,
    consumo_estimado_kwh DECIMAL(10, 4),
    horario_uso VARCHAR(50),
    activo BOOLEAN DEFAULT TRUE,
    creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
);
```

**Ejemplos de dispositivos:**
```sql
INSERT INTO dispositivos_usuario (usuario_id, nombre, tipo, potencia_watts, horario_uso) VALUES
(1, 'Lavadora LG', 'lavadora', 2000, '22:00-23:00'),
(1, 'Frigorífico Samsung', 'nevera', 150, '24h'),
(1, 'Aire Acondicionado', 'climatizacion', 3000, '14:00-18:00');
```

---

### 8. **recomendaciones_ia**
Recomendaciones generadas por algoritmos de IA.

```sql
CREATE TABLE recomendaciones_ia (
    id INT AUTO_INCREMENT PRIMARY KEY,
    usuario_id INT NOT NULL,
    tipo_recomendacion ENUM('optimizacion', 'ahorro', 'eficiencia', 'tarifaria'),
    titulo VARCHAR(200) NOT NULL,
    descripcion TEXT NOT NULL,
    ahorro_potencial DECIMAL(10, 2),
    prioridad INT DEFAULT 5,
    aplicada BOOLEAN DEFAULT FALSE,
    fecha_recomendacion DATETIME NOT NULL,
    fecha_aplicacion DATETIME,
    modelo_ia VARCHAR(50),
    creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
);
```

---

### 9. **patrones_consumo**
Patrones de consumo detectados automáticamente.

```sql
CREATE TABLE patrones_consumo (
    id INT AUTO_INCREMENT PRIMARY KEY,
    usuario_id INT NOT NULL,
    tipo_patron ENUM('diario', 'semanal', 'mensual', 'estacional'),
    descripcion VARCHAR(200) NOT NULL,
    hora_pico_inicio TIME,
    hora_pico_fin TIME,
    consumo_promedio DECIMAL(10, 4),
    desviacion_estandar DECIMAL(10, 4),
    confianza DECIMAL(5, 2),
    datos_patron JSON,
    fecha_deteccion DATETIME NOT NULL,
    activo BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
);
```

---

## 📊 Vistas Predefinidas

### Vista: `resumen_diario_usuario`
Agregación automática de datos diarios por usuario.

```sql
CREATE OR REPLACE VIEW resumen_diario_usuario AS
SELECT 
    b.usuario_id,
    DATE(b.fecha_hora) AS fecha,
    SUM(b.consumo_total) AS consumo_dia_kwh,
    SUM(b.produccion_total) AS produccion_dia_kwh,
    SUM(b.balance_neto) AS balance_dia_kwh,
    SUM(b.coste_estimado) AS coste_dia_euros,
    SUM(b.ahorro_estimado) AS ahorro_dia_euros,
    AVG(b.precio_medio_kwh) AS precio_medio_dia
FROM balance_energetico b
GROUP BY b.usuario_id, DATE(b.fecha_hora);
```

### Vista: `analisis_precios`
Estadísticas de precios por día y zona.

```sql
CREATE OR REPLACE VIEW analisis_precios AS
SELECT 
    DATE(fecha_hora) AS fecha,
    zona,
    MIN(precio_kwh) AS precio_min,
    MAX(precio_kwh) AS precio_max,
    AVG(precio_kwh) AS precio_promedio,
    STDDEV(precio_kwh) AS desviacion_estandar
FROM historico_precios
GROUP BY DATE(fecha_hora), zona;
```

---

## 🔧 Procedimientos Almacenados

### `sp_calcular_balance_dia`
Calcula el balance energético de un día específico.

```sql
CALL sp_calcular_balance_dia(1, '2026-03-27');
```

### `sp_obtener_recomendaciones_activas`
Obtiene las 10 recomendaciones más prioritarias no aplicadas.

```sql
CALL sp_obtener_recomendaciones_activas(1);
```

---

## 🚀 Uso desde Python

### Ejemplo 1: Guardar precios históricos

```python
from backend.mysql_manager import mysql_db
from datetime import datetime

# Guardar un precio
mysql_db.guardar_precio(
    fecha_hora=datetime(2026, 3, 27, 14, 0),
    precio_kwh=0.15234,
    zona='ES',
    fuente='ESIOS'
)

# Obtener precios del día
precios = mysql_db.obtener_precios_rango(
    fecha_inicio=datetime(2026, 3, 27, 0, 0),
    fecha_fin=datetime(2026, 3, 27, 23, 59),
    zona='ES'
)
```

### Ejemplo 2: Registrar consumo del usuario

```python
# Registrar consumo
mysql_db.guardar_consumo(
    usuario_id=1,
    fecha_hora=datetime.now(),
    consumo_kwh=2.5,
    dispositivo='Lavadora',
    tipo_medicion='simulado'
)

# Obtener consumo del mes
from datetime import timedelta
consumo = mysql_db.obtener_consumo_usuario(
    usuario_id=1,
    fecha_inicio=datetime.now() - timedelta(days=30),
    fecha_fin=datetime.now()
)
```

### Ejemplo 3: Calcular y guardar balance

```python
# Calcular balance energético
mysql_db.calcular_y_guardar_balance(
    usuario_id=1,
    fecha_hora=datetime.now(),
    consumo_total=15.5,
    produccion_total=12.3,
    precio_kwh=0.15
)

# Obtener resumen del día
resumen = mysql_db.obtener_resumen_diario(
    usuario_id=1,
    fecha=datetime.now()
)
print(f"Consumo: {resumen['consumo_dia_kwh']} kWh")
print(f"Coste: {resumen['coste_dia_euros']} €")
```

---

## 🔐 Configuración de Variables de Entorno

Crear archivo `.env`:

```bash
# Base de datos
DB_TYPE=mysql

# Configuración MySQL
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=smartwatt_user
MYSQL_PASSWORD=smartwatt_pass
MYSQL_DATABASE=smartwatt_db
```

---

## 📝 Instalación del Schema

```bash
# 1. Crear base de datos y usuario
mysql -u root -p << EOF
CREATE DATABASE smartwatt_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'smartwatt_user'@'localhost' IDENTIFIED BY 'smartwatt_pass';
GRANT ALL PRIVILEGES ON smartwatt_db.* TO 'smartwatt_user'@'localhost';
FLUSH PRIVILEGES;
