#!/usr/bin/env bash
set -o errexit

pip install -r requirements.txt

python manage.py collectstatic --noinput
python manage.py migrate

python manage.py shell << PYCODE
from django.contrib.auth import get_user_model
User = get_user_model()

username = "admin"
email = "admin@example.com"
password = "admin123"

if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username=username, email=email, password=password)
    print("Superuser created: admin / admin123")
else:
    print("Superuser already exists")
PYCODE

