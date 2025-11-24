# Configuración del Backend para Testing

## Opción 1: Backend Simple con JSON Server + Auth

### Instalación
```bash
npm install -g json-server json-server-auth
```

### Crear `db.json`
```json
{
  "users": [],
  "products": [
    {
      "id": "1",
      "name": "Producto de Prueba 1",
      "description": "Descripción del producto",
      "price": 99.99,
      "imageUrl": "https://via.placeholder.com/300",
      "category": "electronics",
      "stock": 10
    }
  ],
  "orders": []
}
```

### Ejecutar
```bash
json-server --watch db.json --port 3000 --middlewares ./node_modules/json-server-auth
```

### Configurar en Flutter
```dart
// lib/data/api_client.dart
baseUrl: 'http://localhost:3000',
// o para emulador Android:
baseUrl: 'http://10.0.2.2:3000',
```

### Endpoints disponibles:
- POST `/register` - Registro
- POST `/login` - Login
- GET `/600/users/:id` - Usuario (requiere auth)

---

## Opción 2: Backend con Node.js + Express

### Crear `server.js`
```javascript
const express = require('express');
const cors = require('cors');
const jwt = require('jsonwebtoken');
const bodyParser = require('body-parser');

const app = express();
const SECRET_KEY = 'tu_clave_secreta_super_segura';
const users = [];

app.use(cors());
app.use(bodyParser.json());

// Middleware de autenticación
const authenticateToken = (req, res, next) => {
  const authHeader = req.headers['authorization'];
  const token = authHeader && authHeader.split(' ')[1];

  if (!token) return res.sendStatus(401);

  jwt.verify(token, SECRET_KEY, (err, user) => {
    if (err) return res.sendStatus(403);
    req.user = user;
    next();
  });
};

// POST /auth/register
app.post('/auth/register', (req, res) => {
  const { name, email, password } = req.body;

  // Validaciones básicas
  if (!email || !password || !name) {
    return res.status(400).json({ message: 'Faltan datos requeridos' });
  }

  // Verificar si el usuario ya existe
  const existingUser = users.find(u => u.email === email);
  if (existingUser) {
    return res.status(409).json({ message: 'Este email ya está registrado' });
  }

  // Crear usuario
  const user = {
    id: String(users.length + 1),
    name,
    email,
    password, // En producción: hashear con bcrypt
    createdAt: new Date().toISOString(),
  };

  users.push(user);

  // Generar token
  const token = jwt.sign({ id: user.id, email: user.email }, SECRET_KEY, {
    expiresIn: '7d',
  });

  // Retornar sin la contraseña
  const { password: _, ...userWithoutPassword } = user;

  res.status(201).json({
    token,
    user: userWithoutPassword,
  });
});

// POST /auth/login
app.post('/auth/login', (req, res) => {
  const { email, password } = req.body;

  if (!email || !password) {
    return res.status(400).json({ message: 'Email y contraseña requeridos' });
  }

  const user = users.find(u => u.email === email && u.password === password);

  if (!user) {
    return res.status(401).json({ message: 'Credenciales inválidas' });
  }

  // Generar token
  const token = jwt.sign({ id: user.id, email: user.email }, SECRET_KEY, {
    expiresIn: '7d',
  });

  const { password: _, ...userWithoutPassword } = user;

  res.json({
    token,
    user: userWithoutPassword,
  });
});

// GET /auth/me
app.get('/auth/me', authenticateToken, (req, res) => {
  const user = users.find(u => u.id === req.user.id);

  if (!user) {
    return res.status(404).json({ message: 'Usuario no encontrado' });
  }

  const { password: _, ...userWithoutPassword } = user;
  res.json(userWithoutPassword);
});

// GET /products
app.get('/products', (req, res) => {
  const products = [
    {
      id: '1',
      name: 'iPhone 15 Pro',
      description: 'El último modelo de Apple',
      price: 999.99,
      imageUrl: 'https://via.placeholder.com/300',
      category: 'electronics',
      stock: 5,
    },
    {
      id: '2',
      name: 'Samsung Galaxy S24',
      description: 'Flagship de Samsung',
      price: 899.99,
      imageUrl: 'https://via.placeholder.com/300',
      category: 'electronics',
      stock: 8,
    },
    {
      id: '3',
      name: 'MacBook Pro M3',
      description: 'Laptop profesional de Apple',
      price: 1999.99,
      imageUrl: 'https://via.placeholder.com/300',
      category: 'computers',
      stock: 3,
    },
  ];

  res.json(products);
});

// GET /products/:id
app.get('/products/:id', (req, res) => {
  const { id } = req.params;
  
  const products = [
    {
      id: '1',
      name: 'iPhone 15 Pro',
      description: 'El último modelo de Apple con chip A17 Pro',
      price: 999.99,
      imageUrl: 'https://via.placeholder.com/300',
      category: 'electronics',
      stock: 5,
    },
    // ... más productos
  ];

  const product = products.find(p => p.id === id);

  if (!product) {
    return res.status(404).json({ message: 'Producto no encontrado' });
  }

  res.json(product);
});

const PORT = 3000;
app.listen(PORT, () => {
  console.log(`🚀 Servidor corriendo en http://localhost:${PORT}`);
  console.log('\nEndpoints disponibles:');
  console.log('  POST /auth/register');
  console.log('  POST /auth/login');
  console.log('  GET  /auth/me (requiere token)');
  console.log('  GET  /products');
  console.log('  GET  /products/:id');
});
```

### Instalación de dependencias
```bash
npm init -y
npm install express cors jsonwebtoken body-parser
```

### Ejecutar
```bash
node server.js
```

---

## Opción 3: Usar Mockoon (Recomendado para principiantes)

1. Descargar Mockoon: https://mockoon.com/download/
2. Crear nuevo environment
3. Configurar endpoints:

### POST `/auth/register`
- Status: 201
- Body:
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.mock",
  "user": {
    "id": "{{faker 'datatype.uuid'}}",
    "name": "{{body 'name'}}",
    "email": "{{body 'email'}}",
    "createdAt": "{{now}}"
  }
}
```

### POST `/auth/login`
- Status: 200
- Body: (mismo que register)

### GET `/auth/me`
- Headers required: `Authorization: Bearer *`
- Status: 200
- Body:
```json
{
  "id": "{{faker 'datatype.uuid'}}",
  "name": "Usuario Mock",
  "email": "mock@example.com",
  "createdAt": "{{now}}"
}
```

---

## Testing con cURL

### Registro
```bash
curl -X POST http://localhost:3000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Juan Pérez",
    "email": "juan@example.com",
    "password": "123456"
  }'
```

### Login
```bash
curl -X POST http://localhost:3000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "juan@example.com",
    "password": "123456"
  }'
```

### Obtener usuario (con token)
```bash
curl -X GET http://localhost:3000/auth/me \
  -H "Authorization: Bearer TU_TOKEN_AQUI"
```

---

## Configuración para Emuladores

### Android Emulator
```dart
baseUrl: 'http://10.0.2.2:3000/api',
```

### iOS Simulator
```dart
baseUrl: 'http://localhost:3000/api',
```

### Dispositivo físico (misma red WiFi)
```dart
baseUrl: 'http://192.168.1.XXX:3000/api', // Tu IP local
```

Para encontrar tu IP:
- Windows: `ipconfig`
- Mac/Linux: `ifconfig`
