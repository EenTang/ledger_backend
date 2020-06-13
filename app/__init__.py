from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.declarative import declarative_base
from config import config
from sqlalchemy import create_engine, Column, Integer
from flask_cors import CORS

Base = declarative_base()


class BaseModel(Base):
    __abstract__ = True
    id = Column(Integer, primary_key=True)


db = SQLAlchemy(model_class=BaseModel)


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    db.init_app(app)
    engine = create_engine(config[config_name].SQLALCHEMY_DATABASE_URI, convert_unicode=True)
    Base.engine = engine
    from .handler import handler
    app.register_blueprint(handler, url_prefix='/api/v1')
    CORS(app, supports_credentials=True)
    # CORS(handler, supports_credentials=True)

    return app
