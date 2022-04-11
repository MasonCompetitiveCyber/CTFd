#!/bin/bash
set -euo pipefail

WORKERS=${WORKERS:-1}
WORKER_CLASS=${WORKER_CLASS:-gevent}
ACCESS_LOG=${ACCESS_LOG:--}
ERROR_LOG=${ERROR_LOG:--}
WORKER_TEMP_DIR=${WORKER_TEMP_DIR:-/dev/shm}
SECRET_KEY=${SECRET_KEY:-}

# Check that a .ctfd_secret_key file or SECRET_KEY envvar is set
if [ ! -f .ctfd_secret_key ] && [ -z "$SECRET_KEY" ]; then
    if [ $WORKERS -gt 1 ]; then
        echo "[ ERROR ] You are configured to use more than 1 worker."
        echo "[ ERROR ] To do this, you must define the SECRET_KEY environment variable or create a .ctfd_secret_key file."
        echo "[ ERROR ] Exiting..."
        exit 1
    fi
fi

# Copy SSH key to container if it exists
SSH_KEY_RSA=id_rsa
if [ -f "$SSH_KEY_RSA" ]; then
        mkdir -p /root/.ssh/
        chmod 700 /root/.ssh/
        cp $SSH_KEY_RSA /root/.ssh/$SSH_KEY_RSA
        chmod 600 /root/.ssh/$SSH_KEY_RSA
fi

SSH_KEY_ED=id_ed25519
if [ -f "$SSH_KEY_ED" ]; then
        mkdir -p /root/.ssh/
        chmod 700 /root/.ssh/
        cp $SSH_KEY_ED /root/.ssh/$SSH_KEY_ED
        chmod 600 /root/.ssh/$SSH_KEY_ED
fi

# Ensures that the database is available
python ping.py

# Initialize database
python manage.py db upgrade

# Start CTFd
echo "Starting CTFd"
exec gunicorn 'CTFd:create_app()' \
    --bind '0.0.0.0:8000' \
    --workers $WORKERS \
    --worker-tmp-dir "$WORKER_TEMP_DIR" \
    --worker-class "$WORKER_CLASS" \
    --access-logfile "$ACCESS_LOG" \
    --error-logfile "$ERROR_LOG"
