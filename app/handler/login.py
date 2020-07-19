from . import handler
from flask import jsonify, request, current_app, session, g
from app.models import User, Role
from app import db
from app.helper import result_fmt, success, check_params, now
from app.error import bad_request, err_handler, forbidden, unauthorized
from app.exceptions import Unauthorized
from flask_cors import cross_origin
from flask_httpauth import HTTPBasicAuth

auth = HTTPBasicAuth()


@auth.verify_password
def verify_password(phone_or_token, password):
    if not phone_or_token:
        return False
    if not password:
        g.current_user = User.verify_auth_token(phone_or_token)
        g.token_used = True
    else:
        g.current_user = User.verify_and_get(phone=phone_or_token, password=password)
        g.token_used = False
    return g.current_user is not None


@auth.error_handler
def auth_error():
    return unauthorized('没有登录！')


@handler.before_request
@auth.login_required
def before_request():
    pass


@handler.route('/logout/', methods=['DELETE'])
@cross_origin()
@err_handler
def logout():
    g.current_user = None
    return success()


@handler.route('/auth/', methods=['GET'])
@cross_origin()
@err_handler
def authentication():
    return success()


@handler.route('/tokens/', methods=['POST', 'GET'])
@err_handler
def get_token():
    if g.token_used:
        raise Unauthorized("请使用用户名和密码获取 token。")
    return success(
        token=g.current_user.generate_auth_token(),
        username=g.current_user.name,
        role=g.current_user.role.name)


@handler.route('/user/details', methods=['GET', 'PUT'])
@cross_origin()
@err_handler
def details():
    pass


@handler.route('/admin/users/', methods=['GET', 'POST', 'DELETE', 'PUT', 'PATCH'])
@cross_origin()
@err_handler
def admin():
    if g.current_user.role.name != 'Administrator':
        return forbidden("没有足够权限")
    if request.method == 'GET':
        return User.get(g.current_user.store_id, **request.args)
    elif request.method == 'POST':
        return User.add(g.current_user.store_id, **request.json)
    elif request.method == 'DELETE':
        return User.delete(g.current_user.store_id, **request.args)
    elif request.method == 'PUT':
        return User.update(g.current_user.store_id, **request.json)
    elif request.method == 'PATCH':
        return User.reset_password(g.current_user.store_id, **request.json)


@handler.route('/me', methods=['GET', 'PATCH'])
@cross_origin()
@err_handler
def me():
    if request.method == 'GET':
        return User.me(g.current_user.store_id, g.current_user.id)
    elif request.method == 'PATCH':
        return User.update_passsword(g.current_user.store_id, g.current_user.id, **request.json)


@handler.route('/roles/', methods=['GET'])
@cross_origin()
@err_handler
def role():
    if g.current_user.role.name != 'Administrator':
        return forbidden("没有足够权限")
    return Role.get(**request.args)
