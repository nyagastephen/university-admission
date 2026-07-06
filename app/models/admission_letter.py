from app.extensions import db


class AdmissionLetter(db.Model):
    __tablename__ = "admission_letters"

    id = db.Column(db.Integer, primary_key=True)

    application_id = db.Column(
        db.Integer,
        db.ForeignKey("applications.id"),
        nullable=False,
        unique=True
    )

    letter_number = db.Column(
        db.String(50),
        unique=True,
        nullable=False
    )

    file_name = db.Column(
        db.String(255),
        nullable=False
    )

    generated_by = db.Column(
        db.Integer,
        db.ForeignKey("users.id")
    )

    generated_at = db.Column(
        db.DateTime,
        server_default=db.func.now()
    )

    application = db.relationship(
    "Application",
    backref=db.backref(
        "admission_letter",
        uselist=False
    )
    )