from NocodeChatbot.extensions import db

class DataExtractor(db.Model):
    __tablename__ = 'data_extractors'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    customer_id = db.Column(db.Text(255), nullable=False)
    name = db.Column(db.Text(255), nullable=False)
    extractiontype = db.Column(db.Text(255), nullable=False)
    extractionFile = db.Column(db.Text(255), nullable=False)
    extractionUrl = db.Column(db.Text(255), nullable=False)
    created_on = db.Column(db.Text(255))
    status = db.Column(db.Text(20), nullable=False, default="Active")

    def __repr__(self):
        return f'<DataExtractor>'