import os,re,shutil
from flask import Flask, render_template, request, jsonify, session, current_app
from bs4 import BeautifulSoup
import requests
from docx import Document
import PyPDF2
from NocodeChatbot.extensions import db
from NocodeChatbot.dataextractor import bp
from NocodeChatbot.models.projects import Projects
from NocodeChatbot.models.models import ManageModels
from NocodeChatbot.models.dataextraction import DataExtractor
from NocodeChatbot.utils.logwritter import LogWriter 
from NocodeChatbot.utils.common import get_utc_now

log_writer_ = LogWriter()

ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'txt'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_text_from_file(filepath):
    ext = filepath.rsplit('.', 1)[1].lower()
    text = ""
    try:
        if ext == "txt":
            with open(filepath, 'r', encoding='utf-8') as f:
                text = f.read()
        elif ext in ["doc", "docx"]:
            doc = Document(filepath)
            text = "\n".join([p.text for p in doc.paragraphs])
        elif ext == "pdf":
            with open(filepath, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                text = "\n".join([page.extract_text() or "" for page in reader.pages])
    except Exception as e:
        log_writer_.log_exception("dataextractor", "extract_text_from_file", e)
    return text

import re

def clean_extracted_text(raw_text):
    """
    Cleans messy extracted text:
    - Removes line breaks inside paragraphs
    - Reduces multiple spaces/tabs to a single space
    - Preserves paragraph breaks (double newline between paragraphs)
    """
    raw_text = raw_text.replace('\r\n', '\n').replace('\r', '\n')

    paragraphs = re.split(r'\n{2,}', raw_text)
    cleaned_paragraphs = []

    for para in paragraphs:
        cleaned_para = re.sub(r'\s+', ' ', para).strip()
        if cleaned_para:
            cleaned_paragraphs.append(cleaned_para)

    return "\n\n".join(cleaned_paragraphs)


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
        extractionFile = request.files.get('extractionFile')
        extractionUrl = request.form.get('extractionUrl')
        db_file_path = ""
        if not name:
            return_msg['msg'] = "Extraction name is required."
            return_msg['error_code'] = 1
            return jsonify(return_msg)

        if extractiontype not in ["document", "website"]:
            return_msg['msg'] = "Extraction type must be selected."
            return_msg['error_code'] = 1
            return jsonify(return_msg)
        
        existing_extractor = DataExtractor.query.filter_by(name=name, customer_id=customer_id).first()
        if existing_extractor:
            return_msg['msg'] = "Data Extractor with this name already exists."
            return_msg['error_code'] = 1
            return jsonify(return_msg)

        extracted_text = ""
        filename = None
        original_file_path = None

        new_extractor = DataExtractor(
            customer_id=customer_id,
            name=name,
            extractiontype=extractiontype,
            extractionFile='',
            extractionUrl='',
            created_on=get_utc_now(),
            status="Active"
        )
        db.session.add(new_extractor)
        db.session.commit()

        if extractiontype.lower() == "website" and extractionUrl:
            try:
                response = requests.get(extractionUrl)
                response.raise_for_status()
                soup = BeautifulSoup(response.content, "html.parser")
                elements = soup.find_all(['p','h1','h2','h3','h4','h5','h6','li'])
                raw_text = "\n\n".join(el.get_text() for el in elements if el.get_text().strip())
                extracted_text = clean_extracted_text(raw_text)

                if not extracted_text:
                    return_msg['msg'] = "No text could be extracted from the website."
                    return_msg['error_code'] = 1
                    return jsonify(return_msg)

                new_extractor.extractionUrl = extractionUrl
            except Exception:
                return_msg['msg'] = "Failed to fetch or parse the website."
                return_msg['error_code'] = 1
                return jsonify(return_msg)
        elif extractiontype.lower() == "document":
            if not extractionFile or extractionFile.filename == "":
                return_msg['msg'] = "Document file is required for document extraction."
                return_msg['error_code'] = 1
                return jsonify(return_msg)
            filename = extractionFile.filename

            if not allowed_file(filename):
                return_msg['msg'] = "File type not supported."
                return_msg['error_code'] = 1
                return jsonify(return_msg)
            original_dir = os.path.join(current_app.root_path, "static", "original_file", f"{customer_id}_{new_extractor.id}")
            os.makedirs(original_dir, exist_ok=True)
            original_file_path = os.path.join(original_dir, filename)
            extractionFile.save(original_file_path)
            db_file_path = f"static/original_file/{customer_id}_{new_extractor.id}/{filename}"
            new_extractor.extractionFile = db_file_path
            raw_text = extract_text_from_file(original_file_path)
            extracted_text = clean_extracted_text(raw_text)

            if not extracted_text:
                return_msg['msg'] = "The uploaded document is empty or could not be read."
                return_msg['error_code'] = 1
                return jsonify(return_msg)
        text_dir = os.path.join(current_app.root_path, "static", "dataextractor", f"{customer_id}_{new_extractor.id}")
        os.makedirs(text_dir, exist_ok=True)

        text_file_path = os.path.join(text_dir, f"{name}.txt")
        with open(text_file_path, "w", encoding='utf-8') as f:
            f.write(extracted_text)

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
        customer_id = session.get("CustomerId")
        if not customer_id:
            return_msg['msg'] = "Customer not logged in"
            return_msg['error_code'] = 1
            return jsonify(return_msg)
        extractor_id = request.form.get('id')
        name = request.form.get('name')
        extractiontype = request.form.get('extractiontype')
        extractionFile = request.files.get('extractionFile')
        extractionUrl = request.form.get('extractionUrl')
        db_file_path = ""

        if not extractor_id:
            return_msg['msg'] = "Extractor ID is required."
            return_msg['error_code'] = 1
            return jsonify(return_msg)
        if not name:
            return_msg['msg'] = "Extraction name is required."
            return_msg['error_code'] = 1
            return jsonify(return_msg)
        extractor = DataExtractor.query.filter_by(id=extractor_id, customer_id=customer_id).first()
        if not extractor:
            return_msg['msg'] = "Data Extractor not found."
            return_msg['error_code'] = 1
            return jsonify(return_msg)

        extracted_text = ""
        filename = None 
        if extractiontype.lower() == "website" and extractionUrl:
            if not extractionUrl or not re.match(r'^(https?:\/\/)', extractionUrl, re.I):
                return_msg['msg'] = "Valid URL is required for website extraction."
                return_msg['error_code'] = 1
                return jsonify(return_msg)
            try:
                response = requests.get(extractionUrl)
                response.raise_for_status()
                soup = BeautifulSoup(response.content, "html.parser")
                elements = soup.find_all(['p','h1','h2','h3','h4','h5','h6','li'])
                raw_text = "\n\n".join(el.get_text() for el in elements if el.get_text().strip())
                extracted_text = clean_extracted_text(raw_text)

                if not extracted_text:
                    return_msg['msg'] = "No text could be extracted from the website."
                    return_msg['error_code'] = 1
                    return jsonify(return_msg)

            except Exception:
                return_msg['msg'] = "Failed to fetch or parse the website."
                return_msg['error_code'] = 1
                return jsonify(return_msg)
            if extractor.extractionFile:
                old_file_path = os.path.join(current_app.root_path, extractor.extractionFile)
                if os.path.exists(old_file_path):
                    os.remove(old_file_path)

            extractor.extractionUrl = extractionUrl
            extractor.extractionFile = ""

        elif extractiontype.lower() == "document" and extractionFile:
            if not extractionFile or extractionFile.filename == "":
                return_msg['msg'] = "Document file is required for document extraction."
                return_msg['error_code'] = 1
                return jsonify(return_msg)

            filename = extractionFile.filename

            if not allowed_file(filename):
                return_msg['msg'] = "File type not supported."
                return_msg['error_code'] = 1
                return jsonify(return_msg)

            if extractor.extractionFile:
                old_file_path = os.path.join(current_app.root_path, extractor.extractionFile)
                if os.path.exists(old_file_path):
                    os.remove(old_file_path)

            original_dir = os.path.join(current_app.root_path, "static", "original_file", f"{customer_id}_{extractor.id}")
            os.makedirs(original_dir, exist_ok=True)
            original_file_path = os.path.join(original_dir, filename)
            extractionFile.save(original_file_path)
            db_file_path = f"static/original_file/{customer_id}_{extractor.id}/{filename}"
            extractor.extractionFile = db_file_path
            extractor.extractionUrl = ""

            raw_text = extract_text_from_file(original_file_path)
            extracted_text = clean_extracted_text(raw_text)

            if not extracted_text:
                return_msg['msg'] = "The uploaded document is empty or could not be read."
                return_msg['error_code'] = 1
                return jsonify(return_msg)

        extractor.name = name
        extractor.extractiontype = extractiontype
        db.session.commit()

        text_dir = os.path.join(current_app.root_path, "static", "dataextractor", f"{customer_id}_{extractor.id}")
        os.makedirs(text_dir, exist_ok=True)
        text_file_path = os.path.join(text_dir, f"{name}.txt")
        with open(text_file_path, "w", encoding="utf-8") as f:
            f.write(extracted_text)

        return_msg['msg'] = "Data Extractor updated successfully."
        return_msg['error_code'] = 0

    except Exception as e:
        log_writer_.log_exception("dataextractor", "update_data_extractor", e)
        return_msg['msg'] = "Something went wrong."
        return_msg['error_code'] = 1

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

        extractor = DataExtractor.query.filter_by(
            id=extractor_id,
            customer_id=customer_id
        ).first()

        if not extractor:
            return_msg['msg'] = "Data Extractor not found."
            return_msg['error_code'] = 1
            return jsonify(return_msg)

        extractor_folder = os.path.join(
            current_app.root_path,
            "static",
            "dataextractor",
            f"{customer_id}_{extractor.id}"
        )
        if os.path.exists(extractor_folder):
            shutil.rmtree(extractor_folder)

        if extractor.extractiontype.lower() == "document" and extractor.extractionFile:
            original_file_path = os.path.join(
                current_app.root_path,
                "static",
                "original_file",
                f"{customer_id}_{extractor.id}",
                os.path.basename(extractor.extractionFile)
            )
            if os.path.exists(original_file_path):
                os.remove(original_file_path)

            original_dir = os.path.join(
                current_app.root_path,
                "static",
                "original_file",
                f"{customer_id}_{extractor.id}"
            )
            if os.path.exists(original_dir) and not os.listdir(original_dir):
                os.rmdir(original_dir)
        db.session.delete(extractor)
        db.session.commit()

        return_msg['msg'] = "Data Extractor deleted successfully."
        return_msg['error_code'] = 0

    except Exception as e:
        return_msg['msg'] = "Something went wrong"
        return_msg['error_code'] = 1
        log_writer_.log_exception("dataextractor", "delete_data_extractor", e)

    return jsonify(return_msg)