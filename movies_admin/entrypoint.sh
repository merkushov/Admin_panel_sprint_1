#!/bin/bash

python manage.py flush --noinput

echo "Migrate data schema..."
python manage.py migrate --noinput

echo "Creating super user..."
python manage.py createsuperuser --noinput

echo "Compiling localization files..."
python manage.py compilemessages

echo "Gathering static files in a single directory..."
python manage.py collectstatic --noinput

# Нужно, для того чтобы стартанул Django
exec "$@"