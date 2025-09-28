from flask import Flask, render_template,request,jsonify
from NocodeChatbot.extensions import db
from NocodeChatbot.manageprojects import bp
from NocodeChatbot.models.projects import Projects
import json
from NocodeChatbot.utils.common import get_utc_now
# from NocodeChatbot.utils.logwritter import LogWriter 
# from NocodeChatbot.utils.login_requried import login_required
# logger = LogWriter()


@bp.route('/')
# @login_required
def index():
    return render_template("projects.html")


@bp.route("/save_project", methods=["POST"])
def save_project():
    return_msg = {}
    try:
        project_name = request.form.get("project_name")
        project_details = request.form.get("project_details")

        project = Projects(
            customer_id="123",
            project_name=project_name,
            project_details=project_details,
            created_by="m.driyaskhan55@gmail.com",
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
        return_msg["msg"] = f"Error saving project: {str(e)}"
        return json.dumps(return_msg), 500