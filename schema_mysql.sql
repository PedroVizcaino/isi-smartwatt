-- ============================================
-- Schema MySQL para ISI-SmartWatt
-- Sistema de Gestión de Energía Inteligente
-- ============================================

-- Crear base de datos
CREATE DATABASE IF NOT EXISTS smartwatt_db
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;

USE smartwatt_db;

-- ============================================
-- Tabla: usuarios
-- Almacena información de los usuarios del sistema
-- ============================================
CREATE TABLE IF NOT EXISTS usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    ubicacion VARCHAR(100) DEFAULT 'Madrid',
    tarifa_actual VARCHAR(50) DEFAULT 'PVPC',
    preferencias JSON,
    creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    actualizado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_email (email)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Usuarios del sistema SmartWatt';

-- ============================================
-- Tabla: historico_precios
-- Almacena el histórico de precios de electricidad
-- ============================================
CREATE TABLE IF NOT EXISTS historico_precios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    fecha_hora DATETIME NOT NULL,
    precio_kwh DECIMAL(10, 6) NOT NULL COMMENT 'Precio en €/kWh',
    zona VARCHAR(50) DEFAULT 'ES' COMMENT 'Zona geográfica',
    fuente VARCHAR(50) DEFAULT 'ESIOS' COMMENT 'Fuente de datos (ESIOS, REE, etc)',
    tipo_tarifa VARCHAR(50) DEFAULT 'PVPC',
    creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_fecha_hora (fecha_hora),
    INDEX idx_zona_fecha (zona, fecha_hora),
    UNIQUE KEY unique_precio (fecha_hora, zona, tipo_tarifa)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Histórico de precios de electricidad';

-- ============================================
-- Tabla: perfil_consumo
-- Almacena el histórico de consumo energético del usuario
-- ============================================
CREATE TABLE IF NOT EXISTS perfil_consumo (
    id INT AUTO_INCREMENT PRIMARY KEY,
    usuario_id INT NOT NULL,
    fecha_hora DATETIME NOT NULL,
    consumo_kwh DECIMAL(10, 4) NOT NULL COMMENT 'Consumo en kWh',
    dispositivo VARCHAR(100) DEFAULT 'General' COMMENT 'Dispositivo consumidor',
    tipo_medicion ENUM('real', 'simulado', 'estimado') DEFAULT 'simulado',
    notas TEXT,
    metadata JSON COMMENT 'Información adicional',
    creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE,
    INDEX idx_usuario_fecha (usuario_id, fecha_hora),
    INDEX idx_fecha_hora (fecha_hora),
    INDEX idx_tipo_medicion (tipo_medicion)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Perfil de consumo energético del usuario';

-- ============================================
-- Tabla: perfil_produccion
-- Almacena el histórico de producción energética renovable
-- ============================================
CREATE TABLE IF NOT EXISTS perfil_produccion (
    id INT AUTO_INCREMENT PRIMARY KEY,
    usuario_id INT NOT NULL,
    fecha_hora DATETIME NOT NULL,
    produccion_solar_kwh DECIMAL(10, 4) DEFAULT 0 COMMENT 'Producción solar en kWh',
    produccion_eolica_kwh DECIMAL(10, 4) DEFAULT 0 COMMENT 'Producción eólica en kWh',
    produccion_otras_kwh DECIMAL(10, 4) DEFAULT 0 COMMENT 'Otras fuentes en kWh',
    tipo_medicion ENUM('real', 'simulado', 'estimado') DEFAULT 'simulado',
    condiciones_climaticas JSON COMMENT 'Datos climáticos (temperatura, nubes, viento, etc)',
    creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE,
    INDEX idx_usuario_fecha (usuario_id, fecha_hora),
    INDEX idx_fecha_hora (fecha_hora)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Perfil de producción energética renovable';

-- ============================================
-- Tabla: balance_energetico
-- Almacena el balance neto entre consumo y producción
-- ============================================
CREATE TABLE IF NOT EXISTS balance_energetico (
    id INT AUTO_INCREMENT PRIMARY KEY,
    usuario_id INT NOT NULL,
    fecha_hora DATETIME NOT NULL,
    consumo_total DECIMAL(10, 4) NOT NULL COMMENT 'Consumo total en kWh',
    produccion_total DECIMAL(10, 4) NOT NULL COMMENT 'Producción total en kWh',
    balance_neto DECIMAL(10, 4) NOT NULL COMMENT 'Balance (producción - consumo)',
    coste_estimado DECIMAL(10, 4) COMMENT 'Coste en € si balance negativo',
    ahorro_estimado DECIMAL(10, 4) COMMENT 'Ahorro en € si balance positivo',
    precio_medio_kwh DECIMAL(10, 6) COMMENT 'Precio medio aplicado',
    creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE,
    INDEX idx_usuario_fecha (usuario_id, fecha_hora),
    UNIQUE KEY unique_balance (usuario_id, fecha_hora)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Balance energético (consumo vs producción)';

-- ============================================
-- Tabla: alertas_usuario
-- Almacena alertas y recomendaciones personalizadas
-- ============================================
CREATE TABLE IF NOT EXISTS alertas_usuario (
    id INT AUTO_INCREMENT PRIMARY KEY,
    usuario_id INT NOT NULL,
    tipo_alerta ENUM('precio_alto', 'precio_bajo', 'exceso_consumo', 'recomendacion', 'mantenimiento') NOT NULL,
    titulo VARCHAR(200) NOT NULL,
    mensaje TEXT NOT NULL,
    prioridad ENUM('baja', 'media', 'alta') DEFAULT 'media',
    leida BOOLEAN DEFAULT FALSE,
    fecha_alerta DATETIME NOT NULL,
    datos_adicionales JSON,
    creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE,
    INDEX idx_usuario_leida (usuario_id, leida),
    INDEX idx_fecha (fecha_alerta),
    INDEX idx_tipo (tipo_alerta)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Alertas y notificaciones para usuarios';

-- ============================================
-- Tabla: dispositivos_usuario
-- Catálogo de dispositivos eléctricos del usuario
-- ============================================
CREATE TABLE IF NOT EXISTS dispositivos_usuario (
    id INT AUTO_INCREMENT PRIMARY KEY,
    usuario_id INT NOT NULL,
    nombre VARCHAR(100) NOT NULL,
    tipo VARCHAR(50) NOT NULL COMMENT 'lavadora, nevera, calefacción, etc',
    potencia_watts INT NOT NULL COMMENT 'Potencia nominal en watts',
    consumo_estimado_kwh DECIMAL(10, 4) COMMENT 'Consumo estimado diario',
    horario_uso VARCHAR(50) COMMENT 'Horario típico de uso',
    activo BOOLEAN DEFAULT TRUE,
    creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    actualizado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE,
    INDEX idx_usuario (usuario_id),
    INDEX idx_tipo (tipo)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Dispositivos eléctricos del usuario';

-- ============================================
-- Tabla: recomendaciones_ia
-- Almacena recomendaciones generadas por IA
-- ============================================
CREATE TABLE IF NOT EXISTS recomendaciones_ia (
    id INT AUTO_INCREMENT PRIMARY KEY,
    usuario_id INT NOT NULL,
    tipo_recomendacion ENUM('optimizacion', 'ahorro', 'eficiencia', 'tarifaria') NOT NULL,
    titulo VARCHAR(200) NOT NULL,
    descripcion TEXT NOT NULL,
    ahorro_potencial DECIMAL(10, 2) COMMENT 'Ahorro estimado en €',
    prioridad INT DEFAULT 5 COMMENT 'Prioridad 1-10',
    aplicada BOOLEAN DEFAULT FALSE,
    fecha_recomendacion DATETIME NOT NULL,
    fecha_aplicacion DATETIME,
    modelo_ia VARCHAR(50) COMMENT 'Modelo de IA usado',
    creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE,
    INDEX idx_usuario (usuario_id),
    INDEX idx_aplicada (aplicada)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Recomendaciones generadas por IA';

-- ============================================
-- Tabla: patrones_consumo
-- Patrones de consumo detectados automáticamente
-- ============================================
CREATE TABLE IF NOT EXISTS patrones_consumo (
    id INT AUTO_INCREMENT PRIMARY KEY,
    usuario_id INT NOT NULL,
    tipo_patron ENUM('diario', 'semanal', 'mensual', 'estacional') NOT NULL,
    descripcion VARCHAR(200) NOT NULL,
    hora_pico_inicio TIME,
    hora_pico_fin TIME,
    consumo_promedio DECIMAL(10, 4),
    desviacion_estandar DECIMAL(10, 4),
    confianza DECIMAL(5, 2) COMMENT 'Nivel de confianza 0-100',
    datos_patron JSON COMMENT 'Detalles del patrón detectado',
    fecha_deteccion DATETIME NOT NULL,
    activo BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE,
    INDEX idx_usuario (usuario_id),
    INDEX idx_tipo (tipo_patron)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Patrones de consumo detectados';

-- ============================================
-- VISTAS ÚTILES
-- ============================================

-- Vista: Resumen diario por usuario
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

-- Vista: Análisis de precios
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

-- ============================================
-- DATOS DE EJEMPLO (OPCIONAL)
-- ============================================

-- Insertar usuario de prueba
INSERT INTO usuarios (nombre, email, password, ubicacion, tarifa_actual) VALUES
('Usuario Demo', 'demo@smartwatt.com', 'hashed_password_here', 'Madrid', 'PVPC')
ON DUPLICATE KEY UPDATE nombre=nombre;

-- Insertar precios de ejemplo para hoy
INSERT INTO historico_precios (fecha_hora, precio_kwh, zona) VALUES
(CONCAT(CURDATE(), ' 00:00:00'), 0.15234, 'ES'),
(CONCAT(CURDATE(), ' 01:00:00'), 0.14156, 'ES'),
(CONCAT(CURDATE(), ' 02:00:00'), 0.13789, 'ES')
ON DUPLICATE KEY UPDATE precio_kwh=precio_kwh;

-- ============================================
-- PROCEDIMIENTOS ALMACENADOS
-- ============================================

DELIMITER //

-- Procedimiento: Calcular balance del día
CREATE PROCEDURE sp_calcular_balance_dia(
    IN p_usuario_id INT,
    IN p_fecha DATE
)
BEGIN
    SELECT 
        DATE(fecha_hora) AS fecha,
        SUM(consumo_total) AS consumo_total_dia,
        SUM(produccion_total) AS produccion_total_dia,
        SUM(balance_neto) AS balance_neto_dia,
        SUM(COALESCE(coste_estimado, 0)) AS coste_total_dia,
        SUM(COALESCE(ahorro_estimado, 0)) AS ahorro_total_dia
    FROM balance_energetico
    WHERE usuario_id = p_usuario_id
    AND DATE(fecha_hora) = p_fecha
    GROUP BY DATE(fecha_hora);
END //

-- Procedimiento: Obtener recomendaciones activas
CREATE PROCEDURE sp_obtener_recomendaciones_activas(
    IN p_usuario_id INT
)
BEGIN
    SELECT 
        tipo_recomendacion,
        titulo,
        descripcion,
        ahorro_potencial,
        prioridad,
        fecha_recomendacion
    FROM recomendaciones_ia
    WHERE usuario_id = p_usuario_id
    AND aplicada = FALSE
    ORDER BY prioridad DESC, fecha_recomendacion DESC
    LIMIT 10;
END //

DELIMITER ;

-- ============================================
-- ÍNDICES ADICIONALES PARA OPTIMIZACIÓN
-- ============================================

-- Índices compuestos para consultas frecuentes
CREATE INDEX idx_consumo_usuario_tipo_fecha 
ON perfil_consumo(usuario_id, tipo_medicion, fecha_hora);

CREATE INDEX idx_produccion_usuario_fecha 
ON perfil_produccion(usuario_id, fecha_hora DESC);

CREATE INDEX idx_balance_fecha_desc 
ON balance_energetico(usuario_id, fecha_hora DESC);

-- ============================================
-- TRIGGERS
-- ============================================

DELIMITER //

-- Trigger: Actualizar timestamp en usuarios
CREATE TRIGGER tr_usuarios_before_update
BEFORE UPDATE ON usuarios
FOR EACH ROW
BEGIN
    SET NEW.actualizado_en = CURRENT_TIMESTAMP;
END //

DELIMITER ;

-- ============================================
-- FIN DEL SCHEMA
-- ============================================
