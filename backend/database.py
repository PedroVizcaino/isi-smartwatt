import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash, check_password_hash

# Cargar variables de entorno
load_dotenv()


def get_db():
    """Obtiene una conexión a MySQL con reintentos robustos para Docker"""
    import time
    max_retries = 12
    for i in range(max_retries):
        try:
            conn = mysql.connector.connect(
                host=os.environ.get('MYSQL_HOST', 'localhost'),
                port=int(os.environ.get('MYSQL_PORT', 3306)),
                user=os.environ.get('MYSQL_USER', 'smartwatt_user'),
                password=os.environ.get('MYSQL_PASSWORD', 'SmartWatt2026!'),
                database=os.environ.get('MYSQL_DATABASE', 'smartwatt_db'),
                charset='utf8mb4',
                collation='utf8mb4_unicode_ci'
            )
            return conn
        except Exception as e:
            if i < max_retries - 1:
                print(f"⚠ Intento {i+1}/{max_retries}: Base de datos no lista ({e}). Reintentando en 5s...")
                time.sleep(5)
            else:
                print(f"❌ Error crítico: No se pudo conectar a la base de datos tras {max_retries} intentos.")
                raise


def init_db():
    """Inicializa la tabla de usuarios si no existe (ya debería estar creada por schema_mysql.sql)"""
    conn = get_db()
    cursor = conn.cursor()
    try:
        # Verificar que la tabla existe
        cursor.execute("SHOW TABLES LIKE 'usuarios'")
        result = cursor.fetchone()
        if result:
            print("✓ Tabla 'usuarios' encontrada en MySQL")
        else:
            print("⚠ Tabla 'usuarios' no encontrada. Ejecuta schema_mysql.sql primero")
    except Error as e:
        print(f"Error verificando tabla usuarios: {e}")
    finally:
        cursor.close()
        conn.close()


def crear_usuario(nombre, email, password):
    """Registra un nuevo usuario en MySQL. Devuelve el id creado o None si el email ya existe."""
    hashed = generate_password_hash(password)
    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute(
            'INSERT INTO usuarios (nombre, email, password) VALUES (%s, %s, %s)',
            (nombre, email, hashed)
        )
        conn.commit()
        return cursor.lastrowid
    except Error as e:
        if e.errno == 1062:  # Duplicate entry error
            return None
        print(f"Error creando usuario: {e}")
        return None
    finally:
        cursor.close()
        conn.close()


def verificar_usuario(email, password):
    """Verifica las credenciales. Devuelve el usuario como dict o None si falla."""
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            'SELECT id, nombre, email, password FROM usuarios WHERE email = %s',
            (email,)
        )
        row = cursor.fetchone()
        if row and check_password_hash(row['password'], password):
            return {'id': row['id'], 'nombre': row['nombre'], 'email': row['email']}
        return None
    finally:
        cursor.close()
        conn.close()


def obtener_usuario_por_id(user_id):
    """Devuelve los datos públicos de un usuario por su id."""
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            'SELECT id, nombre, email, creado_en FROM usuarios WHERE id = %s',
            (user_id,)
        )
        row = cursor.fetchone()
        if row:
            return {
                'id': row['id'],
                'nombre': row['nombre'],
                'email': row['email'],
                'creado_en': row['creado_en'].isoformat() if row['creado_en'] else None
            }
        return None
    finally:
        cursor.close()
        conn.close()
