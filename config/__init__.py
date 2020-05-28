from configparser import ConfigParser
from constant import DatabaseConf, APPConf

class Config:

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    db_config = ConfigParser()
    db_config.read(DatabaseConf)
    app_conf = ConfigParser()
    app_conf.read(APPConf)
    DEBUG = app_conf['dev']['DEBUG']
    SQLALCHEMY_DATABASE_URI = 'mysql://{user}:{password}@{host}:{port}/{database}'.format(**db_config['mysql'])


config = {
    'dev': DevelopmentConfig
}
