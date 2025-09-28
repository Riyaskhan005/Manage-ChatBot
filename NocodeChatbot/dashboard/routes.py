from flask import Flask, render_template,request,jsonify
from NocodeChatbot.extensions import db
from NocodeChatbot.dashboard import bp
from NocodeChatbot.models.chatbot import ManageChatbot
# from NocodeChatbot.utils.logwritter import LogWriter 
# from NocodeChatbot.utils.login_requried import login_required
# logger = LogWriter()


@bp.route('/')
# @login_required
def index():
    return render_template("base.html")
