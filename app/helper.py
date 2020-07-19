import random
import string
from flask import jsonify
from datetime import datetime, date
from app.exceptions import ParamsError


def result_fmt(data, query):
    return jsonify({"data": data, "total": query.total, "page": query.page, "pages": query.pages})


def success(message='success', **kwargs):
    res = {'message': message}
    res.update(kwargs)
    return jsonify(res)


def fail(error='', message='fail'):
    return jsonify({'error': error, 'message': message})


def check_params(req, required):
    not_found_params = []
    for params in required:
        if not req.get(params):
            not_found_params.append(params)
    if any(not_found_params):
        err = "{params} is needed.".format(params=str(not_found_params))
        raise ParamsError(err)


def now():
    fmt = "%Y-%m-%d %H:%M:%S"
    return datetime.now()


DATE = "%Y-%m-%d"
DATE_TIME = "%Y-%m-%d %H:%M:%S"


def type_convert(value):
    if isinstance(value, date):
        return value.strftime(DATE)
    elif isinstance(value, datetime):
        return value.strftime(DATE)
    else:
        return value


def gen_random_password():
    return "".join(random.sample(string.ascii_letters + string.digits, 8))
