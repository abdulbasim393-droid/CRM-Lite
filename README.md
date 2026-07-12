# CRM Tracker

A full-featured CRM (Customer Relationship Management) application built with Django REST Framework and React.

## Tech Stack

- **Backend:** Django 6, Django REST Framework, SimpleJWT, PostgreSQL
- **Frontend:** React 18, TypeScript, Tailwind CSS, Vite, Recharts
- **Tooling:** uv (Python package manager), pnpm/npm

## Features

- Lead management with status tracking (New, Contacted, Demo, Negotiation, Won, Lost)
- Customer conversion pipeline
- Follow-up scheduling and tracking
- Activity logging across all entities
- Role-based access control (Admin, Sales Manager, Sales Executive)
- Interactive dashboard with KPIs and charts
- DRF-Spectacular API documentation (Swagger UI)

## Getting Started

### Backend

```bash
# Install dependencies
uv sync

# Apply migrations
uv run backend/manage.py migrate

# Create a superuser
uv run backend/manage.py createsuperuser

# Run the development server
uv run backend/manage.py runserver
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

The frontend dev server proxies `/api` requests to `localhost:8000`.

### API Documentation

Once the backend is running, visit `/api/docs/` for the Swagger UI.
