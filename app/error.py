from flask import jsonify
from app.helper import fail
from functools import wraps
from app.exceptions import ParamsError, BaseError, NotAllowed
# from app import handler


def conflict(message):
    response = fail('conflict', message)
    response.status_code = 409
    return response


def not_found(message):
    response = fail('not found', message)
    response.status_code = 404
    return response


def bad_request(message="bad request"):
    response = fail('bad request', message)
    response.status_code = 400
    return response


def unexpected_err(message="Internal Server Error"):
    response = fail("Internal Server Error", message)
    response.status_code = 500
    return response


def forbidden(message="forbidden"):
    response = fail("Forbidden", message)
    response.status_code = 403
    return response


def err_handler(fun):
    @wraps(fun)
    def wrapper(*args, **kwargs):
        try:
            result = fun(*args, **kwargs)
            return result
        except ParamsError as err:
            return bad_request(str(err))
        except NotAllowed as err:
            return forbidden(str(err))
        except BaseError as err:
            return unexpected_err()
    return wrapper
