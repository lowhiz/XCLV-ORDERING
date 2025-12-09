# XCLV Davao Ordering System

This repository contains all source code and related resources for the **XCLV Davao Ordering System** project.

To better understand our **branching strategies**, **development workflow**, and overall **project context**, please visit the following links:

[Git and GitHub Documentation (by lowhiz)](https://docs.google.com/document/d/1l1XPDwYQddUXh0kjVJZButdPzNLvGjmAEwV0ho1QTAg/edit?usp=sharing)

[Project Document (in school domain)](https://docs.google.com/document/d/1AZlIi8WTghCwsrWWpuuY7iQlhgN1QCuq35Yy6cs11W0/edit?usp=sharing)

---

## 📘 Overview
The **XCLV Davao Ordering System** is being developed to streamline and simplify the ordering process for XCLV Davao.
It serves as a centralized platform for managing orders efficiently and securely.

---

## 🛠️ Tech Stack
* **Frontend:** HTML, CSS, JavaScript, Bootstrap
* **Backend:** Django (Python)
* **Database:** PostgreSQL
* **Version Control:** Git & GitHub

---

## 👥 Contributors
* [lowhiz](#)
* [luigi-ichi](#)
* [jcell](#)
* [jd](#)

## Development Onboarding
### Dependencies
* `pipenv` for managing Python virtual environments (installable via `pip install pipenv`)

### Onboarding Proper
* When working on the project, always run under the pipenv subshell. You can enter it by running `pipenv shell` in the project root directory.
  * The pipenv is a virtual environment containing all necessary dependencies for the project. This is to maintain consistency across different development environments The `Pipfile` lists all dependencies for the project in the event in the event that you prefer your local environment over pipenv.

### Testing
#### Prior to Running The Server
* In Postgres, make sure to create a database named `xclv_ordering`
* Create a superuser account (if not already created) by running `python manage.py createsuperuser`.
* Ensure all migrations are applied by running `python manage.py migrate` within the pipenv shell. This will populate the database with the necessary tables and initial data like QR codes and their batches as well as menu items.

#### Running The Server
* Make sure your Postgres server is running.
* To run tests, use the command `python manage.py runserver` within the pipenv shell.
* To access the ordering form, you can generate test QR URLs. Simply execute `pipenv run python debug_qr_codes.py` and open a valid QR URL from the output to your web browser.

---

## 📄 License
This project is for educational purposes only and is maintained by the XCLV Davao development team.
