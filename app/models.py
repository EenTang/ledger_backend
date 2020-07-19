from datetime import datetime, date
import uuid
import re
from app.helper import result_fmt, success, check_params
from flask import current_app
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from app.exceptions import NotAllowed, ResourceConflic, NotFound, Unauthorized, ParamsError
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine, Column, Integer, func
from sqlalchemy.ext.declarative import declarative_base
from app.helper import type_convert, gen_random_password
from sqlalchemy.orm import validates

Base = declarative_base()


class BaseModel(Base):
    __abstract__ = True
    id = Column(Integer, primary_key=True)
    page = 1
    page_size = 20

    def get_dict(self, mapping=None, ignore=None):
        result = {}
        mapping = {} if mapping is None else mapping
        ignore = [] if ignore is None else ignore
        for col in self.__table__.columns:
            if col.name not in ignore:
                result[mapping.get(col.name, col.name)] = type_convert(
                    getattr(self, col.name, None))
        return result


db = SQLAlchemy(model_class=BaseModel)


class Permission:
    READ = 1
    WRITE = 2
    DOWNLOAD = 4
    REVIEW = 8
    ADMIN = 16


class Boss(db.Model):

    __tablename__ = 'boss'

    boss_id = db.Column(db.String(64), unique=True)
    level = db.Column(db.Integer)
    create_time = db.Column(db.DATETIME, default=datetime.utcnow)
    expire_time = db.Column(db.DATETIME)
    stores = db.relationship('Store', backref='owner', lazy='dynamic')

    @staticmethod
    def add(**request):
        required = ["store_name", "phone"]
        check_params(request, required)
        boss = Boss()
        gb_id = uuid.uuid4()
        while Boss.query.filter_by(boss_id=gb_id).first():
            gb_id = uuid.uuid4()
        boss.boss_id = gb_id
        boss.level = 0
        boss.expire_time = '2099-12-29 00:00:00'
        request['boss_id'] = boss.boss_id
        store = Store.add_not_commit(**request)
        db.session.add(boss)
        db.session.add(store)
        db.session.commit()


class Store(db.Model):

    __tablename__ = 'store'

    boss_id = db.Column(db.String(64), db.ForeignKey(
        'boss.boss_id', onupdate="CASCADE", ondelete="CASCADE"))
    address = db.Column(db.String(64))
    name = db.Column(db.String(64))
    description = db.Column(db.Text)
    create_time = db.Column(db.DATETIME, default=datetime.utcnow)

    # users = db.relationship('User', backref='store', lazy='dynamic')

    @staticmethod
    def add_not_commit(**request):
        required = ["boss_id", "name"]
        check_params(request, required)
        if not Boss.filter_by(boss_id=request['boss_id']).first():
            raise NotFound("Boss not found!")
        store = Store()
        store.owner = request['boss_id']
        store.name = request['store_name']
        store.description = request['description']
        return store


class User(db.Model):
    __tablename__ = 'user'

    store_id = db.Column(db.Integer, db.ForeignKey('store.id', onupdate="CASCADE", ondelete="CASCADE"))
    role_id = db.Column(db.Integer, db.ForeignKey('role.id', onupdate="CASCADE", ondelete="CASCADE"))
    name = db.Column(db.String(64))
    password = db.Column(db.String(64))
    phone = db.Column(db.String(64))
    wechat = db.Column(db.String(64))

    @validates('phone')
    def validate_phone(self, key, value):
        phone_pat = re.compile('^(13\d|14[5|7]|15\d|166|17[3|6|7]|18\d)\d{8}$')
        res = re.search(phone_pat, value)
        if not res:
            raise ParamsError("请输入正确的手机号码!")
        return value

    def generate_auth_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'],
                       expires_in=expiration)
        return s.dumps({'id': self.id}).decode('utf-8')

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return None
        return User.query.get(data['id'])

    @staticmethod
    def add(store_id, **request):
        required = ["role_id", "name", "password", "phone"]
        check_params(request, required)
        user = User()
        user.store_id = store_id
        user.role_id = request['role_id']
        user.name = request['name']
        user.password = generate_password_hash(request['password'])
        user.phone = request['phone']
        user.wechat = request.get('wechat', '')
        db.session.add(user)
        db.session.commit()
        return success(data=user.get_dict(ignore={'password'}))

    @staticmethod
    def update(store_id, **request):
        required = ["user_id"]
        check_params(request, required)
        user = User.query.filter_by(id=request['user_id'], store_id=store_id).first()
        if user:
            user.name = request.get('name', user.name)
            user.phone = request.get('phone', user.phone)
            user.role_id = request.get('role_id', user.role_id)
            if user.role.name == 'Administrator':
                raise NotAllowed("不能更改角色为管理员。")
            db.session.commit()
        return success()

    @staticmethod
    def reset_password(store_id, **request):
        required = ["user_id"]
        check_params(request, required)
        user = User.query.filter_by(id=request['user_id'], store_id=store_id).first()
        if user:
            new_pass = gen_random_password()
            user.password = generate_password_hash(new_pass)
        db.session.commit()
        return success(data=new_pass)

    @staticmethod
    def update_passsword(store_id, user_id, **request):
        required = ['password']
        check_params(request, required)
        user = User.query.filter_by(id=user_id, store_id=store_id).first()
        if user:
            user.password = generate_password_hash(request['password'])
        db.session.add(user)
        db.session.commit()
        return success()

    @staticmethod
    def delete(store_id, **request):
        required = ["user_id"]
        check_params(request, required)
        user = User.query.filter_by(id=request['user_id'], store_id=store_id).first()
        if not user:
            raise NotFound()
        if user.role.name == 'Administrator':
            raise NotAllowed("不能删除 admin 用户。")
        db.session.delete(user)
        db.session.commit()
        return success()

    @staticmethod
    def verify_and_get(phone, password):
        user = User.query.filter_by(phone=phone).first()
        return None if not user or not check_password_hash(user.password, password) else user

    @staticmethod
    def get(store_id, **request):
        page = int(request.get('page', 1))
        page_size = int(request.get('page_size', 20))
        query = User.query
        if request.get('name'):
            query = query.filter_by(name=request['name'])
        query = query.filter_by(store_id=store_id).paginate(page, page_size)
        res = []
        for item in query.items:
            if item.role.name == 'Administrator':
                continue
            data = item.get_dict(ignore={'password'})
            data['role'] = item.role.name
            res.append(data)
        return result_fmt(res, query)

    @staticmethod
    def me(store_id, user_id):
        query = User.query.filter_by(id=user_id, store_id=store_id).paginate(1, 20)
        res = []
        for item in query.items:
            data = item.get_dict(ignore={'password'})
            data['role'] = item.role.name
            res.append(data)
        return result_fmt(res, query)

    def __repr__(self):
        return '<User %r>' % self.name


class Role(db.Model):

    __tablename__ = 'role'

    name = db.Column(db.String(64))
    permissions = db.Column(db.Integer)
    users = db.relationship('User', backref='role', lazy='dynamic')

    @staticmethod
    def insert_roles():
        roles = {
            'Employee': [Permission.READ, Permission.WRITE],
            'Manager': [Permission.READ, Permission.WRITE, Permission.REVIEW],
            'Administrator': [Permission.READ, Permission.WRITE, Permission.REVIEW,
                              Permission.DOWNLOAD, Permission.ADMIN]
        }
        # default_role = 'Employee'
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            role.reset_permissions()
            for perm in roles[r]:
                role.add_permission(perm)
            # role.default = (role.name == default_role)
            db.session.add(role)
        db.session.commit()

    @staticmethod
    def get(**request):
        query = Role.query.filter(
            Role.name != 'Administrator').paginate(
            request.get(
                'page', 1), request.get(
                'page_size', 20))
        return result_fmt([item.get_dict() for item in query.items], query)

    def add_permission(self, perm):
        if not self.has_permission(perm):
            self.permissions += perm

    def remove_permission(self, perm):
        if self.has_permission(perm):
            self.permissions -= perm

    def reset_permissions(self):
        self.permissions = 0

    def has_permission(self, perm):
        return self.permissions & perm == perm

    def __repr__(self):
        return '<Role %r>' % self.name


class GoodsInfo(db.Model):

    __tablename__ = 'goods_info'

    store_id = db.Column(db.Integer, db.ForeignKey('store.id', onupdate="CASCADE", ondelete="CASCADE"))
    name = db.Column(db.String(64))
    unit_price = db.Column(db.Float)
    unit = db.Column(db.String(64))
    estimated_unit_price = db.Column(db.Float)
    estimated_total_price = db.Column(db.Float)
    description = db.Column(db.Text)


class ClientInfo(db.Model):

    __tablename__ = 'client_info'

    store_id = db.Column(db.Integer, db.ForeignKey('store.id', onupdate="CASCADE", ondelete="CASCADE"))
    name = db.Column(db.String(64))
    description = db.Column(db.Text, default='')
    phone = db.Column(db.String(64), default='')
    wechat = db.Column(db.String(64), default='')
    income_book = db.relationship('IncomeDetails', backref='client', lazy='dynamic')
    income_general = db.relationship('IncomeGeneral', backref='client', lazy='dynamic')

    @staticmethod
    def add(**request):
        required = ["client_name", "store_id"]
        check_params(request, required)
        stroe_id = request['store_id']
        name = request['client_name']
        exist = ClientInfo.query.filter_by(name=name, store=stroe_id).first()
        if exist:
            raise ResourceConflic("该姓名已经存在。")
        info = ClientInfo()
        info.store_id = stroe_id
        info.name = name
        info.description = request.get('description', '')
        info.phone = request.get('phone', '')
        info.wechat = request.get('wechat', '')
        db.session.add(info)
        db.session.commit()
        return success()

    @staticmethod
    def update(**request):
        required = ["client_id"]
        check_params(request, required)
        client_id = request.get('client_id')
        info = ClientInfo.query.filter_by(id=client_id).first()
        client_name = request.get("client_name")
        if info is None:
            raise NotFound('客户信息不存在。')
        if client_name:
            exist = ClientInfo.query.filter_by(name=client_name, store=info.store).first()
            if exist:
                raise ResourceConflic("该姓名已经存在。")
            else:
                info.name = client_name
        wechat = request.get('wechat')
        description = request.get('description')
        phone = request.get('phone')
        if wechat:
            info.wechat = wechat
        if description:
            info.description = description
        if phone:
            info.phone = phone
        db.session.commit()
        return success()

    @staticmethod
    def get(**request):
        required = ["store_id"]
        check_params(request, required)
        page = int(request.get('page', 1))
        page_size = int(request.get('page_size', 20))
        name = request.get('client_name')
        store_id = request['store_id']
        if name:
            query = (ClientInfo.query
                     .filter(ClientInfo.name.like(q(name)),
                             ClientInfo.store_id == store_id)
                     )
        else:
            query = (ClientInfo.query
                     .filter(ClientInfo.store_id == store_id)
                     )
        query = query.paginate(page, page_size)
        current_app.logger.info(query)
        info = query.items
        data = [{'client_name': item.name, 'client_id': item.id,
                 'wechat': item.wechat, 'phone': item.phone, 'description': item.description}
                for item in info]
        return result_fmt(data, query)

    @staticmethod
    def delete(**request):
        required = ["client_id"]
        check_params(request, required)
        client_id = request["client_id"]
        if IncomeGeneral.query.filter_by(client=client_id).count():
            raise NotAllowed("该客户存在账单，不能删除。")

        info = ClientInfo.query.filter_by(id=client_id).first()
        db.session.delete(info)
        db.session.commit()
        return success()

# class OrderGeneral(db.Model):

#     __tablename__ = 'order_general'

#     store = db.Column(db.Integer, db.ForeignKey('store.id', onupdate="CASCADE", ondelete="CASCADE"))
#     create_time = db.Column(db.DATETIME, default=datetime.utcnow)
#     estimated_total_price = db.Column(db.Float)


class OrderBook(db.Model):

    __tablename__ = 'order_book'

    client_id = db.Column(db.Integer, db.ForeignKey(
        'client_info.id', onupdate="CASCADE", ondelete="CASCADE"))
    store_id = db.Column(db.Integer, db.ForeignKey('store.id', onupdate="CASCADE", ondelete="CASCADE"))
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

    client_id = db.Column(db.Integer, db.ForeignKey(
        'client_info.id', onupdate="CASCADE", ondelete="CASCADE"))
    store_id = db.Column(db.Integer, db.ForeignKey('store.id', onupdate="CASCADE", ondelete="CASCADE"))

    debt = db.Column(db.Float)
    total = db.Column(db.Float)
    payed = db.Column(db.Float, default=0)
    create_time = db.Column(db.DATETIME, default=datetime.utcnow)
    update_time = db.Column(db.DATETIME, default=datetime.utcnow)
    analyze = db.Column(db.String(64))
    visible = db.Column(db.Boolean, default=True)
    create_date = db.Column(db.Date, default=date.today)

    def count_details(self):
        return IncomeDetails.query.filter_by(client=self.client, store_id=self.store_id, visible=1).count()

    @staticmethod
    def get(**request):
        page = int(request.get('page', 1))
        page_size = int(request.get('page_size', 10))
        query = IncomeGeneral.query
        if request.get('client_name'):
            query = query.join(IncomeGeneral.client).filter(ClientInfo.name == request.get('client_name'))
        current_app.logger.info(query)
        query = query.paginate(page, page_size)
        current_app.logger.info(query.items)
        data = []
        for item in query.items:
            item_info = item.get_dict(mapping={"id": "general_id"})
            item_info['name'] = item.client.name
            data.append(item_info)
        result = result_fmt(data, query)
        return result

    @staticmethod
    def add(**request):
        general = IncomeGeneral()
        general.store_id = request.get('store_id', 1)
        general.client_id = request['client_id']
        general.total = request['total']
        general.debt = request['total']
        general.visible = True
        db.session.add(general)
        db.session.commit()
        return success()

    @staticmethod
    def update(**request):
        general_id = request['general_id']
        general = IncomeGeneral.query.filter_by(id=general_id).first()
        if general:
            debt = request.get('debt', general.debt)
            total = request.get('total', general.total)
            payed = total - debt
            payed = payed if payed > 0 else 0
            general.debt = debt
            general.total = total
            general.payed = payed
            db.session.add(general)
            db.session.commit()
        return success()

    @staticmethod
    def delete(**request):
        general_id = request['general_id']
        general = IncomeGeneral.query.filter_by(id=general_id).first()
        if general.count_details() != 0:
            current_app.logger.info(general.count_details())
            raise NotAllowed("尚有未支付的订单，不能删除。")

        db.session.delete(general)
        db.session.commit()
        return success()


class IncomeDetails(db.Model):

    __tablename__ = 'income_details'

    id = db.Column(db.Integer, primary_key=True)

    client_id = db.Column(db.Integer, db.ForeignKey(
        'client_info.id', onupdate="CASCADE", ondelete="CASCADE"))
    store_id = db.Column(db.Integer, db.ForeignKey('store.id', onupdate="CASCADE", ondelete="CASCADE"))

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

    @classmethod
    def get_unpaid_bills(cls, **request):
        query = (
            db.session.query(
                IncomeDetails.client_id,
                ClientInfo.name,
                IncomeDetails.visible,
                func.sum(IncomeDetails.total_price))
            .join(IncomeDetails.client)
        )
        status = request.get('status')
        if status == 'unpaid':
            query = query.filter(IncomeDetails.visible == 1)
        elif status == 'paid':
            query = query.filter(IncomeDetails.visible == 0)
        query = query.group_by(IncomeDetails.client_id, IncomeDetails.visible
                               ).paginate(request.get('page', cls.page), request.get('page_size', cls.page_size))
        current_app.logger.info(query)
        res = query.items
        for r in res:
            current_app.logger.info(r)

    @staticmethod
    def update_payed(**request):
        detail = IncomeDetails.query.filter_by(id=request['detail_id']).first()
        if detail:
            detail.visible = False
            general = IncomeGeneral.query.filter_by(
                client=detail.client, store=detail.store_id).first()
            payed = general.payed + detail.total_price
            debt = general.total - payed
            general.debt = debt
            general.payed = payed
            db.session.commit()
        return success()

    def add(self, **request):
        total_price = float(request['unit_price']) * float(request['quantity'])
        self.client_id = request['client_id']
        self.store_id = request.get('store_id', 1)
        self.goods = request['goods']
        self.quantity = request['quantity']
        self.unit_price = request['unit_price']
        self.unit = request['unit']
        self.total_price = total_price
        self.description = ''
        self.analyze = 0
        self.visible = 1
        general = IncomeGeneral.query.filter_by(client=self.client, store_id=self.store_id).first()
        if not general:
            general = IncomeGeneral()
            general.store_id = self.store_id
            general.client_id = self.client_id
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
    def get(**request):
        page = int(request.get('page', 1))
        page_size = int(request.get('page_size', 10))
        query = IncomeDetails.query
        if request.get('client_id'):
            query = query.filter_by(client_id=request['client_id'])
        if request.get('goods'):
            query = query.filter(IncomeDetails.goods.like(q(request['goods'])))
        query = query.paginate(page, page_size)
        details = query.items
        data = []
        for item in details:
            item_info = item.get_dict(mapping={"id": "detail_id"})
            item_info['client_name'] = item.client.name
            data.append(item_info)
        return result_fmt(data, query)

    @staticmethod
    def update(**request):
        detail_id = request['detail_id']
        detail = IncomeDetails.query.filter_by(id=detail_id).first()
        if detail:
            total_price = float(request['unit_price']) * float(request['quantity'])
            detal = total_price - detail.total_price
            detail.goods = request["goods"]
            detail.quantity = request["quantity"]
            detail.unit_price = request["unit_price"]
            detail.unit = request["unit"]
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

    @staticmethod
    def delete(**request):
        detail_id = request["detail_id"]
        detail = IncomeDetails.query.filter_by(id=detail_id).first()
        if detail:
            general = IncomeGeneral.query.filter_by(
                store=detail.store, client=detail.client).first()
            total = general.total - detail.total_price
            debt = total - general.payed
            if general.debt <= 0:
                general.visible = False
            general.total = total if total >= 0 else 0
            general.debt = debt if debt >= 0 else 0
            db.session.delete(detail)
            db.session.commit()
        return success()


class CostGeneral(db.Model):

    __tablename__ = 'cost_general'

    client_id = db.Column(db.Integer, db.ForeignKey(
        'client_info.id', onupdate="CASCADE", ondelete="CASCADE"))
    store_id = db.Column(db.Integer, db.ForeignKey('store.id', onupdate="CASCADE", ondelete="CASCADE"))

    total = db.Column(db.Float)
    payed = db.Column(db.Float)
    remain = db.Column(db.Float)
    description = db.Column(db.Text)
    create_time = db.Column(db.DATETIME, default=datetime.utcnow)
    update_time = db.Column(db.DATETIME, default=datetime.utcnow)
    create_date = db.Column(db.Date, default=date.today)


class CostDetails(db.Model):

    __tablename__ = 'cost_details'

    client_id = db.Column(db.Integer, db.ForeignKey(
        'client_info.id', onupdate="CASCADE", ondelete="CASCADE"))
    store_id = db.Column(db.Integer, db.ForeignKey('store.id', onupdate="CASCADE", ondelete="CASCADE"))

    goods = db.Column(db.String(64))
    quantity = db.Column(db.Float)
    unit_price = db.Column(db.Float)
    unit = db.Column(db.String(64))
    total_price = db.Column(db.Float)
    description = db.Column(db.Text)
    create_time = db.Column(db.DATETIME, default=datetime.utcnow)
    update_time = db.Column(db.DATETIME, default=datetime.utcnow)
    create_date = db.Column(db.Date, default=date.today)


def q(arg):
    return "%" + arg + "%"
