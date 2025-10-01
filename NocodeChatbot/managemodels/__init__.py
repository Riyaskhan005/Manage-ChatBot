from flask import Blueprint

bp = Blueprint('managemodels', __name__)

from NocodeChatbot.managemodels import routes