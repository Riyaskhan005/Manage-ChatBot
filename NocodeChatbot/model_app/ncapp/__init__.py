from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from config import Config

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    app.config['SECRET_KEY'] = config_class.SECRET_KEY

    CORS(app)
    JWTManager(app)

    from ncapp.chatbot import bp as chatbot_bp
    app.register_blueprint(chatbot_bp, url_prefix='/')

    return app
