from app.extensions import db


class UploadedDocument(db.Model):
    __tablename__ = "uploaded_documents"

    id = db.Column(db.Integer, primary_key=True)

    applicant_profile_id = db.Column(
        db.Integer,
        db.ForeignKey("applicant_profiles.id"),
        nullable=False
    )

    document_type = db.Column(
        db.String(50),
        nullable=False
    )

    original_filename = db.Column(
        db.String(255),
        nullable=False
    )

    stored_filename = db.Column(
        db.String(255),
        nullable=False
    )

    verified = db.Column(
        db.Boolean,
        default=False
    )

    uploaded_at = db.Column(
        db.DateTime,
        server_default=db.func.now()
    )

    applicant = db.relationship(
        "ApplicantProfile",
        back_populates="documents"
    )

    verification_status = db.Column(
        db.String(20),
        default="Pending"
    )

    verification_comment = db.Column(
        db.Text,
        nullable=True
    )

    verified_by = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=True
    )

    verified_at = db.Column(
        db.DateTime,
        nullable=True
    )