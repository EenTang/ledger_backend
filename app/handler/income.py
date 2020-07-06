from . import handler
from flask import jsonify, request, current_app, g
from app.models import IncomeDetails, ClientInfo, IncomeGeneral
from app import db
from app.helper import result_fmt, success, check_params, now
from app.error import bad_request, err_handler
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
        # IncomeDetails.get_unpaid_bills()
        return IncomeDetails.get(**request.args)
    elif request.method == 'PUT':
        required = ["unit_price", "quantity", "goods", "unit"]
        check_params(request.json, required)
        return IncomeDetails.update(**request.json)
    elif request.method == 'DELETE':
        required = ["detail_id"]
        check_params(request.args, required)
        return IncomeDetails.delete(**request.args)
    elif request.method == 'PATCH':
        required = ["detail_id"]
        check_params(request.json, required)
        current_app.logger.info(request.json)
        return IncomeDetails.update_payed(**request.json)


@handler.route('/income/general/', methods=['GET', 'POST', 'PUT', 'DELETE'])
@cross_origin()
@err_handler
def income_general():
    if request.method == 'POST':
        required = ['client_id', 'total']
        current_app.logger.info(request.json)
        check_params(request.json, required)
        return IncomeGeneral.add(**request.json)
    elif request.method == 'GET':
        # required = ["client_id"]
        # check_params(request.args, required)
        return IncomeGeneral.get(**request.args)
    elif request.method == 'PUT':
        required = ["general_id"]
        check_params(request.json, required)
        return IncomeGeneral.update(**request.json)
    elif request.method == 'DELETE':
        required = ["general_id"]
        check_params(request.args, required)
        return IncomeGeneral.delete(**request.args)
