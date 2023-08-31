#!/bin/sh

if [ "$DATABASE" = "postgres" ]
then
    echo "Waiting for postgres..."

    while ! nc -z $SQL_HOST $SQL_PORT; do
      sleep 1
    done
    sleep 3
    echo "PostgreSQL started"
fi

# python manage.py dumpdata > fixtures.json # сохранение фикстур
#python manage.py flush --no-input
python ./manage.py migrate


#gunicorn stones.asgi:application \
#  -k uvicorn.workers.UvicornWorker \
#  --bind 0.0.0.0:8000 \
#  --timeout 100 \
#  --workers "1" \
#  --threads "1"


#python ./manage.py runserver 0.0.0.0:8000
exec "$@"