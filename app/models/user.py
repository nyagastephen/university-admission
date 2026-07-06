from app.extensions import db
from flask_login import UserMixin

class User(UserMixin,db.Model):

    __tablename__="users"

    id=db.Column(db.Integer,primary_key=True)

    username=db.Column(db.String(100),unique=True,nullable=False)

    email=db.Column(db.String(120),unique=True,nullable=False)

    password=db.Column(db.String(255),nullable=False)

    role=db.Column(db.String(50),default="Applicant")

    profile = db.relationship(
    "ApplicantProfile",
    back_populates="user",
    uselist=False
    )