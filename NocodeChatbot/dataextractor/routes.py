from flask import Flask, render_template,request,jsonify,session
from NocodeChatbot.extensions import db
from NocodeChatbot.dataextractor import bp
from NocodeChatbot.models.projects import Projects
from NocodeChatbot.models.models import ManageModels
from NocodeChatbot.models.dataextraction import DataExtractor
from NocodeChatbot.utils.logwritter import LogWriter 
from NocodeChatbot.utils.common import get_utc_now
# from NocodeChatbot.utils.login_requried import login_required
log_writer_ = LogWriter()

@bp.route('/')
# @login_required
def index():
    return render_template("dataextractor.html")

@bp.route('/loaddataextractors', methods=['POST','GET'])
def loaddataextractors():
    return_msg = {}
    try:
        customer_id = session["CustomerId"]
        if not customer_id:
            return_msg['msg'] = "Customer not logged in"
            return_msg['error_code'] = 1
            return jsonify(return_msg)

        # Query data extractors only for this customer
        data_extractors = DataExtractor.query.filter_by(customer_id=customer_id).all()
        data_extractor_list = []
        for extractor in data_extractors:
            extractor_info = {
                'id': extractor.id,
                'name': extractor.name,
                'extractiontype': extractor.extractiontype,
                'extractionFile': extractor.extractionFile,
                'extractionUrl': extractor.extractionUrl,
                'created_on': extractor.created_on,
                'status': extractor.status
            }
            data_extractor_list.append(extractor_info)
        return_msg['data_extractor_list'] = data_extractor_list
        return_msg['msg'] = "Data Extractors loaded successfully."
        return_msg['error_code'] = 0

    except Exception as e:
        return_msg['msg'] = "Something went wrong"
        return_msg['error_code'] = 1
        log_writer_.log_exception("dataextractor", "loaddataextractors", e)

    return jsonify(return_msg)

@bp.route('/save_data_extractor', methods=['POST'])
def save_data_extractor():
    return_msg = {}
    try:
        customer_id = session["CustomerId"]

        name = request.form['name']
        extractiontype = request.form['extractiontype']
        extractionFile = request.form['extractionFile']
        extractionUrl = request.form['extractionUrl']

        exsisting_extractor = DataExtractor.query.filter_by(name=name, customer_id=customer_id).first()
        if exsisting_extractor:
            return_msg['msg'] = "Data Extractor with this name already exists."
            return_msg['error_code'] = 1
            return jsonify(return_msg)

        new_extractor = DataExtractor(
            customer_id=customer_id,
            name=name,
            extractiontype=extractiontype,
            extractionFile=extractionFile,
            extractionUrl=extractionUrl,
            created_on=get_utc_now(),
            status="Active"
        )
        db.session.add(new_extractor)
        db.session.commit()

        return_msg['msg'] = "Data Extractor saved successfully."
        return_msg['error_code'] = 0

    except Exception as e:
        return_msg['msg'] = "Something went wrong"
        return_msg['error_code'] = 1
        log_writer_.log_exception("dataextractor", "save_data_extractor", e)

    return jsonify(return_msg)

@bp.route('/update_data_extractor', methods=['POST'])
def update_data_extractor():
    return_msg = {}
    try:
        customer_id = session["CustomerId"]
        if not customer_id:
            return_msg['msg'] = "Customer not logged in"
            return_msg['error_code'] = 1
            return jsonify(return_msg)

        extractor_id = request.form['id']
        name = request.form['name']
        extractiontype = request.form['extractiontype']
        extractionFile = request.form['extractionFile']
        extractionUrl = request.form['extractionUrl']

        extractor = DataExtractor.query.filter_by(id=extractor_id, customer_id=customer_id).first()
        if extractor:
            extractor.name = name
            extractor.extractiontype = extractiontype
            extractor.extractionFile = extractionFile
            extractor.extractionUrl = extractionUrl
            db.session.commit()

            return_msg['msg'] = "Data Extractor updated successfully."
            return_msg['error_code'] = 0
        else:
            return_msg['msg'] = "Data Extractor not found."
            return_msg['error_code'] = 1

    except Exception as e:
        return_msg['msg'] = "Something went wrong"
        return_msg['error_code'] = 1
        log_writer_.log_exception("dataextractor", "update_data_extractor", e)

    return jsonify(return_msg)


@bp.route('/delete_data_extractor', methods=['POST'])
def delete_data_extractor():
    return_msg = {}
    try:
        customer_id = session["CustomerId"]
        if not customer_id:
            return_msg['msg'] = "Customer not logged in"
            return_msg['error_code'] = 1
            return jsonify(return_msg)

        extractor_id = request.form['id']

        extractor = DataExtractor.query.filter_by(id=extractor_id, customer_id=customer_id).first()
        if extractor:
            db.session.delete(extractor)
            db.session.commit()

            return_msg['msg'] = "Data Extractor deleted successfully."
            return_msg['error_code'] = 0
        else:
            return_msg['msg'] = "Data Extractor not found."
            return_msg['error_code'] = 1

    except Exception as e:
        return_msg['msg'] = "Something went wrong"
        return_msg['error_code'] = 1
        log_writer_.log_exception("dataextractor", "delete_data_extractor", e)

    return jsonify(return_msg)