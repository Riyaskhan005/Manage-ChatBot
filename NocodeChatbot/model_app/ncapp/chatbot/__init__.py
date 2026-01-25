from flask import Blueprint

bp = Blueprint('chatbot', __name__)

from ncapp.chatbot import routes