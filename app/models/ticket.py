from app.extensions import db
from datetime import datetime

class Ticket(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=False)
    is_urgent = db.Column(db.Boolean, default=False)
    status = db.Column(db.String(20), nullable=False, default='open') #Debera salir open | in_progress | resolved
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    responses = db.relationship('Response', backref='ticket', lazy=True, cascade='all, delete-orphan')
