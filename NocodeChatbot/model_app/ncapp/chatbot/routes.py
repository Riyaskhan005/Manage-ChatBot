from flask import Flask, render_template,request,jsonify,session
import json
from ncapp.chatbot import bp
from ncapp.ncutils.logwritter import LogWriter 
log_writer_ = LogWriter()


@bp.route('/')
def index():
    return render_template("chatbot.html")