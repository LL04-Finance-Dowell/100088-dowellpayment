#!/usr/bin/env bash

set -o errexit  # exit on error

python get-pip.py
pip install -r requirements.txt

python manage.py collectstatic --no-input
python manage.py migrate