from flask import Flask, render_template,request,jsonify,session
from NocodeChatbot.extensions import db
from NocodeChatbot.managemodels import bp
from NocodeChatbot.models.chatbot import ManageChatbot
from NocodeChatbot.models.Customer import Customers
from NocodeChatbot.models.projects import Projects
from NocodeChatbot.models.models import ManageModels
from NocodeChatbot.utils.logwritter import LogWriter
from NocodeChatbot.utils.common import get_utc_now
# from NocodeChatbot.utils.login_requried import login_required
log_writer_ = LogWriter()
import json


@bp.route('/')
# @login_required
def index():
    return render_template("models.html")

@bp.route('/load_models', methods=['GET'])
def load_models():
    try:
        customer_id = session.get("CustomerId")
        if not customer_id:
            return jsonify({"error_code": 1, "msg": "Customer not logged in"})

        project_id = request.args.get("project_id")
        if not project_id:
            return jsonify({"error_code": 2, "msg": "Project ID is required"})

        models = ManageModels.query.filter_by(customer_id=customer_id, project_id=project_id).all()

        models_list = []
        for model in models:
            models_list.append({
                "id": model.id,
                "project_id": model.project_id,
                "customer_id": model.customer_id,
                "config": model.model_config,
                "model_name": model.model_name,
                "model_key": model.model_key,
                "model_version": model.model_version,
                "created_by": model.created_by,
                "created_on": model.created_on,
                "status": model.status
            })

        return jsonify({"error_code": 0, "models": models_list})

    except Exception as e:
        log_writer_.log_exception("managemodels", "load_models", e)
        return jsonify({"error_code": 1, "msg": f"Error loading models: {str(e)}"}), 500

@bp.route("/save_model", methods=["POST"])
def save_model():
    return_msg = {}
    try:
        project_id = request.form.get("project_id")
        config = request.form.get("config")
        model_name = request.form.get("name")
        model_key = request.form.get("key")
        model_version = request.form.get("version")
        customer_id = session.get('CustomerId')
        customer_email = session.get('email')


        if not customer_id or not customer_email:
            return_msg["error_code"] = 1
            return_msg["msg"] = "Customer not logged in"
            return json.dumps(return_msg)

        existing_model = ManageModels.query.filter_by(
            project_id=project_id,
            model_name=model_name
        ).first()

        if existing_model:
            return_msg["error_code"] = 3
            return_msg["msg"] = "Model name already exists for this project"
            return json.dumps(return_msg)

        model = ManageModels(
            project_id=project_id,
            customer_id=customer_id,
            model_config=config,
            model_name=model_name,
            model_key=model_key,
            model_version=model_version,
            created_by=customer_email,
            created_on=get_utc_now(),
            status="Active"
        )
        db.session.add(model)
        db.session.commit()

        return_msg["error_code"] = 0
        return_msg["msg"] = "Model saved successfully"
        return json.dumps(return_msg)

    except Exception as e:
        db.session.rollback()
        return_msg["error_code"] = 1
        return_msg["msg"] = f"Error saving model: {str(e)}"
        log_writer_.log_exception("managemodels", "save_model", e)
        return json.dumps(return_msg), 500

@bp.route("/update_model", methods=["POST"])
def update_model():
    return_msg = {}
    try:
        model_id = request.form.get("id")
        config = request.form.get("config")
        name = request.form.get("name")
        key = request.form.get("key")
        version = request.form.get("version")
        customer_id = session.get("CustomerId")

        if not customer_id:
            return_msg["error_code"] = 1
            return_msg["msg"] = "Customer not logged in"
            return json.dumps(return_msg)

        updated_rows = ManageModels.query.filter_by(id=model_id, customer_id=customer_id).update({
            "model_config": config,
            "model_name": name,
            "model_key": key,
            "model_version": version
        })

        if not updated_rows:
            return_msg["error_code"] = 2
            return_msg["msg"] = "Model not found"
            return json.dumps(return_msg)

        db.session.commit()

        return_msg["error_code"] = 0
        return_msg["msg"] = "Model updated successfully"
        return json.dumps(return_msg)

    except Exception as e:
        db.session.rollback()
        log_writer_.log_exception("managemodels", "update_model", e)
        return_msg["error_code"] = 1
        return_msg["msg"] = f"Error updating model: {str(e)}"
        return json.dumps(return_msg), 500

@bp.route("/delete_model", methods=["POST"])
def delete_model():
    return_msg = {}
    try:
        model_id = request.form.get("id")
        customer_id = session.get("CustomerId")

        if not customer_id:
            return_msg["error_code"] = 1
            return_msg["msg"] = "Customer not logged in"
            return json.dumps(return_msg)

        model = ManageModels.query.filter_by(id=model_id, customer_id=customer_id).first()
        if not model:
            return_msg["error_code"] = 2
            return_msg["msg"] = "Model not found"
            return json.dumps(return_msg)

        db.session.delete(model)
        db.session.commit()

        return_msg["error_code"] = 0
        return_msg["msg"] = "Model deleted successfully"
        return json.dumps(return_msg)

    except Exception as e:
        db.session.rollback()
        log_writer_.log_exception("managemodels", "delete_model", e)
        return_msg["error_code"] = 1
        return_msg["msg"] = f"Error deleting model: {str(e)}"
        return json.dumps(return_msg), 500