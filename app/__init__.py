import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.declarative import declarative_base
from config import config
from sqlalchemy import create_engine, Column, Integer
from flask_cors import CORS
from app.helper import type_convert
from app.models import db, Role, Base


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    app.secret_key = bytes(os.environ.get('SECRECT_KEY'), "utf8")
    config[config_name].init_app(app)
    engine = create_engine(config[config_name].SQLALCHEMY_DATABASE_URI, convert_unicode=True)
    db.init_app(app)
    Base.engine = engine
    with app.app_context():
        Role.insert_roles()
    from .handler import handler
    app.register_blueprint(handler, url_prefix='/api/v1')
    CORS(app, supports_credentials=True)
    # CORS(handler, supports_credentials=True)

    return app
