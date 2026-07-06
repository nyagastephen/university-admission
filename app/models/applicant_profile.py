from app.extensions import db

class ApplicantProfile(db.Model):
    __tablename__ = "applicant_profiles"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        unique=True,
        nullable=False
    )

    first_name = db.Column(db.String(100), nullable=False)

    middle_name = db.Column(db.String(100))

    last_name = db.Column(db.String(100), nullable=False)

    gender = db.Column(db.String(10))

    date_of_birth = db.Column(db.Date)

    national_id = db.Column(db.String(30), unique=True)

    phone = db.Column(db.String(20))

    county = db.Column(db.String(100))

    postal_address = db.Column(db.String(150))

    city = db.Column(db.String(100))

    nationality = db.Column(db.String(100))

    created_at = db.Column(
        db.DateTime,
        server_default=db.func.now()
    )

    user = db.relationship(
        "User",
        back_populates="profile"
    )
    education = db.relationship(
    "EducationHistory",
    back_populates="applicant",
    uselist=False,
    cascade="all, delete-orphan"
    )

    documents = db.relationship(
    "UploadedDocument",
    back_populates="applicant",
    cascade="all, delete-orphan"
    )

    application = db.relationship(
    "Application",
    back_populates="applicant",
    uselist=False,
    cascade="all, delete-orphan"
    )
