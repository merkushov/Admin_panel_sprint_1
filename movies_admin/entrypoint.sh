#!/bin/bash

python manage.py flush --noinput

echo "Migrate data schema..."
python manage.py migrate --noinput

echo "Creating super user..."
python manage.py createsuperuser --noinput

# Нужно, для того чтобы стартанул Django
exec "$@"