from flask import Blueprint

handler = Blueprint('handler', __name__)

from . import login, income, client_info

