# BoardBuy UAE — OOH Marketplace

Production starter codebase for a three-sided billboard marketplace
(advertisers · billboard owners · admin).

## Stack

| Layer | Choice |
|---|---|
| Frontend | Next.js 14 (App Router) + Tailwind CSS |
| Backend | Django 5 + Django REST Framework |
| Database | PostgreSQL 16 + PostGIS (GeoDjango) |
| Maps | Mapbox GL JS (Google Maps swappable) |
| Payments | Stripe (Telr / PayTabs / Network International adapters stubbed) |
| Storage | S3 or Cloudflare R2 (django-storages) |
| Notifications | SendGrid email + WhatsApp Business API stubs |
| Dev infra | Docker Compose |

## Quick start

```bash
cp .env.example .env          # fill in keys (works with defaults for local dev)
docker compose up --build
```

- API: http://localhost:8000/api/  (browsable DRF)
- Admin: http://localhost:8000/admin/
- Frontend: http://localhost:3000

First run:

```bash
docker compose exec backend python manage.py migrate
docker compose exec backend python manage.py createsuperuser
docker compose exec backend python manage.py seed_demo   # loads sample UAE billboards
```

## Repo layout

```
backend/
  config/            Django settings, urls
  api/               single app: models, serializers, views, permissions
    models.py        MediaCompany, Advertiser, Unit(PointField), AvailabilitySlot,
                     Campaign, Booking, Creative, PlayProof, Invoice, Dispute
    payments.py      Stripe integration + UAE gateway adapter interface
    notifications.py SendGrid / WhatsApp stubs
frontend/
  src/app/           home, marketplace (map + filters), unit detail, checkout
  src/lib/api.ts     typed fetch client
```

## Key API endpoints

| Method | Path | Purpose |
|---|---|---|
| GET | /api/units/?emirate=Dubai&format=digital | search inventory (geo filters) |
| GET | /api/units/{id}/ | unit detail + availability |
| POST | /api/campaigns/ | create campaign draft |
| POST | /api/bookings/ | request booking (per unit + date range) |
| POST | /api/bookings/{id}/decide/ | owner accept / reject |
| POST | /api/payments/checkout/ | create Stripe PaymentIntent (deposit or full) |
| POST | /api/creatives/ | artwork upload |
| POST | /api/bookings/{id}/proof/ | installation / proof-of-display photos |
| GET | /api/reports/sales/ | admin sales report |

## Where to plug in UAE payment gateways

`backend/api/payments.py` defines `PaymentGateway` with a `StripeGateway`
implementation. Add `TelrGateway`, `PayTabsGateway`, or `NetworkIntlGateway`
by implementing `create_checkout()` and `verify_webhook()` — the booking flow
is gateway-agnostic.

## Production notes

- Set `DJANGO_DEBUG=0`, real `SECRET_KEY`, `ALLOWED_HOSTS`
- Use managed Postgres with PostGIS (AWS RDS, DigitalOcean, or a UAE-based cloud)
- Media to S3/R2: set `USE_S3=1` + credentials in `.env`
- Run backend under gunicorn behind nginx; frontend on Vercel or Node
