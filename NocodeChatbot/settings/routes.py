from flask import Flask, redirect, render_template,request,jsonify,session
from NocodeChatbot.extensions import db
from NocodeChatbot.settings import bp
from NocodeChatbot.models.Customer import Customers
import json,os
from NocodeChatbot.utils import common
from NocodeChatbot.utils.logwritter import LogWriter
from NocodeChatbot.utils.common import decrypt_data,encrypt_data
log_writer_ = LogWriter()


@bp.route('/')
def index():
    return render_template("settings.html")


@bp.route('/getProfileDetails', methods=['GET'])
def getProfileDetails():
    return_msg = {}
    try:
        if 'CustomerId' in session or session['CustomerId']:
            customer_id = session['CustomerId']
        else:
            return_msg ["error_code"] = 3
            return_msg ["msg"] = "User not logged in"
            return jsonify(return_msg)

        customer = db.session.query(Customers).filter_by(id=customer_id).first()
        if customer:
            return_msg ["error_code"] = 0
            return_msg ["firstname"] = customer.First_name
            return_msg ["lastname"] = customer.Last_name
            return_msg ["email"] = customer.Email
            return_msg ["contact"] = customer.Contact
            return_msg ["company_name"] = customer.Company_Name
            return_msg ["notes"] = customer.Notes
        else:
            return_msg ["error_code"] = 1
            return_msg ["msg"] = "Customer not found"
    except Exception as e:
        log_writer_.log_exception("getProfileDetails", "get_profile", e)
        return_msg ["error_code"] = 2
        return_msg ["msg"] = "Something went wrong"
    return jsonify(return_msg)

@bp.route('/ProfileDetailsUpdate', methods=['POST'])
def ProfileDetailsUpdate():
    return_msg = {}
    try:
        if 'CustomerId' not in session or not session['CustomerId']:
            return_msg ["error_code"] = 3
            return_msg ["msg"] = "User not logged in"
            return jsonify(return_msg)
        customer_id = session['CustomerId']
        firstnameInput = request.form.get('firstnameInput')
        lastnameInput = request.form.get('lastnameInput')
        emailInput = request.form.get('emailInput')
        phonenumberInput = request.form.get('phonenumberInput')
        Company_Name = request.form.get('Company_Name')
        Notes = request.form.get('Notes')

        customer = db.session.query(Customers).filter_by(id=customer_id).first()
        if customer:
            customer.First_name = firstnameInput
            customer.Last_name = lastnameInput
            customer.Email = emailInput
            customer.Contact = phonenumberInput
            customer.Company_Name = Company_Name
            customer.Notes = Notes
            session['first_Name'] = customer.First_name 
            session['last_Name'] = customer.Last_name
            session['email'] = customer.Email
            db.session.commit()
            return_msg ["error_code"] = 0
            return_msg ["msg"] = "Profile updated successfully"
        else:
            return_msg ["error_code"] = 1
            return_msg ["msg"] = "Customer not found"
    except Exception as e:
        log_writer_.log_exception("ProfileDetailsUpdate", "update_profile", e)
        return_msg ["error_code"] = 2
        return_msg ["msg"] = "Something went wrong"
    return jsonify(return_msg)

@bp.route('/ChangePassword', methods=['POST'])
def ChangePassword():
    return_msg = {}
    try:
        if 'CustomerId' in session or session['CustomerId']:
            customer_id = session['CustomerId']
        else:
            return_msg ["error_code"] = 3
            return_msg ["msg"] = "User not logged in"
            return jsonify(return_msg)
        currentPassword = request.form.get('oldpasswordInput')
        newPassword = request.form.get('newpasswordInput')

        customer = db.session.query(Customers).filter_by(id=customer_id).first()
        if customer:
            decrypted_password = decrypt_data(customer.Password)
            if decrypted_password == currentPassword:
                encrypted_new_password = encrypt_data(newPassword)
                customer.Password = encrypted_new_password
                db.session.commit()
                return_msg ["error_code"] = 0
                return_msg ["msg"] = "Password changed successfully"
            else:
                return_msg ["error_code"] = 1
                return_msg ["msg"] = "Old password is incorrect"
        else:
            return_msg ["error_code"] = 2
            return_msg ["msg"] = "Customer not found"
    except Exception as e:
        log_writer_.log_exception("ChangePassword", "change_password", e)
        return_msg ["error_code"] = 3
        return_msg ["msg"] = "Something went wrong"
    return jsonify(return_msg)

@bp.route('/ChangeProfile', methods=['POST'])
def UpdateProfileImage():
    return_msg = {}
    try:
        if 'CustomerId' not in session or not session['CustomerId']:
            return_msg ["error_code"] = 3
            return_msg ["msg"] = "User not logged in"
            return jsonify(return_msg)

        customer_id = session['CustomerId']

        if 'profileImage' not in request.files:
            return_msg["error_code"] = 1
            return_msg["msg"] = "No file part"
            return jsonify(return_msg)
        
        file = request.files['profileImage']
        if file.filename == '':
            return_msg["error_code"] = 2
            return_msg["msg"] = "No selected file"

        customer = db.session.query(Customers).filter_by(id=customer_id).first()
        if not customer:
            return_msg["error_code"] = 4
            return_msg["msg"] = "Customer not found"

        filename = f"profile_{customer.id}_{file.filename}"
        upload_dir = os.path.join(os.path.dirname(__file__), '..', 'static', 'profile_images')
        upload_dir = os.path.abspath(upload_dir)
        os.makedirs(upload_dir, exist_ok=True)

        filename = f"profile_{customer.id}_{file.filename}"
        filepath = os.path.join(upload_dir, filename)
        file.save(filepath)

        customer.ProfilePath = f"profile_images/{filename}"
        db.session.commit()
        session['Profilepath'] = customer.ProfilePath
        return_msg["error_code"] = 0
        return_msg["msg"] = "Profile image updated successfully"

        
    except Exception as e:
        log_writer_.log_exception("UpdateProfileImage", "update_profile_image", e)
        return_msg["error_code"] = 5
        return_msg["msg"] = "Something went wrong" 
    return jsonify(return_msg)
