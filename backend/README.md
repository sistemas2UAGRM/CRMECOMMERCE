# CRM & E-commerce System Documentation

## Overview

This project integrates a Customer Relationship Management (CRM) system with an E-commerce platform using Django REST Framework. The system provides a comprehensive solution for managing customer interactions, sales processes, and online retail operations.

## Technology Stack

- **Python**: 3.11
- **Framework**: Django & Django REST Framework
- **Database**: PostgreSQL
- **Authentication**: JWT (JSON Web Tokens)
- **API Documentation**: Swagger
- **Testing**: Postman
- **Environment Management**: .env files

## Project Structure

```
mi_proyecto/
├── manage.py
├── mi_proyecto/
│   ├── __init__.py
│   ├── settings.py
│   └── urls.py                # Main project router
│
├── core/                      # Business logic and data models
│   ├── common/                # Shared models/logic
│   ├── crm/
│   │   ├── models.py          # Client, Lead, Interaction models
│   │   ├── services.py        # Business logic
│   │   └── ...
│   └── ecommerce/
│       ├── models.py          # Product, Order, Cart models
│       ├── services.py        # Business logic
│       └── ...
│
├── api/                       # Presentation layer
│   ├── v1/                    # API versioning
│   │   ├── __init__.py
│   │   ├── urls.py            # Router for v1 endpoints
│   │   ├── crm/
│   │   │   ├── serializers.py # JSON representation of CRM objects
│   │   │   └── views.py       # CRM endpoints
│   │   │
│   │   ├── ecommerce/
│   │   │   ├── serializers.py # JSON representation of E-commerce objects
│   │   │   └── views.py       # E-commerce endpoints
│   │   │
│   │   └── users/
│   │       ├── serializers.py
│   │       └── views.py       # Auth endpoints
│   │
│   ├── pagination.py          # Custom pagination classes
│   └── permissions.py         # Custom permissions
│
└── requirements.txt
```

## Installation & Setup

### 1. Clone the Repository

```bash
git clone https://github.com/sistemas2UAGRM/CRMECOMMERCE.git
cd CRMECOMMERCE
```

### 2. Create a Virtual Environment

```bash
python -m venv venv
```

Activate the virtual environment:

- Windows:
  ```bash
  venv\Scripts\activate
  ```
- macOS/Linux:
  ```bash
  source venv/bin/activate
  ```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the project root:

```
# Database Configuration
DB_NAME=crmecommerce
DB_USER=postgres
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432

# Django Settings
SECRET_KEY=your_secret_key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# JWT Settings
JWT_SECRET_KEY=your_jwt_secret
JWT_ACCESS_TOKEN_LIFETIME=1h
JWT_REFRESH_TOKEN_LIFETIME=24h
```

### 5. Database Setup

```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Create Superuser

```bash
python manage.py createsuperuser
```

### 7. Run Development Server

```bash
python manage.py runserver
```

## API Documentation

The API is documented using Swagger UI. Access it at:

```
http://localhost:8000/api/schema/swagger-ui/
```

### Key Endpoints

#### Authentication

- `POST /api/v1/auth/register/` - Register a new user
- `POST /api/v1/auth/login/` - Login and get JWT tokens
- `POST /api/v1/auth/refresh/` - Refresh JWT token
- `POST /api/v1/auth/logout/` - Logout (invalidate token)

#### CRM

- `GET /api/v1/crm/leads/` - List all leads
- `POST /api/v1/crm/leads/` - Create a new lead
- `GET /api/v1/crm/leads/{id}/` - Get lead details
- `PUT /api/v1/crm/leads/{id}/` - Update lead
- `DELETE /api/v1/crm/leads/{id}/` - Delete lead
- `POST /api/v1/crm/leads/{id}/convert/` - Convert lead to client

Similar endpoints exist for clients and interactions.

#### E-commerce

- `GET /api/v1/ecommerce/products/` - List all products
- `POST /api/v1/ecommerce/orders/` - Create a new order
- `GET /api/v1/ecommerce/cart/` - View current user's cart

## Testing with Postman

A Postman collection is available for testing the API endpoints. Import the collection from:

```
docs/postman/CRMECOMMERCE_API.postman_collection.json
```

### Environment Setup in Postman

1. Create a new environment in Postman
2. Add the following variables:
   - `base_url`: http://localhost:8000
   - `access_token`: (leave empty, will be filled after login)
   - `refresh_token`: (leave empty, will be filled after login)

3. Use the login request to authenticate and automatically set the tokens

## Development Workflow

1. Create feature branch from development branch
2. Implement changes and write tests
3. Submit pull request for review
4. After approval, merge into development
5. Periodically merge development into main for releases

## Features

### CRM Module

- Lead management
- Client tracking
- Interaction history
- Sales pipeline visualization
- Task scheduling and reminders
- Reporting and analytics

### E-commerce Module

- Product catalog management
- Order processing
- Shopping cart functionality
- Discount and promotion handling
- Inventory management
- Customer reviews and ratings

## License

[MIT License](LICENSE)

---

*This documentation is maintained by the Sistemas2UAGRM team.*
