from flask import Flask
from config import Config
from app.models import User
from app.extensions import db
from app.extensions import migrate
from app.extensions import login_manager
from app.routes.main import main
from app.routes.auth import auth
from app.routes.admin import admin
from app.routes.department import department
from app.routes.course import course
from app.routes.applicant import applicant
from app.routes.education import education
from app.routes.document import document
from app.routes.application import application_bp
from app.routes.admissions import admissions
def create_app():

    app=Flask(__name__)
    app.config["SECRET_KEY"] = "your_secret_key_here"
    app.config.from_object(Config)

    db.init_app(app)

    migrate.init_app(app,db)

    login_manager.init_app(app)

    app.register_blueprint(main)

    app.register_blueprint(auth)

    app.register_blueprint(admin)

    app.register_blueprint(department)

    app.register_blueprint(course)

    app.register_blueprint(applicant)
    
    app.register_blueprint(education)

    app.register_blueprint(document)

    app.register_blueprint(application_bp)
    
    app.register_blueprint(admissions)
    return app
