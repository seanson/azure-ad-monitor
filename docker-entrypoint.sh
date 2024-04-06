#!/bin/sh

set -e

. /venv/bin/activate

exec uwsgi --ini uwsgi.ini
