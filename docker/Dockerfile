FROM python:3.11-alpine

EXPOSE 443
EXPOSE 8000

ARG DJANGO_SUPERUSER_PASSWORD
ARG DJANGO_SUPERUSER_USERNAME=admin
ARG DJANGO_SUPERUSER_EMAIL=example@mail.com

ENV WORKING_DIR /app

# Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

WORKDIR $WORKING_DIR

# Project files
COPY src/manage.py $WORKING_DIR/manage.py
COPY src/core $WORKING_DIR/core
COPY src/users $WORKING_DIR/users
COPY src/clicks $WORKING_DIR/clicks

# Secrets
COPY secrets/cert.pem /secrets/cert.pem
COPY secrets/key.pem /secrets/key.pem

# Data
COPY data $WORKING_DIR/data

# Run migrations, and load the database
RUN python manage.py migrate
RUN python manage.py import_clicks_from_csv --path data/click_log.csv

# Create super user
RUN python manage.py createsuperuser --noinput

# Generate static files
RUN python manage.py collectstatic

ENTRYPOINT ["python"]
CMD ["-m", "gunicorn", "core.wsgi", "-b", ":443", "--keyfile", "/secrets/key.pem", "--certfile", "/secrets/cert.pem"]