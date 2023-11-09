#!/bin/bash
echo "Начинаю удаление хлама"
rm recipes/migrations/00*
rm users/migrations/00*
rm db.sqlite3
echo "удалено"
echo "начинаю установку нового хлама"
python3 manage.py makemigrations
python3 manage.py migrate

python3 manage.py createsuperuser


