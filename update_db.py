import os
import mysql.connector
from dotenv import load_dotenv

def execute_schema():
    print("--- Conectando a la base de datos usando las credenciales de .env ---")
    load_dotenv()
    
    try:
        # Nos conectamos inicialmente sin seleccionar la base de datos
        # por si necesitamos crearla (CREATE DATABASE)
        conn = mysql.connector.connect(
            host=os.getenv('MYSQL_HOST', 'localhost'),
            port=int(os.getenv('MYSQL_PORT', 3306)),
            user=os.getenv('MYSQL_USER', 'root'),
            password=os.getenv('MYSQL_PASSWORD', '')
        )
        cursor = conn.cursor()
        
        with open('schema_mysql.sql', 'r', encoding='utf-8') as f:
            sql_script = f.read()
            
        statements = []
        current_statement = []
        delimiter = ";"
        
        lines = sql_script.split('\n')
        for line in lines:
            stripped = line.strip()
            # Ignorar líneas vacías y comentarios (si no están dentro de un statement multi-línea complejo)
            if not stripped or (stripped.startswith('--') and not current_statement):
                continue
                
            if stripped.startswith('DELIMITER'):
                delimiter = stripped.split()[1]
                continue
                
            current_statement.append(line)
            
            if stripped.endswith(delimiter):
                stmt = '\n'.join(current_statement)
                if delimiter != ';':
                    stmt = stmt.rstrip()[:-len(delimiter)].strip()
                else:
                    stmt = stmt.rstrip()[:-1].strip()
                
                if stmt:
                    statements.append(stmt)
                current_statement = []
                
        # Ejecutar los statements recolectados
        for stmt in statements:
            if stmt:
                try:
                    cursor.execute(stmt)
                except mysql.connector.Error as err:
                    print(f"Advertencia/Error al ejecutar: {err}\nEn el statement: {stmt[:50]}...")
                    
        conn.commit()
        print("--- Base de datos actualizada con éxito sin usar sudo ---")
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Error de conexión o ejecución: {e}")

if __name__ == '__main__':
    execute_schema()
