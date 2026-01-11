from flask import Blueprint

bp = Blueprint('dataextractor', __name__)

from NocodeChatbot.dataextractor import routes