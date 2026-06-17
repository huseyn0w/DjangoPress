#!/usr/bin/env bash
set -euo pipefail

# Wait for Postgres to accept connections before touching the ORM.
if [ -n "${POSTGRES_HOST:-}" ]; then
  echo "Waiting for database at ${POSTGRES_HOST}:${POSTGRES_PORT:-5432}..."
  until python -c "
import os, socket, sys
s = socket.socket()
s.settimeout(1)
try:
    s.connect((os.environ['POSTGRES_HOST'], int(os.environ.get('POSTGRES_PORT', '5432'))))
except OSError:
    sys.exit(1)
" 2>/dev/null; do
    sleep 1
  done
  echo "Database is up."
fi

echo "Applying migrations..."
python manage.py migrate --noinput

exec "$@"
