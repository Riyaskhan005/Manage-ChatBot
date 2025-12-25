
from NocodeChatbot.extensions import db

class ManageChatbot(db.Model):
    __tablename__ = 'manage_chatbot'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    project_id = db.Column(db.Text(255), nullable=False)
    customer_id = db.Column(db.Text(255), nullable=False)
    chatbot_color_code = db.Column(db.Text(20), nullable=True)
    chatbot_name = db.Column(db.Text(255), nullable=False)
    chatbot_domain = db.Column(db.Text(255), nullable=False)
    chatbot_model = db.Column(db.Text(255), nullable=False)
    created_by = db.Column(db.Text(255), nullable=False)
    created_on = db.Column(db.Text(255))
    status = db.Column(db.Text(20), nullable=False, default="Active")

    def __repr__(self):
        return f'<ManageChatbot>'

