#!/usr/bin/env bash
set -o errexit

cd /opt/render/project/src
export PYTHONPATH=/opt/render/project/src:$PYTHONPATH

echo "Working directory: $(pwd)"
echo "Python path: $PYTHONPATH"
echo "Files here: $(ls)"

exec gunicorn wanderly.wsgi:application --bind 0.0.0.0:$PORT