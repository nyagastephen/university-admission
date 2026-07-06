from app.extensions import db
class Course(db.Model):
    __tablename__ = "courses"

    id = db.Column(db.Integer, primary_key=True)

    code = db.Column(db.String(20), unique=True, nullable=False)

    name = db.Column(db.String(150), nullable=False)

    duration = db.Column(db.Integer, nullable=False)

    capacity = db.Column(db.Integer, nullable=False)

    is_active = db.Column(db.Boolean, default=True)

    department_id = db.Column(
        db.Integer,
        db.ForeignKey("departments.id"),
        nullable=False
    )

    department = db.relationship(
        "Department",
        back_populates="courses"
    )

    created_at = db.Column(
        db.DateTime,
        server_default=db.func.now()
    )

    def __repr__(self):
        return f"<Course {self.code}>"
    
    