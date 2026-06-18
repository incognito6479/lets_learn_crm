# Learning Center Management System

A management application for learning centers built with Django, DRF, Vue.js, and PostgreSQL.

## Prerequisites
- Docker
- Docker Compose

## Getting Started

1. **Clone the repository (if applicable)**
2. **Build and start the containers:**
   ```bash
   docker-compose up --build
   ```
3. **Run migrations:**
   ```bash
   docker-compose exec backend python manage.py migrate
   ```
4. **Create a superuser:**
   ```bash
   docker-compose exec backend python manage.py createsuperuser
   ```

## Services
- **Backend (Django):** http://localhost:8000
- **Frontend (Vue.js):** http://localhost:3000
- **Admin Interface:** http://localhost:8000/admin
- **API Documentation:** http://localhost:8000/api/

## Features
- Student management
- Payment recording
- Course and Group management
- Branch and Room management
- User roles (Admin, Cashier, CEO, Teacher)
