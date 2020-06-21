from . import handler
from flask import jsonify, request, current_app
from app.models import IncomeDetails, ClientInfo, IncomeGeneral, query_with_client_info
from app import db
from app.helper import result_fmt, success, check_params, now
from app.error import bad_request, err_handler
from app.exceptions import NotAllowed
from flask_cors import cross_origin
# from app.exceptions import ParamsError


@handler.route('/income/details/', methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH'])
@cross_origin()
@err_handler
def income_details():
    if request.method == 'POST':
        required = ["client_id", "goods", "quantity", "unit_price", "unit"]
        check_params(request.json, required)
        return IncomeDetails().add(**request.json)
    elif request.method == 'GET':
        return IncomeDetails.get(**request.args)
    elif request.method == 'PUT':
        required = ["unit_price", "quantity", "goods", "unit"]
        check_params(request.json, required)
        return IncomeDetails.update(**request.json)
    elif request.method == 'DELETE':
        required = ["detail_id"]
        check_params(request.args, required)
        delete_income_details(request.args)
        return success()
    elif request.method == 'PATCH':
        required = ["detail_id"]
        check_params(request.json, required)
        has_payed(request.json)
        return success()


def has_payed(req):
    detail = IncomeDetails.query.filter_by(id=req['detail_id']).first()
    if detail:
        detail.visible = False
        db.session.add(detail.update_payed())
        db.session.add(detail)
        db.session.commit()


def delete_income_details(req):
    detail_id = req["detail_id"]
    detail = IncomeDetails.query.filter_by(id=detail_id).first()
    if detail:
        general = IncomeGeneral.query.filter_by(store=detail.store, client=detail.client).first()
        total = general.total - detail.total_price
        debt = general.debt - detail.total_price
        general.payed += detail.total_price
        if general.debt <= 0:
            general.visible = False
        general.total = total if total >= 0 else 0
        general.debt = debt if debt >= 0 else 0
        db.session.delete(detail)
        db.session.commit()


def update_income_detail(req):
    detail_id = req.pop('detail_id')
    detail = IncomeDetails.query.filter_by(id=detail_id).first()
    if detail:
        total_price = float(req['unit_price']) * float(req['quantity'])
        detal = total_price - detail.total_price
        detail.goods = req["goods"]
        detail.quantity = req["quantity"]
        detail.unit_price = req["unit_price"]
        detail.unit = req["unit"]
        detail.total_price = total_price

        general = IncomeGeneral.query.filter_by(store=detail.store, client=detail.client).first()
        total = general.total + detal
        debt = general.debt + detal
        if general.debt <= 0:
            general.visible = False
        general.total = total if total >= 0 else 0
        general.debt = debt if debt >= 0 else 0
        db.session.commit()


def get_income_general(req):
    page = int(req.get('page', 1))
    page_size = int(req.get('page_size', 10))
    query = query_with_client_info(IncomeGeneral, page, page_size, **req)
    data = []
    for item, client_name in query.items:
        item_info = item.get_dict(mapping={"client": "client_id", "id": "general_id"})
        item_info['name'] = client_name
        data.append(item_info)
    result = result_fmt(data, query)
    return result


def add_income_general(req):
    general = IncomeGeneral()
    general.store = req.get('store_id', 1)
    general.client = req['client_id']
    general.total = req['total']
    general.debt = req['total']
    general.visible = True
    db.session.add(general)
    db.session.commit()


def update_income_general(req):
    general_id = req['general_id']
    general = IncomeGeneral.query.filter_by(id=general_id).first()
    if general:
        debt = req.get('debt', general.debt)
        total = req.get('total', general.total)
        payed = total - debt
        payed = payed if payed > 0 else 0
        general.debt = debt
        general.total = total
        general.payed = payed
        db.session.add(general)
        db.session.commit()


def delete_income_general(req):
    general_id = req['general_id']
    general = IncomeGeneral.query.filter_by(id=general_id).first()
    if general.count_details() != 0:
        current_app.logger.info(general.count_details())
        raise NotAllowed("尚有未支付的订单，不能删除。")

    db.session.delete(general)
    db.session.commit()


@handler.route('/income/general/', methods=['GET', 'POST', 'PUT', 'DELETE'])
@cross_origin()
@err_handler
def income_general():
    if request.method == 'POST':
        required = ['client_id', 'total']
        current_app.logger.info(request.json)
        check_params(request.json, required)
        add_income_general(request.json)
        return success()
    elif request.method == 'GET':
        # required = ["client_id"]
        # check_params(request.args, required)
        return get_income_general(request.args)
    elif request.method == 'PUT':
        required = ["general_id"]
        check_params(request.json, required)
        update_income_general(request.json)
        return success()
    elif request.method == 'DELETE':
        required = ["general_id"]
        check_params(request.args, required)
        delete_income_general(request.args)
        return success()
