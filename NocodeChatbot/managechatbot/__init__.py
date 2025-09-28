from flask import Blueprint

bp = Blueprint('managechatbot', __name__)

from NocodeChatbot.managechatbot import routes