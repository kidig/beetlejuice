# Beetlejuice

Django Project Template


## requirements
- Python 3.5+
- PostgreSQL 9.5+

## development
- install python dependencies `pip-compile requirements.in && pip-sync`
- install MJML for _django-happymailer_ `npm install mjml`
- create postgres user and database
- create `.local-env` and fill with the settings (see `.env`)
- run database migrations: `./manage.py migrate`
- start server with './dev.sh'


## tests
- run tests with `./venv/bin/py.test --reuse-db`
