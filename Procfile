web: python wsgi.py
postdeploy: python manage.py create-db; python manage.py create-data;
worker: celery worker -A price_picker.celery_app:app