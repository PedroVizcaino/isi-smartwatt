import sqlite3
import os
from werkzeug.security import generate_password_hash, check_password_hash

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'usuarios.db')


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id       INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre   TEXT    NOT NULL,
            email    TEXT    NOT NULL UNIQUE,
            password TEXT    NOT NULL,
            creado_en DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()


def crear_usuario(nombre, email, password):
    """Registra un nuevo usuario. Devuelve el id creado o None si el email ya existe."""
    hashed = generate_password_hash(password)
    conn = get_db()
    try:
        cursor = conn.execute(
            'INSERT INTO usuarios (nombre, email, password) VALUES (?, ?, ?)',
            (nombre, email, hashed)
        )
        conn.commit()
        return cursor.lastrowid
    except sqlite3.IntegrityError:
        return None
    finally:
        conn.close()


def verificar_usuario(email, password):
    """Verifica las credenciales. Devuelve el usuario como dict o None si falla."""
    conn = get_db()
    row = conn.execute(
        'SELECT * FROM usuarios WHERE email = ?', (email,)
    ).fetchone()
    conn.close()
    if row and check_password_hash(row['password'], password):
        return {'id': row['id'], 'nombre': row['nombre'], 'email': row['email']}
    return None


def obtener_usuario_por_id(user_id):
    """Devuelve los datos públicos de un usuario por su id."""
    conn = get_db()
    row = conn.execute(
        'SELECT id, nombre, email, creado_en FROM usuarios WHERE id = ?', (user_id,)
    ).fetchone()
    conn.close()
    if row:
        return {'id': row['id'], 'nombre': row['nombre'], 'email': row['email'], 'creado_en': row['creado_en']}
    return None
