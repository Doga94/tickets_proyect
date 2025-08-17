from app.extensions import db
from flask_login import UserMixin

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(15), nullable=False)
    role = db.Column(db.String(10), nullable=False, default='user')

    tickets = db.relationship('Ticket', backref='author', lazy=True)
    reponses = db.relationship('Response', backref='agent', lazy=True)