# CRMECOMMERCE
python v:3.11
JWT
ORM
Postgresql
.env(manejarvariables de entorno)
swagger
pruebas Postman


mi_proyecto/
├── manage.py
├── mi_proyecto/
│   ├── __init__.py
│   ├── settings.py
│   └── urls.py                # Enrutador principal del proyecto
│
├── core/                        # Lógica de negocio y modelos de datos (el "cerebro")
│   ├── common/                # Modelos o lógica compartida (ej. un modelo base con UUIDs)
│   ├── crm/
│   │   ├── models.py          # Modelos de Clientes, Leads, Interacciones...
│   │   ├── services.py        # Lógica de negocio: create_lead(), convert_to_client(), etc.
│   │   └── ...
│   └── ecommerce/
│       ├── models.py          # Modelos de Productos, Órdenes, Carritos...
│       ├── services.py        # Lógica de negocio: process_order(), apply_discount(), etc.
│       └── ...
│
├── api/                         # Capa de presentación. Lo único que React y Flutter "ven"
│   ├── v1/                      # MUY RECOMENDADO: Versiona tu API desde el día 1
│   │   ├── __init__.py
│   │   ├── urls.py            # Enrutador para todos los endpoints de la v1
│   │   ├── crm/
│   │   │   ├── serializers.py # Define cómo se ven los objetos CRM en JSON
│   │   │   └── views.py       # Endpoints: /api/v1/leads/, /api/v1/clients/
│   │   │
│   │   ├── ecommerce/
│   │   │   ├── serializers.py # Define cómo se ven los objetos E-commerce en JSON
│   │   │   └── views.py       # Endpoints: /api/v1/products/, /api/v1/orders/
│   │   │
│   │   └── users/
│   │       ├── serializers.py
│   │       └── views.py       # Endpoints: /api/v1/auth/login/, /api/v1/auth/register/
│   │
│   └── pagination.py          # Clases de paginación personalizadas para toda la API
│   └── permissions.py         # Permisos personalizados
│
└── requirements.txt
