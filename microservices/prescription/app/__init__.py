from flask import Flask
from flask_cors import CORS

from app.config import Config
from app.database import init_db


def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(Config)
    init_db()
    from . import api
    app.register_blueprint(api.bp)
    return app
