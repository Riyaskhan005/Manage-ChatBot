from flask import Flask, redirect, render_template,request,jsonify,session
from NocodeChatbot.extensions import db
from NocodeChatbot.authentication import bp
from NocodeChatbot.models.Customer import Customers
import json
from NocodeChatbot.utils import common
from NocodeChatbot.utils.logwritter import LogWriter
log_writer_ = LogWriter()


@bp.route('/')
def index():
    return render_template("login.html")

@bp.route('/login', methods=['POST'])
def login():
    return_msg = {}
    try:
        email = request.form.get('email')
        password = request.form.get('password')

        customer = Customers.query.filter_by(Email=email, status='Active').first()
        if not customer:
            return_msg["error_code"] = 2
            return_msg["msg"] = "Invalid email or password"
            return json.dumps(return_msg)

        decrypted_password = common.decrypt_data(customer.Password)
        if decrypted_password != password:
            return_msg["error_code"] = 1
            return_msg["msg"] = "Invalid email or password"
            return json.dumps(return_msg)

        session['email'] = customer.Email
        session['CustomerId'] = customer.id

        return_msg["error_code"] = 0
        return_msg["msg"] = "Login successful"
        return json.dumps(return_msg)

    except Exception as e:
        return_msg["error_code"] = 99
        return_msg["msg"] = f"Unexpected error: {str(e)}"
        log_writer_.log_exception("authentication", "login", e)
        return json.dumps(return_msg)
    
    
@bp.route('/logout')
def logout():
    try:
        session['email'] = ""
        session['CustomerId'] = ""
        session.clear()  
        return redirect('/')
    except Exception as e:
        log_writer_.log_exception("authentication", "logout", e)
        return redirect('/')