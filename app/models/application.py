from app.extensions import db
class Application(db.Model):
    __tablename__ = "applications"

    id = db.Column(db.Integer, primary_key=True)

    applicant_profile_id = db.Column(
        db.Integer,
        db.ForeignKey("applicant_profiles.id"),
        nullable=False,
        unique=True
    )

    department_id = db.Column(
        db.Integer,
        db.ForeignKey("departments.id"),
        nullable=False
    )

    course_id = db.Column(
        db.Integer,
        db.ForeignKey("courses.id"),
        nullable=False
    )

    status = db.Column(
        db.String(20),
        nullable=False,
        default="Draft"
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
        back_populates="application"
    )

    department = db.relationship("Department")

    course = db.relationship("Course")

    @property
    def application_number(self):
        year = self.created_at.year if self.created_at else "0000"
        return f"APP-{year}-{self.id:06d}"
    submitted_at = db.Column(
    db.DateTime,
    server_default=db.func.now()
    )
    review_notes = db.Column(
    db.Text,
    nullable=True
    )

    reviewed_by = db.Column(
    db.Integer,
    db.ForeignKey("users.id"),
    nullable=True
    )

    reviewed_at = db.Column(
    db.DateTime,
    nullable=True
    )
    logs = db.relationship(
    "ApplicationLog",
    backref="application",
    lazy=True,
    cascade="all, delete-orphan"
    )

   