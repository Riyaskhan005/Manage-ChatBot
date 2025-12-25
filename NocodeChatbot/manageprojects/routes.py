from asyncio.log import logger
from flask import Flask, render_template,request,jsonify, session
from NocodeChatbot.extensions import db
from NocodeChatbot.manageprojects import bp
from NocodeChatbot.models.projects import Projects
import json
from NocodeChatbot.utils.common import get_utc_now
from NocodeChatbot.utils.logwritter import LogWriter 
# from NocodeChatbot.utils.login_requried import login_required
log_writer_ = LogWriter()


@bp.route('/')
# @login_required
def index():
    return render_template("projects.html")

@bp.route('/loadprojects', methods=['GET'])
def load_projects():
    try:
        customer_id = session.get("CustomerId")
        if not customer_id:
            return jsonify({"error_code": 1, "msg": "Customer not logged in"})

        # Query projects only for this customer
        projects = Projects.query.filter_by(customer_id=customer_id).all()
        projects_list = [
            {
                "id": project.id,
                "customer_id": project.customer_id,
                "project_name": project.project_name,
                "project_details": project.project_details,
                "created_by": project.created_by,
                "created_on": project.created_on,
                "status": project.status
            }
            for project in projects
        ]
        return jsonify({"error_code": 0, "projects": projects_list})
    except Exception as e:
        log_writer_.log_exception("manageprojects", "load_projects", e)
        return jsonify({"error_code": 1, "msg": "Something went wrong"}), 500
    
@bp.route("/save_project", methods=["POST"])
def save_project():
    return_msg = {}
    try:
        project_name = request.form.get("project_name")
        project_details = request.form.get("project_details")
        customer_id = session.get('CustomerId')
        customer_email = session.get('email')
        
        if not customer_id or not customer_email:
            return_msg["error_code"] = 1
            return_msg["msg"] = "Customer not logged in"
            return json.dumps(return_msg) 

        existing_project = Projects.query.filter_by(
            customer_id=customer_id,
            project_name=project_name
        ).first()

        if existing_project:
            return_msg["error_code"] = 2
            return_msg["msg"] = "Project name already exists"
            return json.dumps(return_msg)

        project = Projects(
            customer_id=customer_id,
            project_name=project_name,
            project_details=project_details,
            created_by=customer_email,
            created_on=get_utc_now(),
            status="Active"
        )
        db.session.add(project)
        db.session.commit()

        return_msg["error_code"] = 0
        return_msg["msg"] = "Project saved successfully"
        return json.dumps(return_msg)

    except Exception as e:
        db.session.rollback()
        return_msg["error_code"] = 1
        return_msg["msg"] = "Something went wrong"
        log_writer_.log_exception("manageprojects", "save_project", e)
        return json.dumps(return_msg), 500
    

@bp.route("/update_project", methods=["POST"])
def update_project():
    return_msg = {}
    try:
        project_id = request.form.get("id")
        project_name = request.form.get("project_name")
        project_details = request.form.get("project_details")

        if not project_id:
            return_msg["error_code"] = 1
            return_msg["msg"] = "Project ID is required"
            return json.dumps(return_msg)

        updated_rows = Projects.query.filter_by(id=project_id).update({
            "project_name": project_name,
            "project_details": project_details
        })

        if not updated_rows:
            return_msg["error_code"] = 1
            return_msg["msg"] = "Project not found"
            return json.dumps(return_msg)

        db.session.commit()

        return_msg["error_code"] = 0
        return_msg["msg"] = "Project updated successfully"
        return json.dumps(return_msg)

    except Exception as e:
        db.session.rollback()
        return_msg["error_code"] = 1
        return_msg["msg"] = "Something went wrong"
        log_writer_.log_exception("manageprojects", "update_project", e)
        return json.dumps(return_msg), 500
    
@bp.route("/delete_project", methods=["POST"])
def delete_project():
    return_msg = {}
    try:
        project_id = request.form.get("id")
        if not project_id:
            return_msg["error_code"] = 1
            return_msg["msg"] = "Project ID is required"
            return json.dumps(return_msg)

        project = Projects.query.get(project_id)
        if not project:
            return_msg["error_code"] = 1
            return_msg["msg"] = "Project not found"
            return json.dumps(return_msg)

        db.session.delete(project)
        db.session.commit()

        return_msg["error_code"] = 0
        return_msg["msg"] = "Project deleted successfully"
        return json.dumps(return_msg)

    except Exception as e:
        db.session.rollback()
        return_msg["error_code"] = 1
        return_msg["msg"] = "Something went wrong"
        log_writer_.log_exception("manageprojects", "delete_project", e)
        return json.dumps(return_msg), 500