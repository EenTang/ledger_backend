from . import handler
from flask import jsonify, request, current_app, abort
from app.models import ClientInfo
from app import db
from app.helper import result_fmt, success
from app.error import err_handler
from flask import current_app
from flask_cors import CORS, cross_origin


@handler.route('/client-info', methods=['GET', 'POST', 'PUT', 'DELETE'])
@cross_origin()
@err_handler
def client_info():
    if request.method == 'POST':
        return ClientInfo.add(**request.json)
    if request.method == 'GET':
        return ClientInfo.get(**request.args)
    if request.method == 'PUT':
        return ClientInfo.update(**request.json)
    if request.method == 'DELETE':
        return ClientInfo.delete(**request.args)
