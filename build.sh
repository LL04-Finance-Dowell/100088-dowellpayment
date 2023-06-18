#!/usr/bin/env bash

set -o errexit  # exit on error

pip3 install --upgrade pip
pip3 install --upgrade setuptools

pip3 install -r requirements.txt

python manage.py collectstatic --no-input
python manage.py migrate