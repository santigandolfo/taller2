#!/bin/bash
set -e

if [ "$ENV" = 'DEV' ]; then
  echo "Running Dev Server"
  cd /app
  exec gunicorn --bind 0.0.0.0:$PORT wsgi --log-level info --log-file -
else
  echo "Running Production Server"
  cd /app
  exec gunicorn --bind 0.0.0.0:$PORT wsgi  --log-level info --log-file -
fi
