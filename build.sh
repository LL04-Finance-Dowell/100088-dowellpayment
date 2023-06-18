#!/usr/bin/env bash

set -o errexit  # exit on error

python -m pip3 install --upgrade pip3
pip3 install -r requirements.txt

python manage.py collectstatic --no-input
python manage.py migrate