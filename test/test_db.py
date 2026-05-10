import mysql.connector
import os
from dotenv import load_dotenv

# Intentar cargar .env si existe
load_dotenv()

def test_database_connection():
    print("\n--- Test: Conexión Base de Datos (MySQL) ---")
    
    # Valores para entorno Docker
    db_config = {
        'host': 'smartwatt-db',
        'user': 'smartwatt_user',
        'password': 'SmartWatt2026!',
        'database': 'smartwatt_db',
        'port': 3306
    }

    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        
        # Verificar si hay tablas
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        
        print(f"✅ Conexión exitosa a MySQL.")
        print(f"📊 Tablas encontradas: {len(tables)}")
        for (table_name,) in tables:
            print(f"   - {table_name}")
            
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Error conectando a la base de datos: {e}")
        print("Asegúrate de que el contenedor de la DB esté funcionando con 'make status'")

if __name__ == "__main__":
    test_database_connection()
