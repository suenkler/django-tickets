A simple ticketing application
==============================

`django-tickets` is a simple MIT-licensed ticketing application written in Python/Django. Some of the features are:

- creation of new tickets via web interface or via email
- followups on tickets
- file attachments for tickets
- assign tickets to users
- email notifications for new assignments, followups and closed tickets

The application was written to serve my special needs.  It is not intended to grow up to a kitchen sink.  But I will add some features in the future.  Feel free to use and modify it, if it is interesting for you.

What does it look like?
=======================

`django-tickets` uses a simple Bootstrap template. Nothing fancy.

![Landing Page](screenshots/screenshot_landing_page.png?raw=true "Landing Page")
![My tickets](screenshots/screenshot_my_tickets.png?raw=true "My tickets")

Installation
============

Sensitive and installation dependent information is expected in environment variables. You can use a bash script like this one:

```
#!/usr/bin/env bash

export DJANGO_SECRET_KEY="xxx"
export DJANGO_PRODUCTION_DOMAIN="xxx"

# log file
export DJANGO_LOG_FILE="xxx"

# static and media files dir in production
export DJANGO_STATIC_ROOT="static_root/"
export DJANGO_MEDIA_ROOT="xxx"

# User who gets django's email notifications (ADMINS/MANAGERS), see settings.py
export DJANGO_ADMIN_NAME="xxx"
export DJANGO_ADMIN_EMAIL="xxx"

# Django email configuration
export DJANGO_EMAIL_HOST="xxx"
export DJANGO_EMAIL_HOST_USER="xxx"
export DJANGO_EMAIL_HOST_PASSWORD="xxx"

# ticket email inbox, see 'main/management/commands/get_email.py'
export DJANGO_TICKET_INBOX_SERVER="xxx"
export DJANGO_TICKET_INBOX_USER="xxx"
export DJANGO_TICKET_INBOX_PASSWORD="xxx"

# email notifications to admin, see 'main/management/commands/get_email.py'
export DJANGO_TICKET_EMAIL_NOTIFICATIONS_FROM="xxx"
export DJANGO_TICKET_EMAIL_NOTIFICATIONS_TO="xxx"
```

Please note that `django-tickets` is **not** packaged as a reusable django app; it's a **complete django project**. So just clone the repository and install the dependencies via pip and the application including user authentication is ready to go.

```
$ git clone https://github.com/suenkler/django-tickets.git
$ cd django-tickets
$ pip install -r requirements.txt
$ source env.sh
$ ./manage.py migrate
$ ./manage.py collectstatic
$ ./manage.py createsuperuser
$ ./manage.py runserver
```

To check the IMAP account for new messages and create tickets out of these messages, use the management command `get_email`:

```
$ ./manage.py get_email
```
