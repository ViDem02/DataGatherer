#!/bin/sh

if [ "$DATABASE" = "postgres" ]
then
    echo "Waiting for postgres..."

    while ! nc -z $SQL_HOST $SQL_PORT; do
      sleep 0.5
    done

    echo "PostgreSQL started"
fi

# Tests are not run here: a failing test must not stop the application.
# Run them with: docker compose --env-file .env.docker run --rm django python manage.py test

python manage.py migrate || exit
python manage.py collectstatic --noinput

# Creates the administrator from DJANGO_SUPERUSER_* on the first start only
python manage.py shell -c "
import sys
from django.contrib.auth import get_user_model
sys.exit(0 if get_user_model().objects.filter(is_superuser=True).exists() else 1)
" || python manage.py createsuperuser --noinput

exec "$@"
