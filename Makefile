runserver:
	python src/manage.py runserver

migrate:
	python src/manage.py migrate

createsuperuser:
	python src/manage.py createsuperuser --email admin@example.com --username admin

import_data:
	python src/manage.py import_clicks_from_csv --path ../data/click_log.csv

run_tests:
	python src/manage.py test clicks
