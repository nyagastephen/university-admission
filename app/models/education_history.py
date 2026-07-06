from app.extensions import db


class EducationHistory(db.Model):
    __tablename__ = "education_histories"

    id = db.Column(db.Integer, primary_key=True)

    applicant_profile_id = db.Column(
        db.Integer,
        db.ForeignKey("applicant_profiles.id"),
        nullable=False,
        unique=True
    )

    school_name = db.Column(
        db.String(200),
        nullable=False
    )

    index_number = db.Column(
        db.String(30),
        nullable=False,
        unique=True
    )

    exam_year = db.Column(
        db.Integer,
        nullable=False
    )

    mean_grade = db.Column(
        db.String(5),
        nullable=False
    )

    certificate_number = db.Column(
        db.String(50)
    )

    created_at = db.Column(
        db.DateTime,
        server_default=db.func.now()
    )

    updated_at = db.Column(
        db.DateTime,
        server_default=db.func.now(),
        onupdate=db.func.now()
    )

    applicant = db.relationship(
    "ApplicantProfile",
    back_populates="education"
    )