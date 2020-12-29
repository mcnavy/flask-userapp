#!/usr/bin/env bash
export PYTHONUNBUFFERED=1

flask db init
flask db migrate
flask db upgrade
gunicorn -b 0.0.0.0:5000 -w 1 app:app

