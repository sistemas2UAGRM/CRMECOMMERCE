# app/reporting.py
import pandas as pd
import io
from sqlalchemy import create_engine, text
from .core.config import DATABASE_URL
from fastapi import HTTPException

from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib import colors
import openpyxl

try:
    # Configuración SSL para conexiones a bases de datos externas (como Aiven Cloud)
    engine = create_engine(
        DATABASE_URL,
        connect_args={
            "sslmode": "require",
            "connect_timeout": 10,
        },
        pool_pre_ping=True,  # Verifica que la conexión esté activa antes de usarla
        pool_recycle=3600,   # Recicla conexiones cada hora
    )

    # Probar la conexión
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
    print("Conexión a la base de datos PostgreSQL establecida exitosamente.")

except Exception as e:
    print(f"Error al conectar a la base de datos PostgreSQL: {e}")
    print("Intentando usar SQLite como respaldo...")

    try:
        # Usar SQLite como respaldo
        import os
        db_path = "reportes_local.db"

        # Inicializar base de datos SQLite si no existe
        if not os.path.exists(db_path):
            print("Inicializando base de datos SQLite de respaldo...")
            import sqlite3
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            # Crear tablas básicas
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS pedidos_pedido (
                    id INTEGER PRIMARY KEY,
                    fecha_creacion TEXT DEFAULT CURRENT_TIMESTAMP,
                    total REAL DEFAULT 0,
                    estado TEXT DEFAULT 'pendiente',
                    cliente_id INTEGER
                )
            ''')

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS productos_producto (
                    id INTEGER PRIMARY KEY,
                    nombre TEXT,
                    precio REAL DEFAULT 0
                )
            ''')

            # Insertar algunos datos de ejemplo
            cursor.execute("INSERT INTO pedidos_pedido (total, estado) VALUES (150.50, 'pagado')")
            cursor.execute("INSERT INTO pedidos_pedido (total, estado) VALUES (299.99, 'enviado')")
            cursor.execute("INSERT INTO pedidos_pedido (total, estado) VALUES (75.25, 'entregado')")

            cursor.execute("INSERT INTO productos_producto (nombre, precio) VALUES ('Producto A', 25.99)")
            cursor.execute("INSERT INTO productos_producto (nombre, precio) VALUES ('Producto B', 49.99)")
            cursor.execute("INSERT INTO productos_producto (nombre, precio) VALUES ('Producto C', 15.50)")

            conn.commit()
            conn.close()
            print("✅ Base de datos SQLite inicializada con datos de ejemplo.")

        engine = create_engine(f"sqlite:///{db_path}")
        print("Conexión a SQLite establecida exitosamente (modo respaldo).")
        print("⚠️  ADVERTENCIA: Usando base de datos local. Los datos pueden no estar actualizados.")

    except Exception as e2:
        print(f"Error al conectar a SQLite: {e2}")
        engine = None

# ==============================================================================
# --- LÓGICA DE CONSULTAS SQL (BASADA EN TUS MODELOS) ---
# ==============================================================================
# Cada función _get_... sabe cómo construir y ejecutar una consulta SQL.
def _get_ventas_totales(params: dict, date_range: dict, conn) -> pd.DataFrame:
    sql_query = text("""
        SELECT 
            DATE(fecha_creacion) as fecha, 
            COUNT(id) as cantidad_pedidos,
            SUM(total) as ventas_totales
        FROM pedidos_pedido
        WHERE 
            fecha_creacion BETWEEN :start_date AND :end_date
            AND estado IN ('pagado', 'enviado', 'entregado')
        GROUP BY DATE(fecha_creacion)
        ORDER BY fecha;
    """)
    return pd.read_sql(sql_query, conn, params=date_range)

def _get_ticket_promedio(params: dict, date_range: dict, conn) -> pd.DataFrame:
    sql_query = text("""
        SELECT 
            DATE(fecha_creacion) as fecha, 
            COUNT(id) as cantidad_pedidos,
            SUM(total) as ventas_totales,
            AVG(total) as ticket_promedio
        FROM pedidos_pedido
        WHERE 
            fecha_creacion BETWEEN :start_date AND :end_date
            AND estado IN ('pagado', 'enviado', 'entregado')
        GROUP BY DATE(fecha_creacion)
        ORDER BY fecha;
    """)
    return pd.read_sql(sql_query, conn, params=date_range)

def _get_productos_mas_vendidos(params: dict, date_range: dict, conn) -> pd.DataFrame:
    limit = int(params.get("limit", 10))
    sql_query = text("""
        SELECT 
            p.nombre as producto, 
            p.codigo as sku,
            SUM(dp.cantidad) as total_unidades_vendidas,
            SUM(dp.subtotal) as total_monto_vendido
        FROM pedidos_detallepedido AS dp
        JOIN pedidos_pedido AS pe ON dp.pedido_id = pe.id
        JOIN productos_producto AS p ON dp.producto_id = p.id
        WHERE 
            pe.fecha_creacion BETWEEN :start_date AND :end_date
            AND pe.estado IN ('pagado', 'enviado', 'entregado')
        GROUP BY p.nombre, p.codigo
        ORDER BY total_unidades_vendidas DESC
        LIMIT :limit;
    """)
    return pd.read_sql(sql_query, conn, params={**date_range, "limit": limit})

def _get_ventas_por_categoria(params: dict, date_range: dict, conn) -> pd.DataFrame:
    sql_query = text("""
        SELECT 
            c.nombre as categoria,
            COUNT(DISTINCT pe.id) as cantidad_pedidos,
            SUM(dp.subtotal) as total_monto_vendido
        FROM pedidos_detallepedido AS dp
        JOIN pedidos_pedido AS pe ON dp.pedido_id = pe.id
        JOIN productos_producto AS p ON dp.producto_id = p.id
        JOIN productos_producto_categorias AS pc ON pc.producto_id = p.id
        JOIN productos_categoria AS c ON c.id = pc.categoria_id
        WHERE 
            pe.fecha_creacion BETWEEN :start_date AND :end_date
            AND pe.estado IN ('pagado', 'enviado', 'entregado')
        GROUP BY c.nombre
        ORDER BY total_monto_vendido DESC;
    """)
    return pd.read_sql(sql_query, conn, params=date_range)

def _get_pedidos_por_estado(params: dict, date_range: dict, conn) -> pd.DataFrame:
    metric_map = {
        'pedidos_pendientes': ['pendiente'],
        'pedidos_enviados': ['enviado'],
        'pedidos_entregados': ['entregado'],
        'devoluciones': ['cancelado']
    }
    metric = params.get('metric')
    estados = metric_map.get(metric, ['pendiente'])
    
    sql_query = text("""
        SELECT p.id, p.fecha_creacion, u.email as email_cliente, p.total, p.estado
        FROM pedidos_pedido AS p
        LEFT JOIN users_user AS u ON p.cliente_id = u.id
        WHERE 
            p.fecha_creacion BETWEEN :start_date AND :end_date
            AND p.estado IN :estados
        ORDER BY p.fecha_creacion;
    """)
    return pd.read_sql(sql_query, conn, params={**date_range, "estados": tuple(estados)})

def _get_stock_actual(params: dict, date_range: dict, conn) -> pd.DataFrame:
    where_clause = ""
    if params.get('metric') == 'inventario_bajo':
        where_clause = "WHERE aa.cantidad <= 10"
        
    sql_query = text(f"""
        SELECT 
            p.nombre as producto,
            p.codigo as sku,
            a.nombre as almacen,
            aa.cantidad,
            aa.reservado,
            (aa.cantidad - aa.reservado) as disponible
        FROM productos_articuloalmacen AS aa
        JOIN productos_producto AS p ON aa.producto_id = p.id
        JOIN productos_almacen AS a ON aa.almacen_id = a.id
        {where_clause}
        ORDER BY aa.cantidad ASC, p.nombre;
    """)
    return pd.read_sql(sql_query, conn)

def _get_clientes_nuevos(params: dict, date_range: dict, conn) -> pd.DataFrame:
    sql_query = text("""
        WITH PrimeraCompra AS (
            SELECT 
                u.email as email_cliente,
                u.username,
                MIN(p.fecha_creacion) as fecha_primera_compra,
                COUNT(p.id) as total_pedidos
            FROM pedidos_pedido AS p
            JOIN users_user AS u ON p.cliente_id = u.id
            WHERE p.estado IN ('pagado', 'enviado', 'entregado')
            GROUP BY u.email, u.username
        )
        SELECT 
            pc.email_cliente,
            pc.username,
            pc.fecha_primera_compra,
            pc.total_pedidos
        FROM PrimeraCompra pc
        WHERE pc.fecha_primera_compra BETWEEN :start_date AND :end_date
        ORDER BY pc.fecha_primera_compra DESC;
    """)
    return pd.read_sql(sql_query, conn, params=date_range)

def _get_clientes_frecuentes(params: dict, date_range: dict, conn) -> pd.DataFrame:
    sql_query = text("""
        SELECT 
            u.email as email_cliente,
            u.username,
            COUNT(p.id) as total_pedidos,
            SUM(p.total) as gasto_total
        FROM pedidos_pedido AS p
        JOIN users_user AS u ON p.cliente_id = u.id
        WHERE 
            p.fecha_creacion BETWEEN :start_date AND :end_date
            AND p.estado IN ('pagado', 'enviado', 'entregado')
        GROUP BY u.email, u.username
        HAVING COUNT(p.id) > 1
        ORDER BY total_pedidos DESC;
    """)
    return pd.read_sql(sql_query, conn, params=date_range)

def _get_todos_clientes(params: dict, date_range: dict, conn) -> pd.DataFrame:
    """Lista todos los clientes del sistema con sus datos básicos y estadísticas de compras"""
    sql_query = text("""
        SELECT 
            u.id,
            u.email,
            u.username,
            u.first_name as nombre,
            u.last_name as apellido,
            u.celular as telefono,
            u.is_active as activo,
            u.date_joined as fecha_registro,
            COALESCE(COUNT(DISTINCT p.id), 0) as total_pedidos,
            COALESCE(SUM(CASE WHEN p.estado IN ('pagado', 'enviado', 'entregado') THEN p.total ELSE 0 END), 0) as total_gastado
        FROM users_user AS u
        LEFT JOIN pedidos_pedido AS p ON u.id = p.cliente_id
        GROUP BY u.id, u.email, u.username, u.first_name, u.last_name, u.celular, u.is_active, u.date_joined
        ORDER BY u.date_joined DESC;
    """)
    return pd.read_sql(sql_query, conn)

def _get_inventario_por_categoria(params: dict, date_range: dict, conn) -> pd.DataFrame:
    """Muestra el inventario agrupado por categoría de productos"""
    sql_query = text("""
        SELECT 
            c.nombre as categoria,
            COUNT(DISTINCT p.id) as cantidad_productos,
            SUM(aa.cantidad) as stock_total,
            SUM(aa.reservado) as stock_reservado,
            SUM(aa.cantidad - aa.reservado) as stock_disponible,
            AVG(p.precio) as precio_promedio
        FROM productos_categoria AS c
        JOIN productos_producto_categorias AS pc ON c.id = pc.categoria_id
        JOIN productos_producto AS p ON pc.producto_id = p.id
        LEFT JOIN productos_articuloalmacen AS aa ON p.id = aa.producto_id
        WHERE p.activo = true
        GROUP BY c.nombre
        ORDER BY stock_total DESC;
    """)
    return pd.read_sql(sql_query, conn)

def _not_implemented(params: dict, date_range: dict, conn) -> pd.DataFrame:
    metric = params.get('metric')
    if metric in ['costos_totales', 'margen_beneficio', 'rotacion_inventario']:
        raise NotImplementedError(f"Métrica '{metric}' no implementable. Faltan datos de 'costo'.")
    if metric in ['ventas_por_vendedor', 'ventas_por_sucursal']:
        raise NotImplementedError(f"Métrica '{metric}' no implementable. Faltan modelos 'Vendedor' o 'Sucursal'.")
    if metric in ['efectividad_descuentos', 'cupones_mas_usados', 'ventas_por_campaña', 'campañas_activas']:
        raise NotImplementedError(f"Métrica '{metric}' no implementable. Faltan modelos de 'Marketing'.")
        
    raise NotImplementedError(f"Métrica '{metric}' reconocida, pero aún no implementada en reporting.py.")


# ==============================================================================
# --- DESPACHADOR PRINCIPAL ---
# ==============================================================================
METRIC_HANDLERS = {
    'ventas_totales': _get_ventas_totales,
    'cantidad_pedidos': _get_ventas_totales,
    'ticket_promedio': _get_ticket_promedio,
    'productos_mas_vendidos': _get_productos_mas_vendidos,
    'ventas_por_categoria': _get_ventas_por_categoria,
    'stock_actual': _get_stock_actual,
    'inventario_bajo': _get_stock_actual,
    'pedidos_pendientes': _get_pedidos_por_estado,
    'pedidos_enviados': _get_pedidos_por_estado,
    'pedidos_entregados': _get_pedidos_por_estado,
    'devoluciones': _get_pedidos_por_estado,
    'clientes_nuevos': _get_clientes_nuevos,
    'clientes_frecuentes': _get_clientes_frecuentes,
    'todos_clientes': _get_todos_clientes,
    'lista_clientes': _get_todos_clientes,
    'clientes_sistema': _get_todos_clientes,
    'inventario_por_categoria': _get_inventario_por_categoria,
    
    # No implementados
    'ingresos_brutos': _not_implemented,
    'ingresos_netos': _not_implemented,
    'costos_totales': _not_implemented,
    'margen_beneficio': _not_implemented,
    'rotacion_inventario': _not_implemented,
    'ventas_por_vendedor': _not_implemented,
    'ventas_por_sucursal': _not_implemented,
    'efectividad_descuentos': _not_implemented,
    'ventas_por_campaña': _not_implemented,
    'cupones_mas_usados': _not_implemented,
}

def get_report_dataframe(parametros: dict) -> pd.DataFrame:
    if engine is None:
        raise Exception("Error crítico: El motor de la base de datos no está inicializado.")

    metric = parametros.get('metric')
    date_range = parametros.get('date_range')
    tenant_schema = parametros.get('tenant_schema')
    
    if not metric:
        raise HTTPException(status_code=400, detail="La IA no pudo determinar una métrica.")
    
    # Métricas que no requieren rango de fechas
    metrics_sin_fecha = ['stock_actual', 'inventario_bajo', 'todos_clientes', 'lista_clientes', 
                         'clientes_sistema', 'inventario_por_categoria']
        
    if not date_range and metric not in metrics_sin_fecha:
        raise HTTPException(status_code=400, detail="La IA no pudo determinar un rango de fechas.")
    
    handler_function = METRIC_HANDLERS.get(metric, _not_implemented)
    
    print(f"Generando reporte para métrica: {metric} usando {handler_function.__name__}")
    
    # Validar tenant_schema para prevenir SQL injection
    if tenant_schema:
        import re
        if not re.match(r'^[a-z0-9_]+$', tenant_schema):
            raise HTTPException(status_code=400, detail="Invalid tenant schema name")
        print(f"DEBUG: Configurando search_path para schema: {tenant_schema}")

    # Ejecutar consulta con el schema del tenant
    with engine.connect() as conn:
        # Establecer el search_path al schema del tenant
        if tenant_schema:
            conn.execute(text(f"SET search_path TO {tenant_schema}, public"))
            print(f"DEBUG: search_path configurado a: {tenant_schema}, public")
        
        # Ejecutar la función handler pasando la conexión
        df = handler_function(parametros, date_range, conn)
    
    if df is None or (isinstance(df, pd.DataFrame) and df.empty):
        print(f"Advertencia: La consulta para '{metric}' no devolvió datos.")
        return pd.DataFrame({"mensaje": ["La consulta no devolvió resultados para este rango de fechas."]})

    return df

# --- FUNCIONES DE CONVERSIÓN DE FORMATO ---
def convert_df_to_excel_bytes(df: pd.DataFrame, metric_name: str) -> bytes:
    """
    Toma un DataFrame y lo convierte en los bytes de un archivo Excel.
    """
    for col in df.columns:
        if pd.api.types.is_datetime64_any_dtype(df[col]) and df[col].dt.tz is not None:
            df[col] = df[col].dt.tz_localize(None)

    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name=metric_name[:30]) # Nombre de hoja con límite
    return output.getvalue()

def convert_df_to_pdf_bytes(df: pd.DataFrame, metric_name: str) -> bytes:
    """
    Toma un DataFrame y lo convierte en los bytes de un archivo PDF.
    """
    output = io.BytesIO()
    
    # Configuración del documento
    doc = SimpleDocTemplate(output, pagesize=landscape(letter))
    elements = []
    
    # Convertir DataFrame a una lista de listas + headers
    data = [df.columns.to_list()] + df.values.tolist()
    
    # Crear la tabla
    table = Table(data)
    
    # Estilo de la tabla
    style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ])
    
    table.setStyle(style)
    elements.append(table)
    doc.build(elements)
    
    return output.getvalue()
