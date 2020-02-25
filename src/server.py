#!/usr/bin/env python3
import logging
import os

from flask import Flask
from flask_apscheduler import APScheduler
from prometheus_client import make_wsgi_app
from prometheus_client.core import REGISTRY
from werkzeug.middleware.dispatcher import DispatcherMiddleware

import creds

logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"))


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


@app.route("/reload")
def reload_stats():
    # An endpoint for manually triggering an update
    cred_collector.cred_update()
    return "OK"
