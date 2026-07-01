FROM python:3.13-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements-django.txt .
RUN pip install --no-cache-dir -r requirements-django.txt

COPY . .

EXPOSE 8000

# collectstatic runs at container start via docker-compose command
# not at build time — because env vars aren't available at build time

CMD ["daphne", "-b", "0.0.0.0", "-p", "8000", "staylinkproject.asgi:application"]