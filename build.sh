#!/usr/bin/env bash

set -o errexit  # exit on error

pip3 install --upgrade pip
pip3 install --upgrade setuptools

/usr/bin/python3 -m pip install -r requirements.txt


python manage.py collectstatic --no-input
python manage.py migrate