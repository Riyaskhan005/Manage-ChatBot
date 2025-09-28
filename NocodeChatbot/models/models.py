
from NocodeChatbot.extensions import db

class ManageModels(db.Model):
    __tablename__ = 'manage_models'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    project_id = db.Column(db.Text(255), nullable=False)
    customer_id = db.Column(db.Text(255), nullable=False)
    model_name = db.Column(db.Text, nullable=False)
    model_key = db.Column(db.Text, nullable=False)
    model_secret = db.Column(db.Text, nullable=False)
    model_version = db.Column(db.Text, nullable=False)
    created_by = db.Column(db.Text(255), nullable=False)
    created_on = db.Column(db.Text(255))
    status = db.Column(db.Text(20), nullable=False, default="Active")

    def __repr__(self):
        return f'<ManageModels>'