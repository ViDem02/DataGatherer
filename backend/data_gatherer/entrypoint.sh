#!/bin/sh

if [ "$DATABASE" = "postgres" ]
then
    echo "Waiting for postgres..."

    while ! nc -z $SQL_HOST $SQL_PORT; do
      sleep 0.5
    done

    echo "PostgreSQL started"
fi

# Uncomment below to flush db e.g. after running tests
# Just make sure you really mean it
# python manage.py flush --no-input


python manage.py migrate || exit
python manage.py test --noinput || exit
python manage.py collectstatic --noinput
python manage.py createsuperuser --noinput

exec "$@"