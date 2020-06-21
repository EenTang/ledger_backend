from . import db
from datetime import datetime, date
from app.helper import result_fmt, success


class Boss(db.Model):

    __tablename__ = 'boss'

    boss_id = db.Column(db.String(64), unique=True)
    level = db.Column(db.Integer)
    create_time = db.Column(db.DATETIME, default=datetime.utcnow)
    expire_time = db.Column(db.DATETIME)


class Store(db.Model):

    __tablename__ = 'store'

    owner = db.Column(db.String(64), db.ForeignKey(
        'boss.boss_id', onupdate="CASCADE", ondelete="CASCADE"))
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

    owner = db.Column(db.String(64), db.ForeignKey(
        'boss.boss_id', onupdate="CASCADE", ondelete="CASCADE"))
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

    client = db.Column(db.Integer, db.ForeignKey(
        'client_info.id', onupdate="CASCADE", ondelete="CASCADE"))
    store = db.Column(db.Integer, db.ForeignKey('store.id', onupdate="CASCADE", ondelete="CASCADE"))
    goods = db.Column(db.String(64))
    quantity = db.Column(db.Float)
    unit = db.Column(db.String(64))
    estimated_unit_price = db.Column(db.Float)
    estimated_total_price = db.Column(db.Float)
    description = db.Column(db.Text)
    verify = db.Column(db.Boolean)
    create_time = db.Column(db.DATETIME, default=datetime.utcnow)
    create_date = db.Column(db.Date, default=date.today)


class IncomeGeneral(db.Model):

    __tablename__ = 'income_general'

    client = db.Column(db.Integer, db.ForeignKey(
        'client_info.id', onupdate="CASCADE", ondelete="CASCADE"))
    store = db.Column(db.Integer, db.ForeignKey('store.id', onupdate="CASCADE", ondelete="CASCADE"))

    debt = db.Column(db.Float)
    total = db.Column(db.Float)
    payed = db.Column(db.Float, default=0)
    create_time = db.Column(db.DATETIME, default=datetime.utcnow)
    update_time = db.Column(db.DATETIME, default=datetime.utcnow)
    analyze = db.Column(db.String(64))
    visible = db.Column(db.Boolean, default=True)
    create_date = db.Column(db.Date, default=date.today)

    def count_details(self):
        return IncomeDetails.query.filter_by(client=self.client, store=self.store, visible=1).count()


class IncomeDetails(db.Model):

    __tablename__ = 'income_details'

    id = db.Column(db.Integer, primary_key=True)

    client = db.Column(db.Integer, db.ForeignKey(
        'client_info.id', onupdate="CASCADE", ondelete="CASCADE"))
    store = db.Column(db.Integer, db.ForeignKey('store.id', onupdate="CASCADE", ondelete="CASCADE"))

    goods = db.Column(db.String(64))
    quantity = db.Column(db.Float)
    unit_price = db.Column(db.Float)
    unit = db.Column(db.String(64))
    total_price = db.Column(db.Float)
    description = db.Column(db.Text)
    create_time = db.Column(db.DATETIME, default=datetime.utcnow)
    update_time = db.Column(db.DATETIME, default=datetime.utcnow)
    analyze = db.Column(db.String(64))
    visible = db.Column(db.Boolean, default=True)
    create_date = db.Column(db.Date, default=date.today)

    def update_payed(self):
        general = IncomeGeneral.query.filter_by(client=self.client, store=self.store).first()
        if general:
            general.payed += self.total_price
            general.debt = general.total - self.total_price
        return general

    def add(self, **kwargs):
        total_price = float(kwargs['unit_price']) * float(kwargs['quantity'])
        self.client = kwargs['client_id']
        self.store = kwargs.get('store_id', 1)
        self.goods = kwargs['goods']
        self.quantity = kwargs['quantity']
        self.unit_price = kwargs['unit_price']
        self.unit = kwargs['unit']
        self.total_price = total_price
        self.description = ''
        self.analyze = 0
        self.visible = 1
        general = IncomeGeneral.query.filter_by(client=self.client, store=self.store).first()
        if not general:
            general = IncomeGeneral()
            general.store = self.store
            general.client = self.client
            general.total = self.total_price
            general.debt = self.total_price
        else:
            general.total += self.total_price
            general.debt += self.total_price
        general.visible = True
        db.session.add(self)
        db.session.add(general)
        db.session.commit()
        return success()

    @staticmethod
    def get(**kwargs):
        page = int(kwargs.get('page', 1))
        page_size = int(kwargs.get('page_size', 10))
        query = query_with_client_info(IncomeDetails, page, page_size, **kwargs)
        details = query.items
        data = []
        for item, client_name in details:
            item_info = item.get_dict(mapping={"client": "client_id", "id": "detail_id"})
            item_info['client_name'] = client_name
            data.append(item_info)
        return result_fmt(data, query)

    @staticmethod
    def update(**kwargs):
        detail_id = kwargs['detail_id']
        detail = IncomeDetails.query.filter_by(id=detail_id).first()
        if detail:
            total_price = float(kwargs['unit_price']) * float(kwargs['quantity'])
            detal = total_price - detail.total_price
            detail.goods = kwargs["goods"]
            detail.quantity = kwargs["quantity"]
            detail.unit_price = kwargs["unit_price"]
            detail.unit = kwargs["unit"]
            detail.total_price = total_price

            general = IncomeGeneral.query.filter_by(
                store=detail.store, client=detail.client).first()
            total = general.total + detal
            debt = total - general.payed
            if general.debt <= 0:
                general.visible = False
            general.total = total if total >= 0 else 0
            general.debt = debt if debt >= 0 else 0
            db.session.commit()
        return success()


class CostGeneral(db.Model):

    __tablename__ = 'cost_general'

    client = db.Column(db.Integer, db.ForeignKey(
        'client_info.id', onupdate="CASCADE", ondelete="CASCADE"))
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

    client = db.Column(db.Integer, db.ForeignKey(
        'client_info.id', onupdate="CASCADE", ondelete="CASCADE"))
    store = db.Column(db.Integer, db.ForeignKey('store.id', onupdate="CASCADE", ondelete="CASCADE"))

    goods = db.Column(db.String(64))
    quantity = db.Column(db.Float)
    unit_price = db.Column(db.Float)
    unit = db.Column(db.String(64))
    total_price = db.Column(db.Float)
    description = db.Column(db.Text)
    create_time = db.Column(db.DATETIME, default=datetime.utcnow)
    update_time = db.Column(db.DATETIME, default=datetime.utcnow)
    create_date = db.Column(db.Date, default=date.today)


def like_query(arg):
    return "%" + arg + "%"


def query_with_client_info(module, page, page_size, **kwargs):
    query = module.query.join(ClientInfo, ClientInfo.id == module.client)
    if kwargs.get("client_id"):
        query = query.filter(ClientInfo.id == kwargs['client_id'])
    elif kwargs.get("client_name"):
        query = query.filter(ClientInfo.name.like(like_query(kwargs['client_name'])))
    elif kwargs.get("goods"):
        query = query.filter(module.goods.like(like_query(kwargs['goods'])))
    query = query.filter(module.visible == kwargs.get("has_payed", 1)).with_entities(
        module, ClientInfo.name).paginate(page, page_size)
    return query
