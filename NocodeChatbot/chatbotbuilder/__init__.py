from flask import Blueprint

bp = Blueprint('chatbotbuilder', __name__)

from NocodeChatbot.chatbotbuilder import routes