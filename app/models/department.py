from app.extensions import db


class Department(db.Model):
    __tablename__ = "departments"

    id = db.Column(db.Integer, primary_key=True)

    code = db.Column(db.String(20), unique=True, nullable=False)

    name = db.Column(db.String(150), unique=True, nullable=False)

    description = db.Column(db.Text)

    is_active = db.Column(db.Boolean, default=True)

    created_at = db.Column(db.DateTime, server_default=db.func.now())

    def __repr__(self):
        return f"<Department {self.code}>"
    courses = db.relationship(
    "Course",
    back_populates="department",
    lazy=True
        )