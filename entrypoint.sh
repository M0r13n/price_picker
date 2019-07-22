#!/bin/sh

echo "Waiting for postgres to start up..."

while ! nc -z web-db 5432; do
  sleep 0.1
done

echo "PostgreSQL started!"

# finally start the app
python manage.py run -h 0.0.0.0