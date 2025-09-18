# Backend - Sistema de CRM y E-commerce

Este es el backend del sistema de CRM y E-commerce desarrollado con Django y Django REST Framework.

## 🚀 Características Principales

- **Autenticación y Gestión de Usuarios**
  - Registro y autenticación de usuarios
  - Perfiles de usuario personalizados
  - Roles y permisos personalizables

- **Gestión de Productos**
  - Catálogo de productos con categorías
  - Control de inventario
  - Gestión de precios

- **Carrito de Compras**
  - Gestión de carritos de compra
  - Seguimiento de estado del carrito
  - Cálculo automático de totales

## 🛠️ Tecnologías Utilizadas

- **Framework Principal**: Django 5.2.6
- **API REST**: Django REST Framework 3.16.1
- **Autenticación**: JWT (JSON Web Tokens)
- **Base de Datos**: SQLite (desarrollo) / PostgreSQL (producción)
- **Documentación de API**: Swagger/OpenAPI

## 📦 Requisitos del Sistema

- Python 3.8+
- pip (gestor de paquetes de Python)
- Virtualenv (recomendado)

## 🚀 Configuración del Entorno

1. **Clonar el repositorio**
   ```bash
   git clone [URL_DEL_REPOSITORIO]
   cd CRMECOMMERCE/Backend
   ```

2. **Crear y activar entorno virtual**
   ```bash
   python -m venv venv
   .\venv\Scripts\activate  # Windows
   source venv/bin/activate  # Linux/Mac
   ```

3. **Instalar dependencias**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configurar variables de entorno**
   Crear un archivo `.env` en la raíz del proyecto con las siguientes variables:
   ```
   SECRET_KEY=tu_clave_secreta_aqui
   DEBUG=True
   ALLOWED_HOSTS=localhost,127.0.0.1
   ```

5. **Aplicar migraciones**
   ```bash
   python manage.py migrate
   ```

6. **Crear superusuario (opcional)**
   ```bash
   python manage.py createsuperuser
   ```

7. **Iniciar el servidor de desarrollo**
   ```bash
   python manage.py runserver
   ```

## 📚 Estructura del Proyecto

```
Backend/
├── Main/               # Configuración principal de Django
├── api/                # Endpoints de la API
├── core/               # Aplicación principal
│   ├── common/         # Modelos y utilidades comunes
│   ├── ecommerce/      # Lógica de comercio electrónico
│   └── users/          # Gestión de usuarios y autenticación
├── manage.py           # Script de gestión de Django
└── requirements.txt    # Dependencias del proyecto
```

## 📝 Modelos Principales

La arquitectura de la base de datos se basa en el siguiente diagrama de clases:

### Usuarios y Autenticación
- **User**: Modelo de usuario personalizado que hereda de `AbstractUser` de Django. Contiene campos como `email`, `fecha_de_nacimiento`, `sexo`, `celular`, además de los campos estándar.
- **Rol (Group)**: Se utiliza el modelo `Group` de Django para gestionar los roles de los usuarios (ej. Administrador, Cliente).
- **Permiso (Permission)**: Se utiliza el modelo `Permission` de Django para definir permisos específicos que pueden ser asignados a los roles.

### E-commerce
- **Categoria**: Almacena las categorías de los productos.
- **Producto**: Contiene la información detallada de cada producto, incluyendo precio, descripción y garantía.
- **Stock**: Gestiona el inventario de cada producto, con campos para `stock_min` y `stock_actual`.
- **Carrito**: Representa el carrito de compras de un usuario. Tiene un estado (`ABIERTO`, `CERRADO`, `ABANDONADO`) y un total.
- **CarritoProducto**: Tabla intermedia que conecta un `Carrito` con un `Producto`, especificando la `cantidad` de cada producto en el carrito.

### Comunes
- **Bitacora**: Registra acciones importantes en el sistema, como inicios de sesión o modificaciones críticas. Guarda la acción, fecha, dirección IP y el usuario que la realizó.

## 🔒 Autenticación

El sistema utiliza JWT (JSON Web Tokens) para la autenticación. Los endpoints protegidos requieren incluir el token en el encabezado:

```
Authorization: Bearer <tu_token_aqui>
```

## 📄 Documentación de la API

La documentación de la API está disponible en:
- Swagger UI: `http://localhost:8000/swagger/`
- ReDoc: `http://localhost:8000/redoc/`

## 🧪 Ejecutar Pruebas

```bash
python manage.py test
```

## 🐛 Solución de Problemas

- **Error de migraciones**: Si hay problemas con las migraciones, intenta:
  ```bash
  python manage.py makemigrations
  python manage.py migrate
  ```

- **Problemas de dependencias**: Asegúrate de tener todas las dependencias instaladas:
  ```bash
  pip install -r requirements.txt
  ```

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.
