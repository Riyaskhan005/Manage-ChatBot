import json

from flask import Flask, render_template,request,jsonify, session
from sqlalchemy import func
from NocodeChatbot.extensions import db
from NocodeChatbot.dashboard import bp
from NocodeChatbot.models.chatbot import ManageChatbot
from NocodeChatbot.models.chatbotbuilder import ChatbotBuilder
from NocodeChatbot.models.dataextraction import DataExtractor
from NocodeChatbot.models.models import ManageModels
from NocodeChatbot.models.projects import Projects
from NocodeChatbot.utils.logwritter import LogWriter 
# from NocodeChatbot.utils.login_requried import login_required
log_writer_ = LogWriter()


@bp.route('/')
# @login_required
def index():
    return render_template("dashboard.html")


@bp.route('/get_data', methods=['GET'])
def dashboard_stats():
    return_msg = {}

    try:
        # Check login session
        if 'CustomerId' not in session:
            return_msg["error_code"] = 401
            return_msg["msg"] = "Unauthorized. Please login."
            return json.dumps(return_msg)

        customer_id = session['CustomerId']

        # Count Projects
        projects_count = Projects.query.filter_by(
            customer_id=customer_id,
            status="Active"
        ).count()

        # Count Data Extractors
        extrators_count = DataExtractor.query.filter_by(
            customer_id=customer_id,
            status="Active"
        ).count()

        # Count Chatbots
        chatbot_count = ManageChatbot.query.filter_by(
            customer_id=customer_id,
            status="Active"
        ).count()

        # Count Models
        model_count = ManageModels.query.filter_by(
            customer_id=customer_id,
            status="Active"
        ).count()

        return_msg["error_code"] = 0
        return_msg["projects"] = projects_count
        return_msg["extractors"] = extrators_count
        return_msg["chatbots"] = chatbot_count
        return_msg["models"] = model_count

        return json.dumps(return_msg)

    except Exception as e:
        return_msg["error_code"] = 99
        return_msg["msg"] = f"Unexpected error: {str(e)}"
        log_writer_.log_exception("dashboard", "dashboard_stats", e)
        return json.dumps(return_msg)
    

@bp.route('/get_project_chart', methods=['GET'])
def get_project_chart():
    return_msg = {}

    try:
        if 'CustomerId' not in session:
            return_msg["error_code"] = 401
            return json.dumps(return_msg)

        customer_id = session['CustomerId']

        # Join Projects with ChatbotBuilder and count usage
        results = (
            db.session.query(
                Projects.project_name,
                func.count(ChatbotBuilder.id).label("usage_count")
            )
            .join(ChatbotBuilder, Projects.id == ChatbotBuilder.project_id)
            .filter(Projects.customer_id == customer_id)
            .group_by(Projects.project_name)
            .all()
        )

        labels = []
        data = []

        for row in results:
            labels.append(row.project_name)
            data.append(row.usage_count)

        return_msg["error_code"] = 0
        return_msg["labels"] = labels
        return_msg["data"] = data

        return json.dumps(return_msg)

    except Exception as e:
        return_msg["error_code"] = 99
        return_msg["msg"] = str(e)
        log_writer_.log_exception("dashboard", "get_project_chart", e)
        return json.dumps(return_msg)