#!/bin/bash
# ShopNow Setup Script

echo "=============================="
echo "  ShopNow E-Commerce Setup"
echo "=============================="

# Create virtual environment
echo "[1/6] Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install dependencies
echo "[2/6] Installing dependencies..."
pip install -r requirements.txt

# Create MySQL database
echo "[3/6] Setting up MySQL database..."
echo "Please ensure MySQL is running and update .env with your credentials"
cp .env.example .env
echo "→ Edit .env with your MySQL credentials before continuing"

# Apply migrations
echo "[4/6] Running migrations..."
python manage.py makemigrations
python manage.py migrate

# Create superuser
echo "[5/6] Creating admin superuser..."
python manage.py createsuperuser

# Collect static files
echo "[6/6] Collecting static files..."
python manage.py collectstatic --noinput

echo ""
echo "✅ Setup complete!"
echo "   Run: python manage.py runserver"
echo "   Admin: http://localhost:8000/admin/"
echo "   Site:  http://localhost:8000/"
