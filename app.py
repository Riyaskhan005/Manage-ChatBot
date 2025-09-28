import NocodeChatbot as _app
from config import Config
from NocodeChatbot.extensions import db
import os

application = _app.create_app(Config)
application.secret_key = Config.SECRET_KEY

root_path = os.path.dirname(os.path.abspath(__file__))

if __name__ == "__main__":
    with application.app_context():
        db.create_all()
    application.run(debug=True)