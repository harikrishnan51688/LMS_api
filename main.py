from flask import Flask
from flask_cors import CORS
from flask_wtf import CSRFProtect
from config import config
from urls import api

app = Flask(__name__)
CORS(app)

app.config.from_object(config['default'])

# csrf = CSRFProtect(app)
api.init_app(app)

