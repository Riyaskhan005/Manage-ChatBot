from flask import Blueprint

bp = Blueprint('manageprojects', __name__)

from NocodeChatbot.manageprojects import routes