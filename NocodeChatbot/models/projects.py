from NocodeChatbot.extensions import db

class Projects(db.Model):
    __tablename__ = 'projects'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    customer_id = db.Column(db.Text(255), nullable=False)
    project_name = db.Column(db.Text(255), nullable=False)
    project_details = db.Column(db.Text(255), nullable=False)
    created_by = db.Column(db.Text(255), nullable=False)
    created_on = db.Column(db.Text(255))
    status = db.Column(db.String(20), nullable=False, default="Active")


    def __repr__(self):
        return f'<Projects>'