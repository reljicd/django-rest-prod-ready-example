PYTHON = python
MANAGE_PY = src/manage.py
MANAGE = ${PYTHON} ${MANAGE_PY}

DOCKER_TAG = reljicd/clicks_api
DOCKER_FOLDER = ./docker
DOCKERFILE = ${DOCKER_FOLDER}/Dockerfile

SECRET_KEY = ${shell cat secrets/secret.key}
DJANGO_SUPERUSER_PASSWORD = ${shell cat secrets/superuser.password}

run_dev_server:
	${MANAGE} runserver

run_prod_server:
	export DEBUG=False; export SECRET_KEY="${SECRET_KEY}"; cd src; \
	${PYTHON} -m gunicorn core.wsgi \
	-b :443 --keyfile ../secrets/key.pem --certfile ../secrets/cert.pem

bootstrap: clean migrate create_superuser import_data collectstatic

clean:
	rm -rf src/static || true; rm db.sqlite3 || true

migrate:
	${MANAGE} migrate

collectstatic:
	${MANAGE} collectstatic

make_migrations:
	${MANAGE} makemigrations clicks

create_superuser:
	${MANAGE} createsuperuser --email admin@example.com --username admin

import_data:
	${MANAGE} import_clicks_from_csv --path data/click_log.csv

run_tests:
	${MANAGE} test clicks

docker_build:
	docker build -t ${DOCKER_TAG} --build-arg DJANGO_SUPERUSER_PASSWORD=${DJANGO_SUPERUSER_PASSWORD} -f ${DOCKERFILE} .

docker_run_tests: docker_build
	docker run --rm ${DOCKER_TAG} manage.py test clicks

docker_run_dev_server: docker_build
	docker run -p 8000:8000 --rm ${DOCKER_TAG} manage.py runserver 0.0.0.0:8000

docker_run_prod_server: docker_build
	docker run -p 443:443 -e SECRET_KEY="${SECRET_KEY}" -e DEBUG=False --rm ${DOCKER_TAG}