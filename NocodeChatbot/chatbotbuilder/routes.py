from flask import Flask, redirect, render_template,request,jsonify,session
from NocodeChatbot.extensions import db
from NocodeChatbot.chatbotbuilder import bp
from NocodeChatbot.models.Customer import Customers
import json
from NocodeChatbot.utils import common
from NocodeChatbot.utils.logwritter import LogWriter
log_writer_ = LogWriter()


@bp.route('/')
def index():
    return render_template("chatbotbuilder.html")

