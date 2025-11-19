# Script para inicializar base de datos SQLite de respaldo
import sqlite3
import os

def init_sqlite_db():
    """Inicializa la base de datos SQLite con tablas básicas para respaldo"""

    db_path = "reportes_local.db"
    if os.path.exists(db_path):
        print(f"Base de datos SQLite ya existe: {db_path}")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Crear tablas básicas basadas en los modelos del backend
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS pedidos_pedido (
            id INTEGER PRIMARY KEY,
            creado_en TEXT DEFAULT CURRENT_TIMESTAMP,
            total_pedido REAL DEFAULT 0,
            estado TEXT DEFAULT 'PENDIENTE'
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS productos_producto (
            id INTEGER PRIMARY KEY,
            nombre TEXT,
            precio REAL DEFAULT 0,
            stock INTEGER DEFAULT 0
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users_user (
            id INTEGER PRIMARY KEY,
            username TEXT,
            email TEXT,
            fecha_registro TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Insertar algunos datos de ejemplo
    cursor.execute("INSERT INTO pedidos_pedido (total_pedido, estado) VALUES (150.50, 'PAGADO')")
    cursor.execute("INSERT INTO pedidos_pedido (total_pedido, estado) VALUES (299.99, 'ENVIADO')")
    cursor.execute("INSERT INTO pedidos_pedido (total_pedido, estado) VALUES (75.25, 'ENTREGADO')")

    cursor.execute("INSERT INTO productos_producto (nombre, precio, stock) VALUES ('Producto A', 25.99, 10)")
    cursor.execute("INSERT INTO productos_producto (nombre, precio, stock) VALUES ('Producto B', 49.99, 5)")
    cursor.execute("INSERT INTO productos_producto (nombre, precio, stock) VALUES ('Producto C', 15.50, 20)")

    conn.commit()
    conn.close()

    print(f"✅ Base de datos SQLite inicializada: {db_path}")
    print("⚠️  NOTA: Esta es una base de datos de respaldo con datos de ejemplo.")
    print("   Para datos reales, conecta a PostgreSQL configurando DATABASE_URL correctamente.")

if __name__ == "__main__":
    init_sqlite_db()