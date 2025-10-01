from flask import Flask, render_template,request,jsonify,session
from NocodeChatbot.extensions import db
from NocodeChatbot.common import bp
from NocodeChatbot.models.projects import Projects
from NocodeChatbot.utils.logwritter import LogWriter 
# from NocodeChatbot.utils.login_requried import login_required
log_writer_ = LogWriter()


@bp.route('/getprojects', methods=['GET'])
def getprojects():
    return_msg = {}
    try:
        customer_id = session.get("CustomerId")
        if not customer_id:
            return_msg["error_code"] = 1
            return_msg["msg"] = "Session expired. Please login again."
            return jsonify(return_msg)

        projects = Projects.query.filter_by(customer_id=customer_id, status="Active").all()
        project_list = []
        for p in projects:
            project_data = {
                "id": p.id,
                "name": p.project_name
            }
            project_list.append(project_data)

        return_msg["error_code"] = 0
        return_msg["projects"] = project_list
        return jsonify(return_msg)

    except Exception as e:
        return_msg["error_code"] = 99
        return_msg["msg"] = f"Unexpected error: {str(e)}"
        log_writer_.log_exception("projects", "getprojects", e)
        return jsonify(return_msg)
