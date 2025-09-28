from NocodeChatbot.extensions import db

class Customers(db.Model):
    __tablename__ = 'customers'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    First_name = db.Column(db.Text(255), nullable=False)
    Last_name = db.Column(db.Text(255), nullable=False)
    Email = db.Column(db.Text(255), nullable=False)
    Password = db.Column(db.Text(255), nullable=False)
    Contact = db.Column(db.Text(255), nullable=False)
    Company_Name = db.Column(db.Text(255), nullable=False)
    Notes = db.Column(db.Text(255), nullable=False)
    ProfilePath = db.Column(db.Text(255), nullable=False)
    created_on = db.Column(db.Text(255))
    status = db.Column(db.Text(20), nullable=False, default="Active")

    def __repr__(self):
        return f'<Customers>'