# ShopNow — Production-Ready Django E-Commerce

A fully-featured e-commerce website built with Django 4.2 and MySQL.

## 🗂 Project Structure

```
ecommerce/
├── ecommerce/          # Core settings, urls, wsgi
├── users/              # Custom user model, profiles, addresses
├── store/              # Products, categories, brands, reviews, wishlist
├── cart/               # Shopping cart (authenticated + guest), coupons
├── orders/             # Orders, order items, payments, status tracking
├── templates/          # All HTML templates
├── static/             # CSS, JS, images
├── manage.py
├── requirements.txt
└── setup.sh
```

## 🗃 Database Schema (MySQL)

### `users` table (Custom AbstractUser)
| Column | Type | Notes |
|--------|------|-------|
| id | BigInt PK | |
| email | Varchar UNIQUE | Used as USERNAME_FIELD |
| username | Varchar | |
| first_name, last_name | Varchar | |
| phone | Varchar | |
| date_of_birth | Date | |
| is_active, is_staff | Boolean | |
| date_joined, created_at | DateTime | |

### `user_profiles` table
| Column | Type | Notes |
|--------|------|-------|
| id | BigInt PK | |
| user_id | FK → users | OneToOne |
| avatar | ImageField | |
| bio | Text | |
| newsletter_subscribed | Boolean | |

### `addresses` table
| Column | Type | Notes |
|--------|------|-------|
| id | BigInt PK | |
| user_id | FK → users | |
| address_type | Varchar | shipping/billing |
| full_name, address_line1/2, city, state, postal_code, country, phone | Varchar | |
| is_default | Boolean | auto-unsets others |

### `categories` table
| Column | Type | Notes |
|--------|------|-------|
| id | BigInt PK | |
| name | Varchar UNIQUE | |
| slug | Varchar UNIQUE | auto-generated |
| description | Text | |
| image | ImageField | |
| parent_id | FK → categories | self-referential |
| is_active | Boolean | |

### `brands` table
| Column | Type | Notes |
|--------|------|-------|
| id | BigInt PK | |
| name | Varchar UNIQUE | |
| slug | Varchar UNIQUE | |
| logo | ImageField | |
| is_active | Boolean | |

### `products` table
| Column | Type | Notes |
|--------|------|-------|
| id | BigInt PK | |
| category_id | FK → categories | |
| brand_id | FK → brands | nullable |
| name | Varchar | |
| slug | Varchar UNIQUE | auto-generated |
| sku | Varchar UNIQUE | auto UUID-based |
| description | Text | |
| short_description | Varchar(500) | |
| price | Decimal(10,2) | |
| discount_price | Decimal(10,2) | nullable |
| stock | PositiveInt | |
| image | ImageField | |
| weight | Decimal | |
| is_active, is_featured | Boolean | |
| created_at, updated_at | DateTime | |

### `product_images` table
| Column | Type | Notes |
|--------|------|-------|
| product_id | FK → products | |
| image | ImageField | |
| is_primary | Boolean | |
| order | PositiveInt | |

### `product_specifications` table
| Column | Type | Notes |
|--------|------|-------|
| product_id | FK → products | |
| name | Varchar | |
| value | Varchar | |

### `reviews` table
| Column | Type | Notes |
|--------|------|-------|
| id | BigInt PK | |
| product_id | FK → products | |
| user_id | FK → users | |
| rating | SmallInt 1-5 | |
| title | Varchar | |
| body | Text | |
| is_approved | Boolean | |
| is_verified_purchase | Boolean | auto-set |
| helpful_count | PositiveInt | |
| UNIQUE | (product, user) | one review per product |

### `wishlists` table
| Column | Type | Notes |
|--------|------|-------|
| user_id | FK → users | |
| product_id | FK → products | |
| UNIQUE | (user, product) | |

### `carts` table
| Column | Type | Notes |
|--------|------|-------|
| id | BigInt PK | |
| user_id | FK → users | nullable (guest) |
| session_key | Varchar | for guest carts |
| created_at, updated_at | DateTime | |

### `cart_items` table
| Column | Type | Notes |
|--------|------|-------|
| cart_id | FK → carts | |
| product_id | FK → products | |
| quantity | PositiveInt | capped at stock |
| UNIQUE | (cart, product) | |

### `coupons` table
| Column | Type | Notes |
|--------|------|-------|
| code | Varchar UNIQUE | |
| discount_type | Varchar | percentage/fixed |
| discount_value | Decimal | |
| min_order_value | Decimal | |
| max_uses | PositiveInt | 0=unlimited |
| used_count | PositiveInt | |
| valid_from, valid_to | DateTime | |

### `orders` table
| Column | Type | Notes |
|--------|------|-------|
| id | BigInt PK | |
| order_number | Varchar UNIQUE | ORD-XXXXXXXX |
| user_id | FK → users | |
| shipping_* | Varchar | snapshot at order time |
| subtotal, discount_amount, shipping_cost, total | Decimal | |
| coupon_id | FK → coupons | nullable |
| status | Varchar | pending/confirmed/shipped/delivered/cancelled/refunded |
| payment_status | Varchar | pending/paid/failed/refunded |
| tracking_number | Varchar | |
| created_at, updated_at, delivered_at | DateTime | |

### `order_items` table
| Column | Type | Notes |
|--------|------|-------|
| order_id | FK → orders | |
| product_id | FK → products | nullable (product may be deleted) |
| product_name, product_sku | Varchar | **snapshot** |
| unit_price | Decimal | **snapshot** |
| quantity | PositiveInt | |
| line_total | Decimal | auto-calculated |

### `payments` table
| Column | Type | Notes |
|--------|------|-------|
| order_id | FK → orders | |
| payment_method | Varchar | cod/card/upi/netbanking |
| amount | Decimal | |
| status | Varchar | pending/success/failed/refunded |
| transaction_id | Varchar | from payment gateway |
| gateway_response | Text | JSON |

### `order_status_history` table
| Column | Type | Notes |
|--------|------|-------|
| order_id | FK → orders | |
| status | Varchar | |
| note | Text | |
| changed_at | DateTime | |

---

## 🚀 Quick Setup

### 1. Prerequisites
- Python 3.11+
- MySQL 8.0+
- pip

### 2. Clone & Install
```bash
pip install -r requirements.txt
```

### 3. Create MySQL Database
```sql
CREATE DATABASE ecommerce_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 4. Configure Environment
```bash
cp .env.example .env
# Edit .env with your DB credentials
```

Update `ecommerce/settings.py` DATABASES section or use `.env`:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'ecommerce_db',
        'USER': 'root',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '3306',
    }
}
```

### 5. Run Migrations
```bash
python manage.py makemigrations users store cart orders
python manage.py migrate
```

### 6. Create Admin & Seed Data
```bash
python manage.py createsuperuser
python manage.py seed_data
```

### 7. Run Server
```bash
python manage.py runserver
```

---

## 🌐 Pages

| URL | Description |
|-----|-------------|
| `/` | Home page |
| `/products/` | Product listing with filters |
| `/products/<slug>/` | Product detail + reviews |
| `/category/<slug>/` | Products by category |
| `/cart/` | Shopping cart |
| `/orders/checkout/` | Shipping address |
| `/orders/payment/` | Payment method |
| `/orders/confirmation/<id>/` | Order success |
| `/orders/` | My orders list |
| `/orders/<id>/` | Order detail + timeline |
| `/users/profile/` | User profile |
| `/users/profile/edit/` | Edit profile |
| `/users/addresses/` | Manage addresses |
| `/users/login/` | Login |
| `/users/register/` | Register |
| `/wishlist/` | Wishlist |
| `/search/?q=...` | Search |
| `/admin/` | Django admin |

---

## ✨ Features

- ✅ Custom User model (email login)
- ✅ User profiles with avatars
- ✅ Multiple shipping/billing addresses
- ✅ Product catalog with categories, brands, specs, gallery
- ✅ Product search & filtering (price, category, brand)
- ✅ Verified-purchase reviews with ratings
- ✅ Wishlist
- ✅ Cart (logged-in + guest, merges on login)
- ✅ Coupon system (% off / fixed amount)
- ✅ Multi-step checkout (address → payment → confirmation)
- ✅ Order management with status tracking
- ✅ Order cancellation (restores stock)
- ✅ Full Django Admin panel
- ✅ Stock management (auto-reduce on order)
- ✅ Responsive Bootstrap 5 UI
- ✅ Seed data command
"# ShopNow" 
