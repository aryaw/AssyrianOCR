#!/usr/bin/env bash
set +e
echo "Stopping Flask, Celery, Redis"
pkill -f "web/app.py" 2>/dev/null || true
pkill -f "celery" 2>/dev/null || true
pkill -x redis-server 2>/dev/null || true
rm -f flask.pid celery.pid service.log celery.log
echo "Stopped."
