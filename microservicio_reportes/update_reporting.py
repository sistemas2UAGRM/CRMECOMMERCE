# Script para actualizar reporting.py con soporte multi-tenant
import re

# Leer el archivo
with open('app/reporting.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Actualizar todas las firmas de funciones _get_* para aceptar conn
content = re.sub(
    r'def (_get_\w+)\(params: dict, date_range: dict\)',
    r'def \1(params: dict, date_range: dict, conn)',
    content
)

# 2. Actualizar def _not_implemented también
content = re.sub(
    r'def _not_implemented\(params: dict, date_range: dict\)',
    r'def _not_implemented(params: dict, date_range: dict, conn)',
    content
)

# 3. Reemplazar pd.read_sql(sql_query, engine, ...) por pd.read_sql(sql_query, conn, ...)
content = re.sub(
    r'pd\.read_sql\(([^,]+), engine',
    r'pd.read_sql(\1, conn',
    content
)

# Guardar el archivo actualizado
with open('app/reporting.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Archivo reporting.py actualizado correctamente")
print("- Todas las funciones _get_* ahora aceptan 'conn' como parámetro")
print("- Todos los usos de 'engine' en pd.read_sql() fueron reemplazados por 'conn'")
