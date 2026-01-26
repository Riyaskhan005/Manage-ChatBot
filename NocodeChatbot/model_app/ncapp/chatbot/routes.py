from flask import request, jsonify, render_template, session
from ncapp.chatbot import bp
from ncapp.chatbot.chatbot_logic import load_rag_text, build_prompt, API_KEY, MODEL_NAME
from ncapp.ncutils.logwritter import LogWriter
# REPLACE IMPORT
import os

log_writer_ = LogWriter()

@bp.route('/')
def index():
    # Initialize conversation in session
    if 'conversation' not in session:
        session['conversation'] = []
    return render_template("chat.html")


@bp.route('/chat', methods=['POST'])
def chat():
    return_msg = {}
    try:

        data = request.get_json()
        conversation = data.get("conversation", [])
        

        if not conversation or not API_KEY:
            return jsonify({'msg': "message and model_key are required", 'error_code': 1})

        # Build conversation text for prompt
        conversation_text = ""
        for msg in conversation:
            conversation_text += f"{msg['role'].capitalize()}: {msg['text']}\n"

        # Optional RAG text
        rag_text = load_rag_text()
        final_prompt = build_prompt(user_message=conversation[-1]['text'], rag_text=rag_text,conversation_text=conversation_text, chatbot_name="Demo Chatbot",chatbot_domain="General")
        bot_reply = "Hi there! This is a Dummy Response from the Chatbot."

        # REPLACE API CALL

        return_msg['msg'] = bot_reply
        return_msg['error_code'] = 0

    except Exception as e:
        return_msg['msg'] = "Something went wrong"
        return_msg['error_code'] = 1
        log_writer_.log_exception("chatbot", "chat", e)

    return jsonify(return_msg)