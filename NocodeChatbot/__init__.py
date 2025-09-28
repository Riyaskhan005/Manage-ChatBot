from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from config import Config
from NocodeChatbot.extensions import db

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    app.config['SECRET_KEY'] = config_class.SECRET_KEY

    db.init_app(app)
    CORS(app)
    JWTManager(app)

    # Register blueprints
    

    from NocodeChatbot.dashboard import bp as dashboard_bp
    app.register_blueprint(dashboard_bp, url_prefix='/home')

    from NocodeChatbot.manageprojects import bp as projects_bp
    app.register_blueprint(projects_bp, url_prefix='/projects')

    from NocodeChatbot.managechatbot import bp as managechatbot_bp
    app.register_blueprint(managechatbot_bp, url_prefix='/chatbot')

    return app
