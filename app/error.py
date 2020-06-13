from flask import jsonify
# from app import handler

def conflict(message):
    response = jsonify({'error': 'conflict', 'message': message})
    response.status_code = 409
    return response

def not_found(message):
    response = jsonify({'error': 'not found', 'message': message})
    response.status_code = 404
    return response
