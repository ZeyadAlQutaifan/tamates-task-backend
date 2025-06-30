# Tamatem Plus - Gaming Store Backend

**Technical Assignment - Software Engineer Position**  
**Developer: Zeyad Alqutaifan**

## Overview

FastAPI backend service for digital gaming items marketplace with JWT authentication, order processing, and payment simulation.
Built as part of Tamatem Games technical assignment.
## Features

- JWT Authentication (login/register)
- Product catalog with CSV auto-import
- Order management system
- Mock payment processing
- Audit logging middleware
- Location-based filtering (JO/SA)
- Comprehensive error handling

## Tech Stack

- FastAPI
- SQLAlchemy ORM
- JWT Authentication
- PostgreSQL/SQLite
- Pydantic validation
- Middleware for auth & auditing

## Prerequisites

- Python 3.8+
- pip package manager

## Installation

1. **Clone and setup**
```bash
git clone https://github.com/ZeyadAlQutaifan/tamates-task-backend.git
cd tamates-task-backend
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Run the application**
```bash
python main.py
```

Server starts at `http://localhost:8020`

## Project Structure

```
├── main.py                 # FastAPI app with CSV auto-import
├── requirements.txt        # Dependencies
├── database.py            # SQLAlchemy configuration
├── dependencies.py        # Dependency injection
├── items.csv             # Product data (auto-imported)
├── services/             # Business logic
│   ├── auth_service.py
│   ├── products_service.py
│   ├── order_service.py
│   └── payment_service.py
├── routers/              # API endpoints
│   ├── auth_router.py
│   ├── products_router.py
│   ├── orders_router.py
│   └── payment_router.py
├── models/               # Database models
│   ├── users_models.py
│   ├── product_models.py
│   ├── order_models.py
│   └── audit_models.py
├── middlewares/          # Custom middleware
│   ├── auth_middleware.py
│   └── audit_middleware.py
└── config/
    └── setting.py        # Configuration
```

## Key Features

### Auto CSV Import
- Products automatically imported from `items.csv` on startup
- Skips import if products already exist
- 100 gaming items with JO/SA locations

### Authentication
- JWT-based authentication
- User registration and login
- Token refresh capability
- Protected routes with middleware

### Order Processing
- Order initiation with payment URL generation
- Mock payment processing
- Order status tracking (INITIATED → SUCCESS/FAILED)
- User order history with pagination

## API Endpoints

### Authentication
```
POST /auth/login      - User login
POST /auth/register   - User registration  
GET  /auth/me         - Get current user
```

### Products
```
GET  /products/           - List products (paginated)
GET  /products/{id}       - Get product details
```

### Orders
```
POST /orders/initiate     - Create order
GET  /orders/             - Get user orders
GET  /orders/{id}         - Get specific order
```

### Payments
```
GET  /payment/{id}        - Get payment details
POST /payment/process     - Process payment
```

## Configuration

The app uses default SQLite database and auto-creates tables on startup.

**Key Settings:**
- **Host**: localhost
- **Port**: 8020
- **Database**: SQLite (auto-created)
- **CORS**: Enabled for localhost:3000

## Testing the API

**1. Register a user:**
```bash
curl -X POST http://localhost:8020/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"test","email":"test@example.com","password":"password123"}'
```

**2. Login:**
```bash
curl -X POST http://localhost:8020/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123"}'
```

**3. Get products (with token):**
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8020/products/
```

## Database Models

- **User**: id, username, email, hashed_password, role
- **Product**: id, title, description, price, location
- **Order**: id, user_id, product_id, quantity, price, status
- **PaymentRequest**: payment_id, reference_id, price, status

## Mock Payment Testing

Payment simulation logic:
- Cards ending in "0000" → Payment fails
- All other cards → Payment succeeds
- Generates random transaction references

## API Documentation

- **Swagger UI**: `http://localhost:8020/docs`
- **ReDoc**: `http://localhost:8020/redoc`

## Security Features

- JWT token authentication
- Password hashing with bcrypt
- CORS protection
- Request/response audit logging
- Input validation with Pydantic

## Middleware

- **AuthMiddleware**: JWT validation for protected routes
- **AuditMiddleware**: Logs all requests/responses
- **CORS**: Frontend integration

## Dependencies

Main packages:
```
fastapi==0.104.1
sqlalchemy==2.0.41
pydantic==2.11.7
PyJWT==2.10.1
bcrypt==3.2.2
uvicorn==0.24.0
```

## Troubleshooting

**Port 8020 in use:**
```bash
# Kill existing process
sudo lsof -ti:8020 | xargs kill -9
```

**Database issues:**
```bash
# Delete database file to reset
rm *.db
python main.py  # Will recreate automatically
```

**Import errors:**
```bash
pip install -r requirements.txt --force-reinstall
```

## Contact

**Zeyad Alqutaifan**  
Email: zeyada.alqutaifan@gmail.com