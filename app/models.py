from . import *
from app import db
from datetime import datetime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class BaseModel(Base):
    __abstract__ = True
    id = db.Column(db.Integer, primary_key=True)


class Boss(BaseModel):

    __tablename__ = 'boss'

    boss_id = db.Column(db.String(64), unique=True)
    level = db.Column(db.Integer)
    create_time = db.Column(db.DATETIME, default=datetime.utcnow)
    expire_time = db.Column(db.DATETIME)

class Store(BaseModel):

    __tablename__ = 'store'

    owner = db.Column(db.String(64), db.ForeignKey('boss.boss_id', onupdate="CASCADE", ondelete="CASCADE"))
    address = db.Column(db.String(64))
    name = db.Column(db.String(64))
    description = db.Column(db.Text)
    create_time = db.Column(db.DATETIME, default=datetime.utcnow)


class User(BaseModel):
    __tablename__ = 'user'

    owner = db.Column(db.String(64), db.ForeignKey('boss.boss_id', onupdate="CASCADE", ondelete="CASCADE"))
    role = db.Column(db.Integer, db.ForeignKey('role.id', onupdate="CASCADE", ondelete="CASCADE"))
    name = db.Column(db.String(64))
    password = db.Column(db.String(64))
    phone = db.Column(db.String(64))
    wechat = db.Column(db.String(64))


class Role(BaseModel):

    __tablename__ = 'role'

    name = db.Column(db.String(64))
    module_permission = db.Column(db.Text)


class OrderGeneral(BaseModel):

    __tablename__ = 'order_general'

    owner = db.Column(db.String(64), db.ForeignKey('boss.boss_id', onupdate="CASCADE", ondelete="CASCADE"))
    create_time = db.Column(db.DATETIME, default=datetime.utcnow)
    estimated_total_price = db.Column(db.Float)


class GoodsInfo(BaseModel):

    __tablename__ = 'goods_info'

    owner = db.Column(db.String(64), db.ForeignKey('boss.boss_id', onupdate="CASCADE", ondelete="CASCADE"))
    name = db.Column(db.String(64))
    unit_price = db.Column(db.Float)
    unit = db.Column(db.String(64))
    estimated_unit_price = db.Column(db.Float)
    estimated_total_price = db.Column(db.Float)
    description = db.Column(db.Text)


class ClientInfo(BaseModel):

    __tablename__ = 'client_info'

    owner = db.Column(db.String(64), db.ForeignKey('boss.boss_id', onupdate="CASCADE", ondelete="CASCADE"))
    name = db.Column(db.String(64))
    description = db.Column(db.Text)
    phone = db.Column(db.String(64))
    wechat = db.Column(db.String(64))


class OrderBook(BaseModel):

    __tablename__ = 'order_book'

    client = db.Column(db.Integer, db.ForeignKey('client_info.id', onupdate="CASCADE", ondelete="CASCADE"))
    owner = db.Column(db.String(64), db.ForeignKey('boss.boss_id', onupdate="CASCADE", ondelete="CASCADE"))
    goods = db.Column(db.String(64))
    quantity = db.Column(db.Integer)
    unit = db.Column(db.String(64))
    estimated_unit_price = db.Column(db.Float)
    estimated_total_price = db.Column(db.Float)
    description = db.Column(db.Text)
    verify = db.Column(db.Boolean)
    create_time = db.Column(db.DATETIME, default=datetime.utcnow)




class IncomeGeneral(BaseModel):

    __tablename__ = 'income_general'

    client = db.Column(db.Integer, db.ForeignKey('client_info.id', onupdate="CASCADE", ondelete="CASCADE"))
    owner = db.Column(db.String(64), db.ForeignKey('boss.boss_id', onupdate="CASCADE", ondelete="CASCADE"))
    store = db.Column(db.Integer, db.ForeignKey('store.id', onupdate="CASCADE", ondelete="CASCADE"))

    debt = db.Column(db.Float)
    total = db.Column(db.Float)
    payed = db.Column(db.Float)
    create_time = db.Column(db.DATETIME, default=datetime.utcnow)
    update_time = db.Column(db.DATETIME, default=datetime.utcnow)
    analyze = db.Column(db.String(64))
    visible = db.Column(db.Boolean)


class IncomeDetails(BaseModel):

    __tablename__ = 'income_details'

    client = db.Column(db.Integer, db.ForeignKey('client_info.id', onupdate="CASCADE", ondelete="CASCADE"))
    owner = db.Column(db.String(64), db.ForeignKey('boss.boss_id', onupdate="CASCADE", ondelete="CASCADE"))
    store = db.Column(db.Integer, db.ForeignKey('store.id', onupdate="CASCADE", ondelete="CASCADE"))
    general = db.Column(db.Integer, db.ForeignKey('income_general.id', onupdate="CASCADE", ondelete="CASCADE"))

    goods = db.Column(db.String(64))
    quantity = db.Column(db.Integer)
    unit_price = db.Column(db.Float)
    unit = db.Column(db.String(64))
    total_price = db.Column(db.Float)
    description = db.Column(db.Text)
    create_time = db.Column(db.DATETIME, default=datetime.utcnow)
    update_time = db.Column(db.DATETIME, default=datetime.utcnow)
    analyze = db.Column(db.String(64))
    visible = db.Column(db.Boolean)


class CostGeneral(BaseModel):

    __tablename__ = 'cost_general'

    client = db.Column(db.Integer, db.ForeignKey('client_info.id', onupdate="CASCADE", ondelete="CASCADE"))
    owner = db.Column(db.String(64), db.ForeignKey('boss.boss_id', onupdate="CASCADE", ondelete="CASCADE"))
    store = db.Column(db.Integer, db.ForeignKey('store.id', onupdate="CASCADE", ondelete="CASCADE"))

    total = db.Column(db.Float)
    payed = db.Column(db.Float)
    remain = db.Column(db.Float)
    description = db.Column(db.Text)
    create_time = db.Column(db.DATETIME, default=datetime.utcnow)
    update_time = db.Column(db.DATETIME, default=datetime.utcnow)


class CostDetails(BaseModel):

    __tablename__ = 'cost_details'

    client = db.Column(db.Integer, db.ForeignKey('client_info.id', onupdate="CASCADE", ondelete="CASCADE"))
    owner = db.Column(db.String(64), db.ForeignKey('boss.boss_id', onupdate="CASCADE", ondelete="CASCADE"))
    store = db.Column(db.Integer, db.ForeignKey('store.id', onupdate="CASCADE", ondelete="CASCADE"))
    general = db.Column(db.Integer, db.ForeignKey('cost_general.id', onupdate="CASCADE", ondelete="CASCADE"))

    goods = db.Column(db.String(64))
    quantity = db.Column(db.Integer)
    unit_price = db.Column(db.Float)
    unit = db.Column(db.String(64))
    total_price = db.Column(db.Float)
    description = db.Column(db.Text)
    create_time = db.Column(db.DATETIME, default=datetime.utcnow)
    update_time = db.Column(db.DATETIME, default=datetime.utcnow)


if __name__ == '__main__':
    from sqlalchemy import create_engine
    uri = 'mysql://root:tangT#$1@192.168.31.225:3300/ledger'
    engine = create_engine(uri, convert_unicode=True)
    # create_app('dev')
    Base.metadata.create_all(bind=engine)










