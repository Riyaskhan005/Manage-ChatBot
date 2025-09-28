from flask import Flask, render_template,request,jsonify
from NocodeChatbot.extensions import db
from NocodeChatbot.manageprojects import bp
from NocodeChatbot.models.projects import Projects
# from NocodeChatbot.utils.logwritter import LogWriter 
# from NocodeChatbot.utils.login_requried import login_required
# logger = LogWriter()


@bp.route('/')
# @login_required
def index():
    return render_template("projects.html")
