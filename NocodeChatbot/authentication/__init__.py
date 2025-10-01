from flask import Blueprint

bp = Blueprint('authentication', __name__)

from NocodeChatbot.authentication import routes