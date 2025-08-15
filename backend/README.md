# Rental Management Backend

Setup
- Create venv: `python3 -m virtualenv .venv && source .venv/bin/activate`
- Install: `pip install -r requirements.txt`
- Migrate: `python manage.py migrate`
- Run: `python manage.py runserver 0.0.0.0:8000`

Docs
- Open `http://localhost:8000/api/docs/`

Key endpoints
- Products: `GET /api/catalog/products/`
- Availability check: `POST /api/rentals/orders/availability/check`
- Pricelists: `GET /api/pricing/pricelists/`
- Orders: `GET /api/rentals/orders/`