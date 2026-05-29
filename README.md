# XCLV Davao Ordering System

This repository contains the source code and assets for the XCLV Davao Ordering System — a Django-based web app used to manage menus, orders and QR-based ordering flows.

---

## Overview
A small Django application that provides an admin dashboard for managing menu items, tables, QR codes, and order workflows.

## Tech stack
- Frontend: HTML, CSS, JavaScript, Bootstrap 5
- Backend: Django (Python)
- Database: PostgreSQL
- Dev tooling: `pipenv` for virtualenv / dependency management

## Requirements
- Python 3.10+ (3.13-3.14 recommended)
- PostgreSQL (12+)
- `pipenv` (install via `pip install pipenv`)

## Quick install (development)
1. Clone the repo and cd into the project root:

```bash
git clone <repo-url>
cd XCLV-ORDERING
```

2. Install dependencies and enter the virtual environment:

```bash
pip install pipenv
pipenv install
pipenv shell
```

If the virtual environment fails when trying to install dependencies and/or start the Django web server, specify the Python version when re-initializing the Pipenv virtual environment
```bash
pipenv uninstall
# Initialize a virtual environment specifying a Python version
pipenv --python 3.14
pipenv shell
pipenv install
```

3. Create a PostgreSQL database and user (example):

```bash
# create a DB named xclv_ordering
createdb xclv-ordering
# or via psql:
# psql -c "CREATE DATABASE xclv-ordering;"
```

4. Configure environment variables (recommended):

- Create a `.env` file in the project root with at least:

```
SECRET_KEY=your-secret-key
DEBUG=True
DATABASE_NAME=xclv_ordering
DATABASE_USER=<db_user>
DATABASE_PASSWORD=<db_password>
DATABASE_HOST=localhost
DATABASE_PORT=5432
```

5. **Configure `/admin_auth/pipeline.py` to whitelist the Google account emails of your choice by appending to the `ALLOWED_ADMIN_EMAILS` list enclosed in single-quotes (`'`) and separated by commas for multiple entries, such as this example below:**

```python
# List of Google emails allowed to log in as admin.
# Replace these with your actual team's Google emails.
ALLOWED_ADMIN_EMAILS = [
    'johndoe123@gmail.com',
    'juandelacruz@gmail.com',
]
```

> [!IMPORTANT]
> The Google (Gmail) account that you're going to use to log in to the admin dashboard must be included in the `ALLOWED_ADMIN_EMAILS` above. Otherwise, you won't be able to log in even if you have a valid Google account as part of the authentication pipeline.


6. Apply migrations and create a superuser:

```bash
python manage.py migrate
python manage.py createsuperuser
```

> [!NOTE]
> When running the migration command, this will take some time as it populates the /media/qrcodes directory with QR code images for all tables in the database. Do not interrupt the migration process until it completes successfully.

7. Run the development server:

```bash
python manage.py runserver
```

Visit `http://127.0.0.1:8000/` and log in to the admin dashboard to manage menu items.


8. To obtain a URL for a valid QR code to enter the customer side (ordering form), run this command and use any of the three valid QR code URLs

```bash
# generate debug QR codes for testing
pipenv run python debug_qr_codes.py
```


## Production notes
- Set `DEBUG=False` and configure `ALLOWED_HOSTS`.
- Use `collectstatic` and serve static files via a web server or CDN:

```bash
python manage.py collectstatic --noinput
```

- Use a WSGI server (gunicorn/uvicorn) behind a reverse proxy, and configure environment variables for DB and secret key.

## Contributors
- lowhiz (Karlo Louis C. Dongon)
- luigi-ichi (Luigi Antonio G. Guillen)
- jcell (Jeycel Ann M. Tabon)
- jd (Jann Dave R. Casquejo)
