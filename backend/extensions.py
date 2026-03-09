from flask_mail import Mail
from flask_caching import Cache
from celery import Celery

mail = Mail()
cache = Cache()
celery = Celery()
