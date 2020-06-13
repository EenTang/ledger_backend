from . import handler
from flask import jsonify, request, current_app, abort
from app.models import ClientInfo
from app import db
from app.helper import result_fmt, success
from app.error import conflict, not_found
from flask import current_app
from flask_cors import CORS, cross_origin


@handler.route('/client-info', methods=['GET', 'POST', 'PUT', 'DELETE'])
@cross_origin()
def client_info():
    if request.method == 'POST':
        add_client_info(request.json)
        return success()
    if request.method == 'GET':
        result = get_client_info(request.args)
        return result
    if request.method == 'PUT':
        pass
    if request.method == 'DELETE':
        pass


def get_client_info(req):
    page = int(req.get('page', 1))
    page_size = int(req.get('page_size', 20))
    name = req.get('client_name')
    store_id = req['store_id']
    if name:
        query = (ClientInfo.query
            .filter(ClientInfo.name.like("%" + name + "%"),
                    ClientInfo.store == store_id)
            .paginate(page, page_size))
    else:
        query = (ClientInfo.query
            .filter(ClientInfo.store == store_id)
            .paginate(page, page_size))
    current_app.logger.info(query)
    info = query.items
    data = [{'client_name': item.name, 'client_id': item.id,
             'wechat': item.wechat, 'phone': item.phone, 'description': item.description}
             for item in info]
    return result_fmt(data, query)

def add_client_info(req):
    stroe_id = req['store_id']
    name = req['client_name']
    exist = ClientInfo.query.filter_by(name=name, store=stroe_id).first()
    if exist:
        return conflict("该姓名已经存在。")
    info = ClientInfo()
    info.store = stroe_id
    info.name = name
    info.description = req.get('description', '')
    info.phone = req.get('phone', '')
    info.wechat = req.get('wechat', '')
    db.session.add(info)
    db.session.commit()

def delelte_client_info(req):
    info = ClientInfo(req['stroe_id'], req['client_name'])
    db.session.delete(info)
    db.session.commit()

def update_client_info(req):
    stroe_id = req['store_id']
    name = req['name']
    info = ClientInfo.query.filter_by(name=name, store=stroe_id).first()
    if info is None:
        return not_found('客户信息不存在。')
    wechat = req.get('wechat')
    description = req.get('description')
    phone = req.get('phone')
    if wechat:
        info.wechat = wechat
    if description:
        info.description = description
    if phone:
        info.phone = phone
    db.session.commit()



