from flask import Flask, render_template
from .extensions import db, login_manager

from .models.user import User
from .models.ticket import Ticket
from .models.response import Response

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
    
def create_app():
    app = Flask(__name__)
    app.config.from_pyfile('../config.py')

    db.init_app(app)
    login_manager.init_app(app)

    from .routes import main
    app.register_blueprint(main)

    return app