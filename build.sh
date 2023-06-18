#!/usr/bin/env bash

set -o errexit  # exit on error

python -m pip install --upgrade pip
python -m pip install --upgrade setuptools
python -m pip install -r requirements.txt

python manage.py collectstatic --no-input
python manage.py migrate
