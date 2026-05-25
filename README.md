# StayLink Backend

Production-level accommodation booking platform backend.

## Tech Stack

- Django + Django REST Framework
- PostgreSQL
- Redis (Docker)
- Celery + Celery Beat
- JWT Authentication
- Google OAuth

## Project Structure

staylinkproject/
├── staylinkproject/    # Project config, celery.py
├── accounts/           # Auth, profiles, email tasks
└── manage.py

## Setup Instructions

### 1. Clone the repository
```bash
git clone https://github.com/YOURUSERNAME/staylink-backend.git
cd staylink-backend
```

### 2. Create virtual environment
```bash
python -m venv staylinkenv
staylinkenv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 3. Create .env file
Copy `.env.example` to `.env` and fill in your values.

### 4. Start Redis
```bash
docker run -d --name staylink-redis -p 6379:6379 redis
```

### 5. Run migrations
```bash
python manage.py migrate
```

### 6. Start Django server
```bash
python manage.py runserver
```

### 7. Start Celery worker
```bash
celery -A staylinkproject worker --pool=solo --loglevel=info -Q email_queue
```

## Implemented Features

- JWT Authentication
- Google Authentication  
- Email Verification (OTP)
- Role-based system (Traveler, Owner, Broker, Admin)
- Owner onboarding
- Broker onboarding
- Async email system via Celery
- Background OTP cleanup via Celery Beat