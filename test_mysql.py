#!/usr/bin/env python3
"""
Script de verificación de MySQL para ISI-SmartWatt
Verifica que la base de datos esté configurada correctamente y prueba todas las operaciones
"""

import sys
from datetime import datetime, timedelta
import mysql.connector
from mysql.connector import Error

# Colores para terminal
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_header(text):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.END}\n")

def print_success(text):
    print(f"{Colors.GREEN}✓ {text}{Colors.END}")

def print_error(text):
    print(f"{Colors.RED}✗ {text}{Colors.END}")

def print_info(text):
    print(f"{Colors.YELLOW}ℹ {text}{Colors.END}")

# Configuración de conexión
MYSQL_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'user': 'smartwatt_user',
    'password': 'smartwatt_pass',
    'database': 'smartwatt_db'
}

def test_connection():
    """Prueba la conexión a MySQL"""
    print_header("1. PRUEBA DE CONEXIÓN")
    try:
        conn = mysql.connector.connect(**MYSQL_CONFIG)
        if conn.is_connected():
            db_info = conn.get_server_info()
            print_success(f"Conectado a MySQL Server versión {db_info}")
            
            cursor = conn.cursor()
            cursor.execute("SELECT DATABASE();")
            record = cursor.fetchone()
            print_success(f"Base de datos activa: {record[0]}")
            
            cursor.close()
            conn.close()
            return True
    except Error as e:
        print_error(f"Error de conexión: {e}")
        return False

def test_tables():
    """Verifica que todas las tablas existan"""
    print_header("2. VERIFICACIÓN DE TABLAS")
    
    expected_tables = [
        'usuarios',
        'historico_precios',
        'perfil_consumo',
        'perfil_produccion',
        'balance_energetico',
        'alertas_usuario',
        'dispositivos_usuario',
        'recomendaciones_ia',
        'patrones_consumo'
    ]
    
    try:
        conn = mysql.connector.connect(**MYSQL_CONFIG)
        cursor = conn.cursor()
        
        cursor.execute("SHOW TABLES;")
        tables = [table[0] for table in cursor.fetchall()]
        
        all_exist = True
        for table in expected_tables:
            if table in tables:
                print_success(f"Tabla '{table}' existe")
            else:
                print_error(f"Tabla '{table}' NO existe")
                all_exist = False
        
        print(f"\n{Colors.BOLD}Total de tablas: {len(tables)}{Colors.END}")
        
        cursor.close()
        conn.close()
        return all_exist
    except Error as e:
        print_error(f"Error verificando tablas: {e}")
        return False

def test_insert_data():
    """Prueba insertar datos de ejemplo"""
    print_header("3. PRUEBA DE INSERCIÓN DE DATOS")
    
    try:
        conn = mysql.connector.connect(**MYSQL_CONFIG)
        cursor = conn.cursor()
        
        # 1. Insertar precio
        print_info("Insertando precio de ejemplo...")
        fecha_hora = datetime.now().replace(minute=0, second=0, microsecond=0)
        cursor.execute('''
            INSERT INTO historico_precios (fecha_hora, precio_kwh, zona, fuente)
            VALUES (%s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE precio_kwh = %s
        ''', (fecha_hora, 0.15234, 'ES', 'TEST', 0.15234))
        conn.commit()
        print_success(f"Precio insertado: {fecha_hora} - 0.15234 €/kWh")
        
        # 2. Verificar inserción
        cursor.execute('''
            SELECT COUNT(*) FROM historico_precios WHERE fuente = 'TEST'
        ''')
        count = cursor.fetchone()[0]
        print_success(f"Registros de prueba en historico_precios: {count}")
        
        cursor.close()
        conn.close()
        return True
    except Error as e:
        print_error(f"Error insertando datos: {e}")
        return False

def test_queries():
    """Prueba consultas SQL"""
    print_header("4. PRUEBA DE CONSULTAS")
    
    try:
        conn = mysql.connector.connect(**MYSQL_CONFIG)
        cursor = conn.cursor(dictionary=True)
        
        # Consulta 1: Contar registros
        cursor.execute("SELECT COUNT(*) as total FROM historico_precios")
        result = cursor.fetchone()
        print_info(f"Total de precios en histórico: {result['total']}")
        
        # Consulta 2: Último precio insertado
        cursor.execute('''
            SELECT fecha_hora, precio_kwh, zona, fuente 
            FROM historico_precios 
            ORDER BY creado_en DESC 
            LIMIT 1
        ''')
        ultimo = cursor.fetchone()
        if ultimo:
            print_success(f"Último precio: {ultimo['fecha_hora']} - {ultimo['precio_kwh']} €/kWh ({ultimo['fuente']})")
        
        # Consulta 3: Verificar vistas
        cursor.execute("SHOW FULL TABLES WHERE Table_type = 'VIEW'")
        views = cursor.fetchall()
        if views:
            print_success(f"Vistas creadas: {len(views)}")
            for view in views:
                print(f"  - {list(view.values())[0]}")
        else:
            print_info("No hay vistas creadas")
        
        cursor.close()
        conn.close()
        return True
    except Error as e:
        print_error(f"Error en consultas: {e}")
        return False

def test_mysql_manager():
    """Prueba el módulo mysql_manager.py"""
    print_header("5. PRUEBA DE MYSQL MANAGER")
    
    try:
        from backend.mysql_manager import mysql_db
        print_success("Módulo mysql_manager importado correctamente")
        
        # Probar guardar precio
        print_info("Probando guardar_precio()...")
        result = mysql_db.guardar_precio(
            fecha_hora=datetime.now().replace(minute=0, second=0, microsecond=0),
            precio_kwh=0.18456,
            zona='ES',
            fuente='MANAGER_TEST'
        )
        if result:
            print_success("Precio guardado correctamente")
        else:
            print_error("Error guardando precio")
        
        # Probar obtener precios
        print_info("Probando obtener_precios_rango()...")
        precios = mysql_db.obtener_precios_rango(
            fecha_inicio=datetime.now() - timedelta(days=1),
            fecha_fin=datetime.now() + timedelta(days=1),
            zona='ES'
        )
        print_success(f"Obtenidos {len(precios)} registros de precios")
        
        # Probar estadísticas
        print_info("Probando obtener_estadisticas_precios()...")
        stats = mysql_db.obtener_estadisticas_precios(
            fecha_inicio=datetime.now() - timedelta(days=7),
            fecha_fin=datetime.now(),
            zona='ES'
        )
        if stats and stats.get('num_registros', 0) > 0:
            print_success(f"Estadísticas obtenidas: {stats['num_registros']} registros")
            print(f"  - Precio mínimo: {stats.get('precio_min', 'N/A')}")
            print(f"  - Precio máximo: {stats.get('precio_max', 'N/A')}")
            print(f"  - Precio promedio: {stats.get('precio_promedio', 'N/A')}")
        else:
            print_info("No hay suficientes datos para estadísticas")
        
        return True
    except Exception as e:
        print_error(f"Error en mysql_manager: {e}")
        return False

def cleanup_test_data():
    """Limpia datos de prueba"""
    print_header("6. LIMPIEZA DE DATOS DE PRUEBA")
    
    try:
        conn = mysql.connector.connect(**MYSQL_CONFIG)
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM historico_precios WHERE fuente IN ('TEST', 'MANAGER_TEST')")
        deleted = cursor.rowcount
        conn.commit()
        
        print_success(f"Eliminados {deleted} registros de prueba")
        
        cursor.close()
        conn.close()
        return True
    except Error as e:
        print_error(f"Error limpiando datos: {e}")
        return False

def main():
    """Ejecuta todas las pruebas"""
    print(f"\n{Colors.BOLD}{'='*60}{Colors.END}")
    print(f"{Colors.BOLD}VERIFICACIÓN DE BASE DE DATOS MYSQL - ISI-SmartWatt{Colors.END}")
    print(f"{Colors.BOLD}{'='*60}{Colors.END}")
    
    tests = [
        ("Conexión a MySQL", test_connection),
        ("Verificación de Tablas", test_tables),
        ("Inserción de Datos", test_insert_data),
        ("Consultas SQL", test_queries),
        ("MySQL Manager", test_mysql_manager),
        ("Limpieza de Datos", cleanup_test_data)
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print_error(f"Excepción en {name}: {e}")
            results.append((name, False))
    
    # Resumen
    print_header("RESUMEN DE PRUEBAS")
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        if result:
            print_success(f"{name}")
        else:
            print_error(f"{name}")
    
    print(f"\n{Colors.BOLD}Resultado: {passed}/{total} pruebas pasadas{Colors.END}")
    
    if passed == total:
        print(f"\n{Colors.GREEN}{Colors.BOLD}✓ ¡Todas las pruebas pasaron exitosamente!{Colors.END}")
        print(f"{Colors.GREEN}La base de datos MySQL está lista para usar.{Colors.END}\n")
        return 0
    else:
        print(f"\n{Colors.RED}{Colors.BOLD}✗ Algunas pruebas fallaron{Colors.END}")
        print(f"{Colors.RED}Revisa los errores anteriores.{Colors.END}\n")
        return 1

if __name__ == "__main__":
    sys.exit(main())
