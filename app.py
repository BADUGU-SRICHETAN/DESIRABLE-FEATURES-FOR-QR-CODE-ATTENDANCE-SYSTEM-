import os
import logging

from flask import Flask, render_template
from werkzeug.middleware.proxy_fix import ProxyFix
from extensions import db, login_manager, jwt


# Configure logging
logging.basicConfig(level=logging.DEBUG)


def create_app():
    # create the app
    app = Flask(__name__)
    app.secret_key = os.environ.get("SESSION_SECRET", "development_secret_key")
    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)  # needed for url_for to generate with https

    # Initialize login manager
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'  # Specify the login view with blueprint prefix

    # Configure database
    database_url = os.environ.get("DATABASE_URL")
    # Use a default SQLite database if DATABASE_URL is not set
    if not database_url:
        database_url = "sqlite:///attendance.db"
        print("Warning: DATABASE_URL not set, using SQLite database")
    # Ensure compatibility with PostgreSQL - replace postgres:// with postgresql://
    elif database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)

    app.config["SQLALCHEMY_DATABASE_URI"] = database_url
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_recycle": 300,
        "pool_pre_ping": True,
    }
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # Configure JWT
    app.config["JWT_SECRET_KEY"] = os.environ.get("JWT_SECRET_KEY", "jwt_secret_development_key")
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = 3600  # 1 hour
    
    # Initialize extensions
    db.init_app(app)
    jwt.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        from models import User
        return User.query.get(int(user_id))

    with app.app_context():
        # Import models to create tables
        import models  # noqa: F401
        
        # Drop all tables and recreate them
        db.drop_all()
        db.create_all()
        
        # Import and register blueprints
        from routes.auth import auth
        from routes.admin import admin
        from routes.student import student

        app.register_blueprint(auth)  # No prefix for auth routes
        app.register_blueprint(admin, url_prefix='/admin')
        app.register_blueprint(student, url_prefix='/student')

        # Register error handlers
        @app.errorhandler(404)
        def not_found_error(error):
            return render_template('errors/404.html'), 404

        @app.errorhandler(500)
        def internal_error(error):
            db.session.rollback()
            return render_template('errors/500.html'), 500

    return app

app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
