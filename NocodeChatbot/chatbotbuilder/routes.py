from flask import Flask, redirect, render_template,request,jsonify,session
from NocodeChatbot.extensions import db
from NocodeChatbot.chatbotbuilder import bp
from NocodeChatbot.models.chatbot import ManageChatbot
from NocodeChatbot.models.chatbotbuilder import ChatbotBuilder
from NocodeChatbot.models.models import ManageModels
from NocodeChatbot.utils.common import get_utc_now
import json
from NocodeChatbot.utils import common
from NocodeChatbot.utils.logwritter import LogWriter
from NocodeChatbot.chatbotbuilder.chatbotGenerator import ChatbotGenerator
log_writer_ = LogWriter()


@bp.route('/')
def index():
    return render_template("chatbotbuilder.html")


@bp.route('/get_builder_flow', methods=['POST'])
def get_builder_flow():
    return_msg = {}
    try:
        customer_id = session["CustomerId"]
        project_id = request.form.get("project_id")

        if not project_id:
            return_msg['msg'] = "Project ID is required."
            return_msg['error_code'] = 1
            return jsonify(return_msg)

        builder = ChatbotBuilder.query.filter_by(
            project_id=project_id,
            customer_id=customer_id,
            status="Active"
        ).first()

        if not builder:
            return_msg['error_code'] = 0
            return_msg['builder_flow_json'] = None
            return jsonify(return_msg)

        return_msg['error_code'] = 0
        return_msg['builder_flow_json'] = builder.builder_flow_json

    except Exception as e:
        return_msg['msg'] = "Something went wrong"
        return_msg['error_code'] = 1
        log_writer_.log_exception("chatbotbuilder", "get_builder_flow", e)

    return jsonify(return_msg)


@bp.route('/save_builder_flow', methods=['POST'])
def save_builder_flow():
    return_msg = {}
    try:
        customer_id = session["CustomerId"]
        project_id = request.form.get("project_id")
        builder_flow_json = request.form.get("builder_flow_json")

        if not project_id:
            return_msg['msg'] = "Project ID is required."
            return_msg['error_code'] = 1
            return jsonify(return_msg)

        if not builder_flow_json:
            return_msg['msg'] = "Builder flow data is required."
            return_msg['error_code'] = 1
            return jsonify(return_msg)

        existing_builder = ChatbotBuilder.query.filter_by(
            project_id=project_id,
            customer_id=customer_id,
            status="Active"
        ).first()

        if existing_builder:
            existing_builder.builder_flow_json = builder_flow_json
        else:
            new_builder = ChatbotBuilder(
                project_id=project_id,
                customer_id=customer_id,
                builder_flow_json=builder_flow_json,
                created_by=session.get("email"),
                created_on=get_utc_now(),
                status="Active"
            )
            db.session.add(new_builder)

        db.session.commit()

        return_msg['msg'] = "Chatbot builder flow saved successfully."
        return_msg['error_code'] = 0

    except Exception as e:
        db.session.rollback()
        return_msg['msg'] = "Something went wrong"
        return_msg['error_code'] = 1
        log_writer_.log_exception("chatbotbuilder", "save_builder_flow", e)

    return jsonify(return_msg)


@bp.route('/initiate_builder', methods=['POST'])
def initiate_builder():
    return_msg = {}
    try:
        customer_id = session["CustomerId"]
        project_id = request.form["project_id"]
        chatbot_id = request.form["chatbot_id"]
        dataextractor_id = request.form["data_extractor_id"]

        if not project_id:
            return_msg['msg'] = "Project ID is required."
            return_msg['error_code'] = 1
            return jsonify(return_msg)

        builder = ChatbotBuilder.query.filter_by(
            project_id=project_id,
            customer_id=customer_id,
            status="Active"
        ).first()

        if not builder or not builder.builder_flow_json:
            return_msg['msg'] = "No builder flow found for this project."
            return_msg['error_code'] = 1
            return jsonify(return_msg)

        builder_id = builder.id

        chatbot = ManageChatbot.query.filter_by(
            id = chatbot_id,
            project_id=project_id,
            customer_id=customer_id,
            status="Active"
        ).first()

        if not chatbot:
            return_msg['msg'] = "Chatbot config not found."
            return_msg['error_code'] = 1
            return jsonify(return_msg)
        
        model = ManageModels.query.filter_by(
            id=chatbot.chatbot_model,
            customer_id=customer_id,
            status="Active"
        ).first()

        if not model:
            return_msg['msg'] = "Model not found."
            return_msg['error_code'] = 1
            return jsonify(return_msg)

        model_id = model.id
        generator = ChatbotGenerator(customer_id,project_id,builder_id,model_id,dataextractor_id,chatbot.id)
        generator.generate_chatbot()

        return_msg['msg'] = "Chatbot initiated successfully."
        return_msg['error_code'] = 0

    except Exception as e:
        return_msg['msg'] = "Something went wrong"
        return_msg['error_code'] = 1
        log_writer_.log_exception("chatbotbuilder", "initiate_builder", e)

    return jsonify(return_msg)
