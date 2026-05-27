# Shop AI 🛒 — A Scalable E-Commerce Platform built with Django & PostgreSQL

A production-grade e-commerce project built in two layers — a **full-stack Django website** and a **REST API** powered by Django REST Framework.  
Designed with clean architecture principles — layered services, repository pattern, DRY mixins, and meaningful test coverage.

---

## 🚀 Features

### Website (Django)
- Full e-commerce frontend with product catalog, cart, and checkout
- Stripe payment integration (webhooks, payment intents, failure handling)
- 90%+ pytest coverage with GitHub Actions CI

### REST API (DRF)
- JWT authentication (register, login, token refresh)
- Product & variant management with image handling
- DB-backed cart system (session-independent)
- Order management with simulated payment flow
- Interactive Swagger documentation

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Backend | Django 5, Django REST Framework |
| Database | PostgreSQL |
| Auth | SimpleJWT |
| Testing | Pytest, pytest-django |
| Docs | drf-spectacular (Swagger / ReDoc) |
| CI | GitHub Actions |
| Environment | django-environ |

---

## 🏗️ Architecture

The project follows a **layered architecture** separating concerns across:

```
views.py        → HTTP in/out only (thin)
services.py     → business logic
repositories.py → database queries only
serializers.py  → validation & transformation
```

Notable patterns used:
- **ImageMixin** — reusable image upload/delete across Product and Variant models
- **Snapshot pattern** on OrderItems — preserves purchase history even if products are later deleted or modified
- **prefetch_related** on querysets — avoids N+1 query issues
- **Slug-based URLs** — human-readable, SEO-friendly endpoints

---

## 🔐 Authentication

JWT-based authentication via SimpleJWT.

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/v1/auth/register/` | Register new user |
| `POST` | `/api/v1/auth/login/` | Login, returns access + refresh tokens |
| `POST` | `/api/v1/auth/token/refresh/` | Refresh access token |

All protected endpoints require:
```
Authorization: Bearer <access_token>
```

---

## 📦 API Endpoints

### Products
| Method | Endpoint | Auth | Description |
|---|---|---|---|
| `GET` | `/api/v1/products/` | ❌ | List all products |
| `GET` | `/api/v1/products/{slug}/` | ❌ | Product detail |
| `POST` | `/api/v1/products/` | Admin | Create product |
| `PATCH` | `/api/v1/products/{slug}/` | Admin | Update product |
| `DELETE` | `/api/v1/products/{slug}/` | Admin | Delete product |
| `POST` | `/api/v1/products/{slug}/images/upload/` | Admin | Upload product image |
| `DELETE` | `/api/v1/products/{slug}/images/delete/{id}/` | Admin | Delete product image |

### Cart
| Method | Endpoint | Auth | Description |
|---|---|---|---|
| `GET` | `/api/v1/cart/` | ✅ | View cart contents |
| `POST` | `/api/v1/cart/` | ✅ | Add product to cart |
| `PATCH` | `/api/v1/cart/` | ✅ | Update item quantity |
| `DELETE` | `/api/v1/cart/` | ✅ | Remove item from cart |
| `DELETE` | `/api/v1/cart/clear/` | ✅ | Clear entire cart |

### Orders
| Method | Endpoint | Auth | Description |
|---|---|---|---|
| `GET` | `/api/v1/orders/` | ✅ | List authenticated user's orders |
| `GET` | `/api/v1/orders/{order_number}/` | ✅ | Order detail (owner only) |
| `POST` | `/api/v1/orders/` | ✅ | Create order from cart |
| `PATCH` | `/api/v1/orders/{order_number}/` | ✅ | Simulate payment (pending → paid) |

### Users
| Method | Endpoint | Auth | Description |
|---|---|---|---|
| `GET` | `/api/v1/users/` | Admin | List users |
| `GET` | `/api/v1/me/` | ✅ | Authenticated user profile |
| `PATCH` | `/api/v1/me/` | ✅ | Update profile |

---

## 🔄 Core Workflows

### Cart → Order → Payment Flow

```
1. User adds products to cart        POST /cart/
2. User creates order from cart      POST /orders/
   → Order created (status: pending)
   → OrderItems attached immediately with full snapshots
   → Cart remains active
3. User pays order                   PATCH /orders/{order_number}/
   → Status transitions: pending → paid
   → Stock decreased per order item
   → Cart cleared automatically
   → Cancelled/paid orders are immutable
```

### Image Upload Flow

```
POST /products/{slug}/images/upload/   (multipart/form-data)
DELETE /products/{slug}/images/delete/{id}/
→ Handled via ImageMixin shared across Product and Variant viewsets
```

### Order Status Transitions

```
pending → paid        ✅ allowed (via PATCH)
pending → cancelled   ✅ allowed (on payment failure)
paid    → any         ❌ immutable
cancelled → any       ❌ immutable
```

---

## 🧪 Test Coverage

Tests written with **pytest** and **pytest-django**, focused on business-critical flows:

```
tests/
  api_fixtures.py     → shared fixtures (JWT token, seeded cart, pending order)
  test_auth.py        → registration, login, token, protected access
  test_cart.py        → add, duplicate, update, remove, clear, unauthenticated
  test_orders.py      → creation, empty cart rejection, payment flow,
                        invalid transitions, cross-user access (404)
```

Product CRUD endpoints follow standard DRF patterns and were tested manually via Swagger UI. Priority test coverage given to auth, cart, and order flows which contain custom business logic.

---

## 💳 Payment

Stripe integration is **intentionally excluded** from this API.

A full Stripe implementation — including payment intents, webhook handling, and failure recovery — is available in the [website version of this project](https://github.com/SylvioDev/shop_ai).

Payment is simulated in the API by updating order status to `paid` via `PATCH /orders/{order_number}/`, which triggers stock decrease and cart clearing — identical to what happens post-Stripe webhook in production.

---

## 📖 API Documentation

Interactive documentation auto-generated via **drf-spectacular**:

| URL | Description |
|---|---|
| `/api/v1/schema/swagger/` | Swagger UI — interactive, try endpoints live |
| `/api/v1/schema/redoc/` | ReDoc — clean read-only documentation |
| `/api/v1/schema/` | Raw OpenAPI 3.0 schema (JSON) |

---

## ⚙️ Local Development

### 1. Clone the repo
```bash
git clone https://github.com/SylvioDev/shop_ai.git
cd shop_ai
```

### 2. Create virtual environment
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure environment
```bash
cp .env.example .env
# Fill in your values (DB, SECRET_KEY, etc.)
```

### 5. Run migrations
```bash
export DJANGO_SETTINGS_MODULE=shop_ai.settings.local
python manage.py migrate
```

### 6. Start the development server
```bash
python manage.py runserver --settings=shop_ai.settings.local 0.0.0.0:8000
```

### 7. Open your browser

**Website:**
```
http://localhost:8000/products/
```

**API Documentation (Swagger):**
```
http://localhost:8000/api/v1/schema/swagger/
```

---

## 🧩 Planned Improvements

- **Redis** — cart caching for performance (currently PostgreSQL JSONField)
- **Celery** — async order confirmation emails
- **Rate limiting** — per-user throttling on sensitive endpoints
- **API versioning** — `/api/v2/` with backward compatibility

---

## 🤝 Contributing

1. Fork the repository
2. Create a branch: `git checkout -b feature/your-feature`
3. Commit: `git commit -m 'feat: add your feature'`
4. Push: `git push origin feature/your-feature`
5. Open a Pull Request
