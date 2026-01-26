import ncapp as _app
from config import Config
import os

application = _app.create_app(Config)
application.secret_key = Config.SECRET_KEY

root_path = os.path.dirname(os.path.abspath(__file__))

if __name__ == "__main__":
    application.run(port=5555,debug=True)