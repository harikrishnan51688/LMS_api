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

# celery -A tasks.celery worker -l info 
# celery -A tasks.celery flower 

# wait