from flask import Blueprint

admin = Blueprint('admin', __name__)
student = Blueprint('student', __name__)
auth = Blueprint('auth', __name__)

from routes.admin import *
from routes.student import *
from routes.auth import *

def init_routes(app):
    # Register blueprints
    app.register_blueprint(auth)
    app.register_blueprint(admin, url_prefix='/admin')
    app.register_blueprint(student, url_prefix='/student')
