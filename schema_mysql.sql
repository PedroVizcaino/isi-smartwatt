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
    tarifa_actual VARCHAR(50) DEFAULT 'Variable',
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
    fecha DATETIME NOT NULL,
    precio_kwh DECIMAL(10, 6) NOT NULL COMMENT 'Precio en €/kWh',
    INDEX idx_fecha (fecha)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Histórico de precios de electricidad';

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
    DATE(fecha) AS fecha,
    MIN(precio_kwh) AS precio_min,
    MAX(precio_kwh) AS precio_max,
    AVG(precio_kwh) AS precio_promedio,
    STDDEV(precio_kwh) AS desviacion_estandar
FROM historico_precios
GROUP BY DATE(fecha);

-- ============================================
-- DATOS DE EJEMPLO (OPCIONAL)
-- ============================================


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

DELIMITER ;

-- ============================================
-- ÍNDICES ADICIONALES PARA OPTIMIZACIÓN
-- ============================================

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
