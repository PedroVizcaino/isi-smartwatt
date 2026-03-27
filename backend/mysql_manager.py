"""
Gestor de base de datos MySQL para ISI-SmartWatt
Funciones para interactuar con el histórico de precios y perfil de uso
"""

import os
import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
import mysql.connector
from mysql.connector import Error


class MySQLManager:
    """Clase para gestionar operaciones con MySQL"""
    
    def __init__(self):
        self.config = {
            'host': os.environ.get('MYSQL_HOST', 'localhost'),
            'port': int(os.environ.get('MYSQL_PORT', 3306)),
            'user': os.environ.get('MYSQL_USER', 'smartwatt_user'),
            'password': os.environ.get('MYSQL_PASSWORD', 'smartwatt_pass'),
            'database': os.environ.get('MYSQL_DATABASE', 'smartwatt_db'),
            'charset': 'utf8mb4',
            'collation': 'utf8mb4_unicode_ci'
        }
    
    def get_connection(self):
        """Obtiene una conexión a MySQL"""
        try:
            conn = mysql.connector.connect(**self.config)
            return conn
        except Error as e:
            print(f"Error conectando a MySQL: {e}")
            raise
    
    # ===== HISTÓRICO DE PRECIOS =====
    
    def guardar_precio(self, fecha_hora: datetime, precio_kwh: float, 
                       zona: str = 'ES', fuente: str = 'ESIOS', 
                       tipo_tarifa: str = 'PVPC') -> bool:
        """
        Guarda un precio en el histórico
        
        Args:
            fecha_hora: Fecha y hora del precio
            precio_kwh: Precio en €/kWh
            zona: Zona geográfica
            fuente: Fuente de datos
            tipo_tarifa: Tipo de tarifa
        
        Returns:
            True si se guardó correctamente, False en caso contrario
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO historico_precios (fecha_hora, precio_kwh, zona, fuente, tipo_tarifa)
                VALUES (%s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE precio_kwh = %s, fuente = %s
            ''', (fecha_hora, precio_kwh, zona, fuente, tipo_tarifa, precio_kwh, fuente))
            conn.commit()
            return True
        except Error as e:
            print(f"Error guardando precio: {e}")
            conn.rollback()
            return False
        finally:
            cursor.close()
            conn.close()
    
    def guardar_precios_batch(self, precios: List[Dict]) -> int:
        """
        Guarda múltiples precios en batch
        
        Args:
            precios: Lista de diccionarios con datos de precio
        
        Returns:
            Número de registros insertados/actualizados
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        count = 0
        
        try:
            for precio in precios:
                cursor.execute('''
                    INSERT INTO historico_precios (fecha_hora, precio_kwh, zona, fuente, tipo_tarifa)
                    VALUES (%s, %s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE precio_kwh = VALUES(precio_kwh)
                ''', (
                    precio['fecha_hora'],
                    precio['precio_kwh'],
                    precio.get('zona', 'ES'),
                    precio.get('fuente', 'ESIOS'),
                    precio.get('tipo_tarifa', 'PVPC')
                ))
                count += cursor.rowcount
            conn.commit()
            return count
        except Error as e:
            print(f"Error guardando precios en batch: {e}")
            conn.rollback()
            return 0
        finally:
            cursor.close()
            conn.close()
    
    def obtener_precios_rango(self, fecha_inicio: datetime, fecha_fin: datetime, 
                              zona: str = 'ES') -> List[Dict]:
        """
        Obtiene precios en un rango de fechas
        
        Args:
            fecha_inicio: Fecha inicial
            fecha_fin: Fecha final
            zona: Zona geográfica
        
        Returns:
            Lista de diccionarios con datos de precios
        """
        conn = self.get_connection()
        cursor = conn.cursor(dictionary=True)
        
        try:
            cursor.execute('''
                SELECT fecha_hora, precio_kwh, zona, fuente, tipo_tarifa
                FROM historico_precios
                WHERE fecha_hora BETWEEN %s AND %s AND zona = %s
                ORDER BY fecha_hora
            ''', (fecha_inicio, fecha_fin, zona))
            
            return cursor.fetchall()
        finally:
            cursor.close()
            conn.close()
    
    def obtener_precio_hora(self, fecha_hora: datetime, zona: str = 'ES') -> Optional[float]:
        """Obtiene el precio de una hora específica"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT precio_kwh
                FROM historico_precios
                WHERE fecha_hora = %s AND zona = %s
                LIMIT 1
            ''', (fecha_hora, zona))
            
            result = cursor.fetchone()
            return result[0] if result else None
        finally:
            cursor.close()
            conn.close()
    
    def obtener_estadisticas_precios(self, fecha_inicio: datetime, fecha_fin: datetime,
                                     zona: str = 'ES') -> Dict:
        """Obtiene estadísticas de precios en un periodo"""
        conn = self.get_connection()
        cursor = conn.cursor(dictionary=True)
        
        try:
            cursor.execute('''
                SELECT 
                    MIN(precio_kwh) as precio_min,
                    MAX(precio_kwh) as precio_max,
                    AVG(precio_kwh) as precio_promedio,
                    STDDEV(precio_kwh) as desviacion_estandar,
                    COUNT(*) as num_registros
                FROM historico_precios
                WHERE fecha_hora BETWEEN %s AND %s AND zona = %s
            ''', (fecha_inicio, fecha_fin, zona))
            
            return cursor.fetchone() or {}
        finally:
            cursor.close()
            conn.close()
    
    # ===== PERFIL DE CONSUMO =====
    
    def guardar_consumo(self, usuario_id: int, fecha_hora: datetime, 
                       consumo_kwh: float, dispositivo: str = 'General',
                       tipo_medicion: str = 'simulado', notas: str = None,
                       metadata: Dict = None) -> bool:
        """
        Guarda un registro de consumo
        
        Args:
            usuario_id: ID del usuario
            fecha_hora: Fecha y hora del consumo
            consumo_kwh: Consumo en kWh
            dispositivo: Nombre del dispositivo
            tipo_medicion: Tipo de medición (real, simulado, estimado)
            notas: Notas adicionales
            metadata: Metadatos adicionales en formato JSON
        
        Returns:
            True si se guardó correctamente
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        metadata_json = json.dumps(metadata) if metadata else None
        
        try:
            cursor.execute('''
                INSERT INTO perfil_consumo 
                (usuario_id, fecha_hora, consumo_kwh, dispositivo, tipo_medicion, notas, metadata)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            ''', (usuario_id, fecha_hora, consumo_kwh, dispositivo, tipo_medicion, notas, metadata_json))
            conn.commit()
            return True
        except Error as e:
            print(f"Error guardando consumo: {e}")
            conn.rollback()
            return False
        finally:
            cursor.close()
            conn.close()
    
    def obtener_consumo_usuario(self, usuario_id: int, fecha_inicio: datetime, 
                               fecha_fin: datetime) -> List[Dict]:
        """Obtiene el histórico de consumo del usuario"""
        conn = self.get_connection()
        cursor = conn.cursor(dictionary=True)
        
        try:
            cursor.execute('''
                SELECT fecha_hora, consumo_kwh, dispositivo, tipo_medicion, notas, metadata
                FROM perfil_consumo
                WHERE usuario_id = %s AND fecha_hora BETWEEN %s AND %s
                ORDER BY fecha_hora
            ''', (usuario_id, fecha_inicio, fecha_fin))
            
            return cursor.fetchall()
        finally:
            cursor.close()
            conn.close()
    
    def obtener_consumo_total_dia(self, usuario_id: int, fecha: datetime) -> float:
        """Obtiene el consumo total de un día"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT COALESCE(SUM(consumo_kwh), 0) as total
                FROM perfil_consumo
                WHERE usuario_id = %s 
                AND DATE(fecha_hora) = DATE(%s)
            ''', (usuario_id, fecha))
            
            result = cursor.fetchone()
            return float(result[0]) if result else 0.0
        finally:
            cursor.close()
            conn.close()
    
    # ===== PERFIL DE PRODUCCIÓN =====
    
    def guardar_produccion(self, usuario_id: int, fecha_hora: datetime,
                          produccion_solar: float = 0, produccion_eolica: float = 0,
                          produccion_otras: float = 0, tipo_medicion: str = 'simulado',
                          condiciones: Dict = None) -> bool:
        """
        Guarda un registro de producción energética
        
        Args:
            usuario_id: ID del usuario
            fecha_hora: Fecha y hora
            produccion_solar: Producción solar en kWh
            produccion_eolica: Producción eólica en kWh
            produccion_otras: Otras fuentes en kWh
            tipo_medicion: Tipo de medición
            condiciones: Condiciones climáticas
        
        Returns:
            True si se guardó correctamente
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        condiciones_json = json.dumps(condiciones) if condiciones else None
        
        try:
            cursor.execute('''
                INSERT INTO perfil_produccion 
                (usuario_id, fecha_hora, produccion_solar_kwh, produccion_eolica_kwh, 
                 produccion_otras_kwh, tipo_medicion, condiciones_climaticas)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            ''', (usuario_id, fecha_hora, produccion_solar, produccion_eolica,
                  produccion_otras, tipo_medicion, condiciones_json))
            conn.commit()
            return True
        except Error as e:
            print(f"Error guardando producción: {e}")
            conn.rollback()
            return False
        finally:
            cursor.close()
            conn.close()
    
    def obtener_produccion_usuario(self, usuario_id: int, fecha_inicio: datetime,
                                   fecha_fin: datetime) -> List[Dict]:
        """Obtiene el histórico de producción del usuario"""
        conn = self.get_connection()
        cursor = conn.cursor(dictionary=True)
        
        try:
            cursor.execute('''
                SELECT fecha_hora, produccion_solar_kwh, produccion_eolica_kwh,
                       produccion_otras_kwh, tipo_medicion, condiciones_climaticas
                FROM perfil_produccion
                WHERE usuario_id = %s AND fecha_hora BETWEEN %s AND %s
                ORDER BY fecha_hora
            ''', (usuario_id, fecha_inicio, fecha_fin))
            
            return cursor.fetchall()
        finally:
            cursor.close()
            conn.close()
    
    # ===== BALANCE ENERGÉTICO =====
    
    def calcular_y_guardar_balance(self, usuario_id: int, fecha_hora: datetime,
                                   consumo_total: float, produccion_total: float,
                                   precio_kwh: float = None) -> bool:
        """
        Calcula y guarda el balance energético
        
        Args:
            usuario_id: ID del usuario
            fecha_hora: Fecha y hora
            consumo_total: Consumo total en kWh
            produccion_total: Producción total en kWh
            precio_kwh: Precio del kWh
        
        Returns:
            True si se guardó correctamente
        """
        balance_neto = produccion_total - consumo_total
        coste_estimado = None
        ahorro_estimado = None
        
        if precio_kwh:
            if balance_neto < 0:
                coste_estimado = abs(balance_neto) * precio_kwh
            else:
                ahorro_estimado = balance_neto * precio_kwh
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO balance_energetico 
                (usuario_id, fecha_hora, consumo_total, produccion_total, balance_neto, 
                 coste_estimado, ahorro_estimado, precio_medio_kwh)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE 
                    consumo_total = VALUES(consumo_total),
                    produccion_total = VALUES(produccion_total),
                    balance_neto = VALUES(balance_neto),
                    coste_estimado = VALUES(coste_estimado),
                    ahorro_estimado = VALUES(ahorro_estimado),
                    precio_medio_kwh = VALUES(precio_medio_kwh)
            ''', (usuario_id, fecha_hora, consumo_total, produccion_total, balance_neto,
                  coste_estimado, ahorro_estimado, precio_kwh))
            conn.commit()
            return True
        except Error as e:
            print(f"Error guardando balance: {e}")
            conn.rollback()
            return False
        finally:
            cursor.close()
            conn.close()
    
    def obtener_balance_usuario(self, usuario_id: int, fecha_inicio: datetime,
                               fecha_fin: datetime) -> List[Dict]:
        """Obtiene el balance energético del usuario"""
        conn = self.get_connection()
        cursor = conn.cursor(dictionary=True)
        
        try:
            cursor.execute('''
                SELECT fecha_hora, consumo_total, produccion_total, balance_neto,
                       coste_estimado, ahorro_estimado, precio_medio_kwh
                FROM balance_energetico
                WHERE usuario_id = %s AND fecha_hora BETWEEN %s AND %s
                ORDER BY fecha_hora
            ''', (usuario_id, fecha_inicio, fecha_fin))
            
            return cursor.fetchall()
        finally:
            cursor.close()
            conn.close()
    
    def obtener_resumen_diario(self, usuario_id: int, fecha: datetime) -> Dict:
        """Obtiene resumen del día desde la vista"""
        conn = self.get_connection()
        cursor = conn.cursor(dictionary=True)
        
        try:
            cursor.execute('''
                SELECT *
                FROM resumen_diario_usuario
                WHERE usuario_id = %s AND fecha = DATE(%s)
            ''', (usuario_id, fecha))
            
            return cursor.fetchone() or {}
        finally:
            cursor.close()
            conn.close()
    
    # ===== ALERTAS =====
    
    def crear_alerta(self, usuario_id: int, tipo_alerta: str, titulo: str,
                    mensaje: str, prioridad: str = 'media',
                    datos_adicionales: Dict = None) -> bool:
        """Crea una nueva alerta para el usuario"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        datos_json = json.dumps(datos_adicionales) if datos_adicionales else None
        
        try:
            cursor.execute('''
                INSERT INTO alertas_usuario 
                (usuario_id, tipo_alerta, titulo, mensaje, prioridad, fecha_alerta, datos_adicionales)
                VALUES (%s, %s, %s, %s, %s, NOW(), %s)
            ''', (usuario_id, tipo_alerta, titulo, mensaje, prioridad, datos_json))
            conn.commit()
            return True
        except Error as e:
            print(f"Error creando alerta: {e}")
            conn.rollback()
            return False
        finally:
            cursor.close()
            conn.close()
    
    def obtener_alertas_no_leidas(self, usuario_id: int) -> List[Dict]:
        """Obtiene alertas no leídas del usuario"""
        conn = self.get_connection()
        cursor = conn.cursor(dictionary=True)
        
        try:
            cursor.execute('''
                SELECT id, tipo_alerta, titulo, mensaje, prioridad, fecha_alerta
                FROM alertas_usuario
                WHERE usuario_id = %s AND leida = FALSE
                ORDER BY prioridad DESC, fecha_alerta DESC
            ''', (usuario_id,))
            
            return cursor.fetchall()
        finally:
            cursor.close()
            conn.close()
    
    # ===== DISPOSITIVOS =====
    
    def agregar_dispositivo(self, usuario_id: int, nombre: str, tipo: str,
                           potencia_watts: int, consumo_estimado_kwh: float = None,
                           horario_uso: str = None) -> bool:
        """Agrega un dispositivo al perfil del usuario"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO dispositivos_usuario 
                (usuario_id, nombre, tipo, potencia_watts, consumo_estimado_kwh, horario_uso)
                VALUES (%s, %s, %s, %s, %s, %s)
            ''', (usuario_id, nombre, tipo, potencia_watts, consumo_estimado_kwh, horario_uso))
            conn.commit()
            return True
        except Error as e:
            print(f"Error agregando dispositivo: {e}")
            conn.rollback()
            return False
        finally:
            cursor.close()
            conn.close()
    
    def obtener_dispositivos_usuario(self, usuario_id: int) -> List[Dict]:
        """Obtiene los dispositivos del usuario"""
        conn = self.get_connection()
        cursor = conn.cursor(dictionary=True)
        
        try:
            cursor.execute('''
                SELECT id, nombre, tipo, potencia_watts, consumo_estimado_kwh, horario_uso, activo
                FROM dispositivos_usuario
                WHERE usuario_id = %s AND activo = TRUE
                ORDER BY tipo, nombre
            ''', (usuario_id,))
            
            return cursor.fetchall()
        finally:
            cursor.close()
            conn.close()


# Instancia global
mysql_db = MySQLManager()
