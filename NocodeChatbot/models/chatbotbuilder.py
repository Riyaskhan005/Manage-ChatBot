
from NocodeChatbot.extensions import db

class ChatbotBuilder(db.Model):
    __tablename__ = 'chatbot_builder'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    project_id = db.Column(db.Text(255), nullable=False)
    customer_id = db.Column(db.Text(255), nullable=False)
    builder_flow_json = db.Column(db.Text, nullable=False)
    created_by = db.Column(db.Text(255), nullable=False)
    created_on = db.Column(db.Text(255))
    status = db.Column(db.Text(20), nullable=False, default="Active")

    def __repr__(self):
        return f'<ChatbotBuilder>'

