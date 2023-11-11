#!/bin/sh
python3 manage.py makemigrations
python3 manage.py migrate
gunicorn --bind 0:8000 backend.wsgi