import profile
from flask import Blueprint
from flask import render_template
from flask import request
from flask import redirect
from flask import url_for
from flask import flash
from flask import jsonify
from flask_login import login_required
from flask_login import current_user
from app.extensions import db
from app.models import application
from app.models.applicant_profile import ApplicantProfile
from app.models.application import Application
from app.models.department import Department
from app.models.course import Course
from app.utils.decorators import roles_required
from app.models.education_history import EducationHistory
from app.models.uploaded_document import UploadedDocument
from app.routes.document import DOCUMENT_TYPES


application_bp = Blueprint("application", __name__)

@application_bp.route("/api/courses/<int:department_id>")
@login_required
@roles_required("Applicant")
def get_courses(department_id):

        courses = Course.query.filter_by(
        department_id=department_id,
        is_active=True
    ).order_by(
        Course.name
    ).all()

        return jsonify([
        {
            "id": course.id,
            "name": course.name
        }
        for course in courses
    ])

@application_bp.route("/application", methods=["GET", "POST"])
@login_required
@roles_required("Applicant")
def application_form():

    profile = ApplicantProfile.query.filter_by(
        user_id=current_user.id
    ).first()
   
    if not profile:
        flash("Complete your profile first.", "warning")
        return redirect(url_for("applicant.profile"))

    departments = Department.query.filter_by(
        is_active=True
    ).order_by(
        Department.name
    ).all()

    application_record = Application.query.filter_by(
        applicant_profile_id=profile.id
    ).first()

    # Already submitted
    if request.method == "GET" and application_record:
        return render_template(
            "application/form.html",
            departments=departments,
            application=application_record
        )

    if request.method == "POST":

        education = EducationHistory.query.filter_by(
            applicant_profile_id=profile.id
        ).first()

        if not education:
            flash(
                "Complete your education history first.",
                "warning"
            )
            return redirect(
                url_for("education.education_form")
            )
        
        uploaded = UploadedDocument.query.filter_by(
            applicant_profile_id=profile.id
        ).count()

        if uploaded != len(DOCUMENT_TYPES):
            flash(
                "Upload all required documents before submitting your application.",
                "warning"
            )
            return redirect(
                url_for("document.list_documents")
            )
        department_id = request.form.get("department")
        course_id = request.form.get("course")

        if not department_id or not course_id:
                flash(
        "Please select a department and course.",
        "danger"
    )
                return redirect(
                url_for("application.application_form")
    )

        if application_record:

            flash(
        "You have already submitted an application.",
        "warning"
    )

            return redirect(
        url_for("application.application_form")
    )

        new_application = Application(
        applicant_profile_id=profile.id,
        department_id=int(department_id),
        course_id=int(course_id),
        status="Submitted"
        )

        db.session.add(new_application)
        db.session.commit()

        flash(
        "Application submitted successfully.",
        "success"
        )
        
        return redirect(
        url_for("application.application_form")
        )
    return render_template(
    "application/form.html",
    departments=departments,
    application=application_record
)