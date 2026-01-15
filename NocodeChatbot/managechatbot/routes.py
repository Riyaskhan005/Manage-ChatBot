from flask import Flask, render_template,request,jsonify,session
import json
from NocodeChatbot.extensions import db
from NocodeChatbot.managechatbot import bp
from NocodeChatbot.models.chatbot import ManageChatbot
from NocodeChatbot.models.Customer import Customers
from NocodeChatbot.models.projects import Projects
from NocodeChatbot.models.models import ManageModels
from NocodeChatbot.utils.logwritter import LogWriter 
from NocodeChatbot.utils.common import get_utc_now
# from NocodeChatbot.utils.login_requried import login_required
log_writer_ = LogWriter()


@bp.route('/')
# @login_required
def index():
    return render_template("managechatbot.html")


@bp.route('/loadchatbot', methods=['POST','GET'])
def loadchatbot():
    return_msg = {}
    try:
        project_id = request.form["project_id"]
        customer_id = session["CustomerId"]
        if not customer_id:
            return_msg['msg'] = "Customer not logged in"
            return_msg['error_code'] = 1
            return jsonify(return_msg)

        # Query projects only for this customer
        chatbots = ManageChatbot.query.filter_by(customer_id=customer_id , project_id=project_id).all()
        chatbot_list = []
        for chatbot in chatbots:
            model = ManageModels.query.filter_by(id=chatbot.chatbot_model).first()
            chatbot_info = {
                'id': chatbot.id,
                'project_id': chatbot.project_id,
                'customer_id': chatbot.customer_id,
                'chatbot_name': chatbot.chatbot_name,
                'chatbot_domain': chatbot.chatbot_domain,
                'chatbot_model_name': model.model_name if model else "",
                'chatbot_model': chatbot.chatbot_model,
                'chatbot_color_code': chatbot.chatbot_color_code, 
                'chatbot_language': chatbot.chatbot_language,
                'chatbot_tone': chatbot.chatbot_tone,
                'chatbot_instructions': chatbot.chatbot_instructions,
                'created_by': chatbot.created_by,
                'created_on': chatbot.created_on,
                'status': chatbot.status
            }
            chatbot_list.append(chatbot_info)
        return_msg['chatbot_list'] = chatbot_list
        return_msg['msg'] = "Chatbots loaded successfully."
        return_msg['error_code'] = 0

    except Exception as e:
        return_msg['msg'] = "Something went wrong"
        return_msg['error_code'] = 1
        log_writer_.log_exception("managechatbot", "loadchatbots", e)
    return jsonify(return_msg)

@bp.route("/create_chatbot", methods=["POST"])
def create_chatbot():
    return_msg = {}
    try:
        customer_id = session.get("CustomerId")
        if not customer_id:
            return_msg['error_code'] = 1
            return_msg['msg'] = "Customer not logged in"
            return json.dumps(return_msg)

        project_id = request.form["project_id"]
        chatbot_name = request.form["chatbot_name"]
        chatbot_model = request.form["chatbot_model"]
        chatbot_domain = request.form["chatbot_domain"]
        chatbot_color_code = request.form["chatbot_color_code"]
        chatbot_language = request.form["chatbot_language"]
        chatbot_tone = request.form["chatbot_tone"]
        chatbot_instructions = request.form["chatbot_instructions"] or ""

        existing_bot = ManageChatbot.query.filter_by(
            project_id=project_id,
            customer_id=customer_id,
            chatbot_name=chatbot_name,
            status="Active"
        ).first()
        if existing_bot:
            return_msg['error_code'] = 1
            return_msg['msg'] = "Chatbot name already exists in this project."
            return json.dumps(return_msg)

        new_bot = ManageChatbot(
            project_id=project_id,
            customer_id=customer_id,
            chatbot_name=chatbot_name,
            chatbot_model=chatbot_model,
            chatbot_domain=chatbot_domain,
            chatbot_color_code=chatbot_color_code,
            chatbot_language=chatbot_language,
            chatbot_tone=chatbot_tone,
            chatbot_instructions=chatbot_instructions,
            created_by=customer_id,
            created_on=get_utc_now(),
            status="Active"
        )

        db.session.add(new_bot)
        db.session.commit()

        return_msg['error_code'] = 0
        return_msg['msg'] = "Chatbot created successfully"
        return json.dumps(return_msg)

    except Exception as e:
        db.session.rollback()
        log_writer_.log_exception("managechatbot", "create_chatbot", e)
        return_msg['error_code'] = 1
        return_msg['msg'] = "Something went wrong"
        return json.dumps(return_msg)
    
@bp.route("/update_chatbot", methods=["POST"])
def update_chatbot():
    return_msg = {}
    try:
        customer_id = session.get("CustomerId")
        if not customer_id:
            return_msg['error_code'] = 1
            return_msg['msg'] = "Customer not logged in"
            return json.dumps(return_msg)

        chatbot_id = request.form["chatbot_id"]
        project_id = request.form["project_id"]
        chatbot_name = request.form["chatbot_name"]
        chatbot_model = request.form["chatbot_model"]
        chatbot_domain = request.form["chatbot_domain"]
        chatbot_color_code = request.form["chatbot_color_code"]
        chatbot_language = request.form["chatbot_language"]
        chatbot_tone = request.form["chatbot_tone"]
        chatbot_instructions = request.form["chatbot_instructions"] or ""

        chatbot = ManageChatbot.query.filter_by(
            id=chatbot_id,
            customer_id=customer_id,
            status="Active"
        ).first()
        if not chatbot:
            return_msg['error_code'] = 1
            return_msg['msg'] = "Chatbot not found."
            return json.dumps(return_msg)

        chatbot.project_id = project_id
        chatbot.chatbot_name = chatbot_name
        chatbot.chatbot_model = chatbot_model
        chatbot.chatbot_domain = chatbot_domain
        chatbot.chatbot_color_code = chatbot_color_code
        chatbot.chatbot_language = chatbot_language
        chatbot.chatbot_tone = chatbot_tone
        chatbot.chatbot_instructions = chatbot_instructions

        db.session.commit()

        return_msg['error_code'] = 0
        return_msg['msg'] = "Chatbot updated successfully"
        return json.dumps(return_msg)

    except Exception as e:
        db.session.rollback()
        log_writer_.log_exception("managechatbot", "update_chatbot", e)
        return_msg['error_code'] = 1
        return_msg['msg'] = "Something went wrong"
        return json.dumps(return_msg)
    
@bp.route("/delete_chatbot", methods=["POST"])
def delete_chatbot():
    return_msg = {}
    try:
        customer_id = session.get("CustomerId")
        if not customer_id:
            return_msg["error_code"] = 1
            return_msg["msg"] = "Customer not logged in"
            return json.dumps(return_msg)

        chatbot_id = request.form.get("chatbot_id")
        if not chatbot_id:
            return_msg["error_code"] = 1
            return_msg["msg"] = "Chatbot id missing"
            return json.dumps(return_msg)

        chatbot = ManageChatbot.query.filter_by(
            id=chatbot_id,
            customer_id=customer_id
        ).first()

        if not chatbot:
            return_msg["error_code"] = 1
            return_msg["msg"] = "Chatbot not found"
            return json.dumps(return_msg)

        db.session.delete(chatbot)
        db.session.commit()

        return_msg["error_code"] = 0
        return_msg["msg"] = "Chatbot deleted successfully"
        return json.dumps(return_msg)

    except Exception as e:
        db.session.rollback()
        log_writer_.log_exception("managechatbot", "delete_chatbot", e)
        return_msg["error_code"] = 1
        return_msg["msg"] = "Something went wrong"
        return json.dumps(return_msg)
