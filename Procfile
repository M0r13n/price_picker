web: python wsgi.py
worker: celery worker -A price_picker.celery_app:app
postdeploy: python manage.py db upgrade