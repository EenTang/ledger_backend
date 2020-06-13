from . import db
from datetime import datetime, date


class Boss(db.Model):

    __tablename__ = 'boss'

    boss_id = db.Column(db.String(64), unique=True)
    level = db.Column(db.Integer)
    create_time = db.Column(db.DATETIME, default=datetime.utcnow)
    expire_time = db.Column(db.DATETIME)

class Store(db.Model):

    __tablename__ = 'store'

    owner = db.Column(db.String(64), db.ForeignKey('boss.boss_id', onupdate="CASCADE", ondelete="CASCADE"))
    address = db.Column(db.String(64))
    name = db.Column(db.String(64))
    description = db.Column(db.Text)
    create_time = db.Column(db.DATETIME, default=datetime.utcnow)


class User(db.Model):
    __tablename__ = 'user'

    store = db.Column(db.Integer, db.ForeignKey('store.id', onupdate="CASCADE", ondelete="CASCADE"))
    role = db.Column(db.Integer, db.ForeignKey('role.id', onupdate="CASCADE", ondelete="CASCADE"))
    name = db.Column(db.String(64))
    password = db.Column(db.String(64))
    phone = db.Column(db.String(64))
    wechat = db.Column(db.String(64))


class Role(db.Model):

    __tablename__ = 'role'

    owner = db.Column(db.String(64), db.ForeignKey('boss.boss_id', onupdate="CASCADE", ondelete="CASCADE"))
    name = db.Column(db.String(64))
    module_permission = db.Column(db.Text)


class GoodsInfo(db.Model):

    __tablename__ = 'goods_info'

    store = db.Column(db.Integer, db.ForeignKey('store.id', onupdate="CASCADE", ondelete="CASCADE"))
    name = db.Column(db.String(64))
    unit_price = db.Column(db.Float)
    unit = db.Column(db.String(64))
    estimated_unit_price = db.Column(db.Float)
    estimated_total_price = db.Column(db.Float)
    description = db.Column(db.Text)


class ClientInfo(db.Model):

    __tablename__ = 'client_info'

    store = db.Column(db.Integer, db.ForeignKey('store.id', onupdate="CASCADE", ondelete="CASCADE"))
    name = db.Column(db.String(64))
    description = db.Column(db.Text)
    phone = db.Column(db.String(64))
    wechat = db.Column(db.String(64))


# class OrderGeneral(db.Model):

#     __tablename__ = 'order_general'

#     store = db.Column(db.Integer, db.ForeignKey('store.id', onupdate="CASCADE", ondelete="CASCADE"))
#     create_time = db.Column(db.DATETIME, default=datetime.utcnow)
#     estimated_total_price = db.Column(db.Float)


class OrderBook(db.Model):

    __tablename__ = 'order_book'

    client = db.Column(db.Integer, db.ForeignKey('client_info.id', onupdate="CASCADE", ondelete="CASCADE"))
    store = db.Column(db.Integer, db.ForeignKey('store.id', onupdate="CASCADE", ondelete="CASCADE"))
    goods = db.Column(db.String(64))
    quantity = db.Column(db.Integer)
    unit = db.Column(db.String(64))
    estimated_unit_price = db.Column(db.Float)
    estimated_total_price = db.Column(db.Float)
    description = db.Column(db.Text)
    verify = db.Column(db.Boolean)
    create_time = db.Column(db.DATETIME, default=datetime.utcnow)
    create_date = db.Column(db.Date, default=date.today)


class IncomeGeneral(db.Model):

    __tablename__ = 'income_general'

    client = db.Column(db.Integer, db.ForeignKey('client_info.id', onupdate="CASCADE", ondelete="CASCADE"))
    store = db.Column(db.Integer, db.ForeignKey('store.id', onupdate="CASCADE", ondelete="CASCADE"))

    debt = db.Column(db.Float)
    total = db.Column(db.Float)
    payed = db.Column(db.Float)
    create_time = db.Column(db.DATETIME, default=datetime.utcnow)
    update_time = db.Column(db.DATETIME, default=datetime.utcnow)
    analyze = db.Column(db.String(64))
    visible = db.Column(db.Boolean)
    create_date = db.Column(db.Date, default=date.today)


class IncomeDetails(db.Model):

    __tablename__ = 'income_details'

    id = db.Column(db.Integer, primary_key=True)

    client = db.Column(db.Integer, db.ForeignKey('client_info.id', onupdate="CASCADE", ondelete="CASCADE"))
    store = db.Column(db.Integer, db.ForeignKey('store.id', onupdate="CASCADE", ondelete="CASCADE"))

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
    create_date = db.Column(db.Date, default=date.today)


class CostGeneral(db.Model):

    __tablename__ = 'cost_general'

    client = db.Column(db.Integer, db.ForeignKey('client_info.id', onupdate="CASCADE", ondelete="CASCADE"))
    store = db.Column(db.Integer, db.ForeignKey('store.id', onupdate="CASCADE", ondelete="CASCADE"))

    total = db.Column(db.Float)
    payed = db.Column(db.Float)
    remain = db.Column(db.Float)
    description = db.Column(db.Text)
    create_time = db.Column(db.DATETIME, default=datetime.utcnow)
    update_time = db.Column(db.DATETIME, default=datetime.utcnow)
    create_date = db.Column(db.Date, default=date.today)


class CostDetails(db.Model):

    __tablename__ = 'cost_details'

    client = db.Column(db.Integer, db.ForeignKey('client_info.id', onupdate="CASCADE", ondelete="CASCADE"))
    store = db.Column(db.Integer, db.ForeignKey('store.id', onupdate="CASCADE", ondelete="CASCADE"))

    goods = db.Column(db.String(64))
    quantity = db.Column(db.Integer)
    unit_price = db.Column(db.Float)
    unit = db.Column(db.String(64))
    total_price = db.Column(db.Float)
    description = db.Column(db.Text)
    create_time = db.Column(db.DATETIME, default=datetime.utcnow)
    update_time = db.Column(db.DATETIME, default=datetime.utcnow)
    create_date = db.Column(db.Date, default=date.today)







