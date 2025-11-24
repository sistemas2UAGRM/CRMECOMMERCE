import os
from sqlalchemy import create_engine
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configuración de la base de datos
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/dbname")

# Crear engine de SQLAlchemy
try:
    engine = create_engine(
        DATABASE_URL,
        connect_args={
            "sslmode": "require",
            "connect_timeout": 10,
        } if DATABASE_URL.startswith("postgresql") else {},
        pool_pre_ping=True,
        pool_recycle=3600,
    )
    print(f"✅ Motor de base de datos configurado correctamente")
except Exception as e:
    print(f"❌ Error al configurar el motor de base de datos: {e}")
    engine = None
