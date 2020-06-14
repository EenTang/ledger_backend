from . import handler
from flask import jsonify, request, current_app
from app.models import IncomeDetails, ClientInfo
from app import db
from app.helper import result_fmt, success
from flask_cors import cross_origin



@handler.route('/income/details/', methods=['GET', 'POST', 'PUT', 'DELETE'])
@cross_origin()
def income_details():
    if request.method in ['POST']:
        add_income_details(request.json['data'])
        return success()
    if request.method == 'GET':
        result = get_income_details(request.args)
        return result
    if request.method == 'PUT':
        update_income_detail(request.json['data'])
        return success()
    if request.method == 'DELETE':
        delete_income_details(request.args)
        return success()


def add_income_details(req):
    total_price = float(req['unit_price']) * float(req['quantity'])
    details = IncomeDetails()
    details.client = req['client_id']
    details.store = req.get('store_id', 1)
    details.goods = req['goods']
    details.quantity = req['quantity']
    details.unit_price = req['unit_price']
    details.unit = req['unit']
    details.total_price = total_price
    details.description = ''
    details.analyze = 0
    details.visible = 1
    db.session.add(details)
    db.session.commit()


def get_income_details(req):
    page = int(req.get('page', 1))
    page_size = int(req.get('page_size', 10))
    client_id = req.get('client_id')
    if client_id:
        query = IncomeDetails.query\
            .join(ClientInfo, ClientInfo.id == IncomeDetails.client)\
            .filter(ClientInfo.id == client_id)\
            .with_entities(IncomeDetails, ClientInfo.name)\
            .paginate(page, page_size)
    else:
        query = IncomeDetails.query\
            .join(ClientInfo, ClientInfo.id == IncomeDetails.client)\
            .with_entities(IncomeDetails, ClientInfo.name)\
            .paginate(page, page_size)
    details = query.items
    data = [{'client_name': client_name, 'client_id': item.client, 'goods': item.goods,
             'quantity': item.quantity, 'unit_price': item.unit_price, 'unit': item.unit,
             'total_price': item.total_price, 'create_date': str(item.create_date), 'detail_id': item.id}
            for item, client_name in details]
    result = result_fmt(data, query)
    return result

def delete_income_details(req):
    detail_id = req["detail_id"]
    IncomeDetails.query.filter_by(id=detail_id).delete()
    db.session.commit()

def update_income_detail(req):
    detail_id = req.pop('detail_id')
    detail = IncomeDetails.query.filter_by(id=detail_id).first()
    if detail:
        total_price = float(req['unit_price']) * float(req['quantity'])
        detail.goods = req["goods"]
        detail.quantity = req["quantity"]
        detail.unit_price = req["unit_price"]
        detail.unit = req["unit"]
        detail.total_price = total_price
        db.session.commit()




