#!/usr/bin/env bash
set -e

if [ -f ".env" ]; then export $(grep -v '^#' .env | xargs); else exit 1; fi

LOCAL_PYENV="$PWD/.pyenv"
PY="$LOCAL_PYENV/versions/3.12.3/bin/python"

if [ ! -d "$LOCAL_PYENV" ]; then exit 1; fi

export PYENV_ROOT="$LOCAL_PYENV"
export PATH="$PYENV_ROOT/bin:$PATH"
eval "$($PYENV_ROOT/bin/pyenv init -)"

if [ ! -f "$PY" ]; then exit 1; fi

if [ -z "$VENV_DIR" ]; then VENV_DIR=venv; fi
if [ ! -d "$VENV_DIR" ]; then $PY -m venv "$VENV_DIR"; fi

source "$VENV_DIR/bin/activate"

pip install --upgrade pip setuptools wheel
pip install -r requirements.txt --no-cache-dir
python scripts/install_argos_models.py || true

python - <<EOF
from argostranslate import package
available = package.get_available_packages()
for p in available:
    if p.from_code == "en" and p.to_code == "id":
        package.install_from_path(p.download())
        break
EOF

pkill -f "web/app.py" 2>/dev/null || true
pkill -f "celery" 2>/dev/null || true

rm -f flask.pid celery.pid

if ! pgrep -x redis-server >/dev/null; then
  redis-server --daemonize yes
fi

nohup celery -A web.worker worker --loglevel=info > celery.log 2>&1 &
echo $! > celery.pid

nohup python -m web.app > service.log 2>&1 &
echo $! > flask.pid

echo "Flask PID $(cat flask.pid)"
echo "Celery PID $(cat celery.pid)"
