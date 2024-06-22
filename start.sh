#!/bin/bash

if [ ! -d ".env" ]; then
    echo "Creating virtual env"
    python3 -m venv .env
    source .env/bin/activate
    pip install -r requirements.txt
fi

source .env/bin/activate

export FLASK_APP=main.py

flask run 

# celery -A main.celery worker -l info 

# wait