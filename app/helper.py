from flask import jsonify

def result_fmt(data, query):
    return jsonify({"data": data, "total": query.total, "page": query.page, "pages": query.pages})

def success(message='success'):
    return jsonify({'message': message})