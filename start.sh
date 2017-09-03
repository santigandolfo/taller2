#!/bin/bash
set -e

if [ "$ENV" = 'DEV' ]; then
  echo "Running Dev Server"
  cd /app
  exec gunicorn --bind 0.0.0.0:$PORT wsgi
else
  echo "Running Production Server"
  cd /app
  exec gunicorn --bind 0.0.0.0:$PORT wsgi  
fi
