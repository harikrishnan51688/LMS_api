from flask import Flask
from flask_cors import CORS
from flask_wtf import CSRFProtect
from config import config
from urls import api
from worker import celery_init_app
from models import db
from api import cache
from flask_migrate import Migrate
from roles import setup_db

app = Flask(__name__)
CORS(app)


app.config.from_object(config['default'])

# csrf = CSRFProtect(app)
api.init_app(app)
celery = celery_init_app(app)

db.init_app(app)
cache.init_app(app)
migrate = Migrate(app, db)


with app.app_context():
    # db.drop_all()
    db.create_all()
    setup_db()

if __name__ == "__main__":
    app.run()