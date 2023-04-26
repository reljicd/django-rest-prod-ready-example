# Django REST API + Gunicorn + Docker + SSL + Token based authentication

##  Requirements

The file *click_log.csv* contains one hour of data for the following fields: id, timestamp (unix timestamp), type, campaign, banner, content_unit, network, browser, operating_system, country, state, city

1. Set up a SQL Server (MySQL or SQLite could be a good choice) with a table that holds the data of the file *click_log.csv*

2. Write a service that accesses the data in your database and returns the following information: Given a campaign, the API returns the amount of clicks that were made on advertisements that belong to this campaign. One entry in the *click_log.csv* file represents one click. Eg.: for the campaign 4510461 the API should return 13.

3. Extend the API with a time filter, so that it only returns the number of clicks that fall between a given start date and a given end date. Both dates should be passed as a string of the format „yyyy-mm-dd hh:mm:ss“. The timezone should always be UTC.

Eg.: for the campaign 4510461, start date 2021-11-07 03:10:00 and end date 2021-11-07 03:30:00, the API should return 4.

## Solution

![Diagram.jpg](screenshots%2FDiagram.jpg)

Solution was provided using **[Python 3.11](https://docs.python.org/3/library/index.html)**, **[Django](https://www.djangoproject.com)**, **[Django REST](https://www.django-rest-framework.org)**, **[Gunicorn](https://gunicorn.org)** and database is **SQLite**.

Testing was done using Django flavor of **[untitest](https://docs.djangoproject.com/en/4.2/topics/testing/overview/)** module.

Solution comes included with **[Django Admin Site](https://docs.djangoproject.com/en/4.2/ref/contrib/admin/)**. Using admin site it is possible
to register new users and generaly to browse database and make CRUD operations on provided tables.

![Screenshot 2023-04-26 at 20.16.20.png](screenshots%2FScreenshot%202023-04-26%20at%2020.16.20.png)
![Screenshot 2023-04-26 at 20.15.51.png](screenshots%2FScreenshot%202023-04-26%20at%2020.15.51.png)
![Screenshot 2023-04-26 at 20.17.40.png](screenshots%2FScreenshot%202023-04-26%20at%2020.17.40.png)

I also provided the access to **[REST Browsable API](https://www.django-rest-framework.org/topics/browsable-api/)**. 

![Screenshot 2023-04-26 at 20.15.28.png](screenshots%2FScreenshot%202023-04-26%20at%2020.15.28.png)
![Screenshot 2023-04-26 at 20.17.29.png](screenshots%2FScreenshot%202023-04-26%20at%2020.17.29.png)

### Security

#### Authentication

API Authentication is provided using **[Django REST Knox](https://james1345.github.io/django-rest-knox/)** library. 

User of the REST API is supposed to login using his **username** and **password** in order to obtain **token**. 
Token is then used to authenticate API endpoints.

Knox provides one token per call to the login view - allowing each client to have its own token which is deleted on the server side when the client logs out. Knox also provides an optional setting to limit the amount of tokens generated per user.

Knox tokens are only stored in an encrypted form. Even if the database were somehow stolen, an attacker would not be able to log in with the stolen credentials.

#### SSL/TLS

I generated self signed certificate and key using **OpenSSL** library for Gunicorn's SSL transport.

#### Other secrets

**Superuser password** and **Django secret key** are also provided as textual files that can be modified.

All the secrets are in the [secrets](secrets) folder.

**_In real production these secrets would be used in CI/CD in encrypted form and services would 
use some secret management service. They would never be passed around in plain text like this_**

## URLs

### Development Server: http://127.0.0.1:8080
### Production Server: https://127.0.0.1:443

### Endpoints

Defined in [urls.py](src%2Fcore%2Furls.py) and [urls.py](src%2Fclicks%2Furls.py)

- **/admin/** - Django Admin Site
- **/api/clicks/campaign/:id/** - Campaign (with provided id) clicks
- **/api/browser/** - REST Browser 
- **/api/auth/login** - Login endpoint
- **/api/auth/logout** - Logout endpoint
- **/api/auth/logoutall** - Invalidate all tokens endpoint

## REST API

### Login

- **POST /api/auth/login**

Required headers
- Authorization: Basic username:password - 

Credentials should be encoded using **base64**. Example in [tests.py](src%2Fclicks%2Ftests.py): 
```python
base64.b64encode(f'{USERNAME}:{PASSWORD}'.encode()).decode()
```

### Clicks

- **GET /api/clicks/campaign/:id[int]/?after_date=:after_date[str]&before_date=:before_date[str]**

Path Parameters
- **id** - campaign ID

Query Parameters
- **after_date** - After date string in the format "YYYY-MM-DD HH:MM:SS"
- **before_date** - Before date string in the format "YYYY-MM-DD HH:MM:SS"

Required headers
- Authorization: Token token_value

Example:
```
https://127.0.0.1/api/clicks/campaign/4510461/?after_date=2021-11-07+03:10:00&before_date=2021-11-07+03:30:00
```


## Prerequisites for CLI and Make

Install virtual environment:

```bash
$ python -m virtualenv env
```

Activate virtual environment:

On macOS and Linux:
```bash
$ source env/bin/activate
```

On Windows:
```bash
$ .\env\Scripts\activate
```

Install dependencies:
```bash
$ pip install -r requirements.txt
```

## How to run

### Make

This is the easiest way to run.

For non docker commands execute [Prerequisites](#prerequisites-for-cli-and-make).

All the commands are defined in the [Makefile](Makefile).

- **bootstrap** - Bootstraps Django. Includes: clean, migrate, create_superuser, import_data, collectstatic
- **clean** - Deletes **db.sqlite3** and generated **src/static** folder.
- **migrate** - Applies migration
- **create_superuser** - Creates Django super user (admin)
- **import_data** - Imports **data/click_log.csv** into **SQLite**
- **collectstatic** - Generates static files to serve with Gunicorn and built in dev server
- **run_tests** - Runs tests
- **run_dev_server** - Runs development server on **http://127.0.0.1:8080**
- **run_prod_server** - Runs Gunicorn server on **https://127.0.0.1:443**


- **docker_build** - Builds **Docker** image
- **docker_run_tests** - Runs tests using generated **Docker** image
- **docker_run_dev_server** - Runs development server on **http://127.0.0.1:8080** inside **Docker** container
- **docker_run_prod_server** - Runs Gunicorn server on **https://127.0.0.1:443** inside **Docker** container

All the commands are run from the root of the project in the form:
```bash
$ make command
```

Examples:
```bash
$ make bootstrap
$ make run_tests
```
```bash
$ make docker_run_prod_server
```

### CLI

You can run the application from the command line with **manage.py**.

Before running any command first execute [Prerequisites](#prerequisites-for-cli-and-make).

From the root of the project:

Run migrations:
```bash
$ python src/manage.py migrate
```

Import **data/click_log.csv** into **SQLite**:
```bash
$ python src/manage.py import_clicks_from_csv --path data/click_log.csv
```

Create Django super user (admin):
```bash
$ python src/manage.py createsuperuser --email admin@example.com --username admin
```

Generate static files to serve with Gunicorn and built in dev server:
```bash
$ python src/manage.py collectstatic
```

Run development server on port **8000**:
```bash
$ python src/manage.py runserver
```

Run **Gunicorn** server on port **443**, using SSL:
```bash
$ export DEBUG=False; export SECRET_KEY="${cat secrets/secret.key}"; cd src; \
	python -m gunicorn core.wsgi \
	-b :443 --keyfile ../secrets/key.pem --certfile ../secrets/cert.pem
```

### Docker

It is also possible to run servers and tests using Docker.

Build the Docker image:
```bash
$ docker build -t reljicd/clicks_api --build-arg DJANGO_SUPERUSER_PASSWORD=very_secret_password -f docker/Dockerfile .
```

Run development server on **http://127.0.0.1:8080** inside **Docker** container:
```bash
$ docker run -p 8000:8000 --rm reljicd/clicks_api manage.py runserver 0.0.0.0:8000
```

Run Gunicorn server on **https://127.0.0.1:443** inside **Docker** container:
```bash
$ docker run -p 443:443 -e SECRET_KEY="${cat secrets/secret.key}" -e DEBUG=False --rm reljicd/clicks_api
```

## Driving REST API using Postman

![Screenshot 2023-04-26 at 18.21.00.png](screenshots%2FScreenshot%202023-04-26%20at%2018.21.00.png)
![Screenshot 2023-04-26 at 18.21.26.png](screenshots%2FScreenshot%202023-04-26%20at%2018.21.26.png)
![Screenshot 2023-04-26 at 22.04.03.png](screenshots%2FScreenshot%202023-04-26%20at%2022.04.03.png)

## Helper Tools

### Django Admin

It is possible to add additional admin user who can login to the admin site. Run the following command:
```bash
$ python src/manage.py createsuperuser
```
Enter your desired username and press enter.
```bash
Username: admin_username
```
You will then be prompted for your desired email address:
```bash
Email address: admin@example.com
```
The final step is to enter your password. You will be asked to enter your password twice, the second time as a confirmation of the first.
```bash
Password: **********
Password (again): *********
Superuser created successfully.
```

Go to the web browser and visit `http://127.0.0.1:8000/admin` (dev) 
or `https://127.0.0.1/admin` (prod)

### REST Browsable API

Go to the web browser and visit `http://127.0.0.1:8000/api/browser/` (dev)
or `https://127.0.0.1/api/browser/` (prod)

### Tests

Tests can be found in [tests.py](src%2Fclicks%2Ftests.py).

Before running tests using CLI or Make first execute [Prerequisites](#prerequisites-for-cli-and-make).

Using manage.py:
```bash
$ python src/manage.py test clicks
```

Using make:
```bash
$ make run_tests
```

#### Docker

It is also possible to run tests using Docker.
First build the image following instructions in [Make](#make) or [Docker](#docker)

Using docker CLI:
```bash
$ docker run --rm reljicd/clicks_api manage.py test clicks
```

Using make:
```bash
$ make docker_run_tests
```