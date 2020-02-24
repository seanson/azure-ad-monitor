#!/usr/bin/env python3
import creds

from flask import Flask
from flask_apscheduler import APScheduler
from werkzeug.middleware.dispatcher import DispatcherMiddleware
from prometheus_client import make_wsgi_app
from prometheus_client.core import REGISTRY


class Config(object):
    SCHEDULER_API_ENABLED = True


# Set up our credential collection
cred_collector = creds.CredentialCollector()
REGISTRY.register(cred_collector)

# Configure a basic flask app
app = Flask(__name__)
app.config.from_object(Config())

# Set up our sheduler for querying credentials in the background
scheduler = APScheduler()
scheduler.init_app(app)
scheduler.start()

# Configure a dispatch middleware for Prometheus metrics
app_dispatch = DispatcherMiddleware(app, {"/metrics": make_wsgi_app()})


@scheduler.task("interval", id="sync_stats_1", seconds=600, misfire_grace_time=900)
def sync_stats():
    cred_collector.cred_update()
