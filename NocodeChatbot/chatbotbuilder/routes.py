from flask import Flask, redirect, render_template,request,jsonify,session
from NocodeChatbot.extensions import db
from NocodeChatbot.chatbotbuilder import bp
from NocodeChatbot.models.chatbotbuilder import ChatbotBuilder
from NocodeChatbot.utils.common import get_utc_now
import json
from NocodeChatbot.utils import common
from NocodeChatbot.utils.logwritter import LogWriter
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
