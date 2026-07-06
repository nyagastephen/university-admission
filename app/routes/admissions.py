import html

from flask import Blueprint, current_app,render_template, request, redirect, url_for, flash
from flask import render_template
from flask_login import login_required
from app.models.application import Application
from app.models.department import Department
from app.models.course import Course
from app.routes import document, education
from app.routes.applicant import profile
from app.utils.decorators import roles_required
from flask import Blueprint
from flask import render_template
from flask import request
from app.extensions import db
from app.models.applicant_profile import ApplicantProfile
from app.utils.decorators import roles_required
from app.models.education_history import EducationHistory
from app.models.uploaded_document import UploadedDocument
from datetime import datetime
from flask_login import login_required, current_user
from app.utils.audit import log_application_action
from app.models.application_log import ApplicationLog
from weasyprint import HTML
import os
import uuid
from app.models import AdmissionLetter
from flask import send_from_directory
from flask import current_app

admissions = Blueprint("admissions", __name__)


@admissions.route("/admissions/dashboard")
@login_required
@roles_required("Admin", "Admissions Officer")
def dashboard():

    total = Application.query.count()

    submitted = Application.query.filter_by(
        status="Submitted"
    ).count()

    under_review = Application.query.filter_by(
        status="Under Review"
    ).count()

    shortlisted = Application.query.filter_by(
        status="Shortlisted"
    ).count()

    accepted = Application.query.filter_by(
        status="Accepted"
    ).count()

    rejected = Application.query.filter_by(
        status="Rejected"
    ).count()

    recent = (
        Application.query
        .order_by(Application.created_at.desc())
        .limit(10)
        .all()
    )

    return render_template(
        "admissions/dashboard.html",
        total=total,
        submitted=submitted,
        under_review=under_review,
        shortlisted=shortlisted,
        accepted=accepted,
        rejected=rejected,
        recent=recent
    )

@admissions.route("/admissions/applications")
@login_required
@roles_required("Admissions Officer")
def applications():

    search = request.args.get("search", "").strip()
    department = request.args.get("department", type=int)
    course = request.args.get("course", type=int)
    status = request.args.get("status", "").strip()
    page = request.args.get("page", 1, type=int)

    query = (
        Application.query
        .join(ApplicantProfile)
        .join(Department)
        .join(Course)
    )

    # Search applicant name or application number
    if search:

        if search.upper().startswith("APP-"):

            query = query.filter(
                Application.id == int(search.split("-")[-1])
            )

        else:

            query = query.filter(

                db.or_(

                    ApplicantProfile.first_name.ilike(f"%{search}%"),

                    ApplicantProfile.last_name.ilike(f"%{search}%")

                )

            )

    # Department
    if department:

        query = query.filter(
            Application.department_id == department
        )

    # Course
    if course:

        query = query.filter(
            Application.course_id == course
        )

    # Status
    if status:

        query = query.filter(
            Application.status == status
        )

    applications = (
        query
        .order_by(Application.created_at.desc())
        .paginate(
            page=page,
            per_page=10,
            error_out=False
        )
    )

    departments = (
        Department.query
        .filter_by(is_active=True)
        .order_by(Department.name)
        .all()
    )

    courses = (
        Course.query
        .filter_by(is_active=True)
        .order_by(Course.name)
        .all()
    )

    statuses = [

        "Submitted",

        "Under Review",

        "Shortlisted",

        "Accepted",

        "Rejected"

    ]

    return render_template(

        "admissions/applications.html",

        applications=applications,

        departments=departments,

        courses=courses,

        statuses=statuses,

        search=search,

        department=department,

        course=course,

        status=status

    )

@admissions.route("/admissions/applications/<int:id>")
@login_required
@roles_required("Admissions Officer")
def view_application(id):

    application = Application.query.get_or_404(id)

    profile = application.applicant

    education = EducationHistory.query.filter_by(
        applicant_profile_id=profile.id
    ).first()

    documents = UploadedDocument.query.filter_by(
        applicant_profile_id=profile.id
    ).all()

    statuses = [

        "Submitted",

        "Under Review",

        "Shortlisted",

        "Accepted",

        "Rejected"

    ]
    logs = ApplicationLog.query.filter_by(
        application_id=application.id
    ).order_by(
    ApplicationLog.created_at.desc()
    ).all()
    return render_template(

        "admissions/view_application.html",

        application=application,

        profile=profile,

        education=education,

        documents=documents,

        statuses=statuses,
        logs=logs

    )

@admissions.route("/documents/<int:id>/verify", methods=["POST"])
@login_required
@roles_required("Admissions Officer")
def verify_document(id):

    document = UploadedDocument.query.get_or_404(id)

    status = request.form.get("verification_status")
    comment = request.form.get("verification_comment")
    print(request.form)
    print("Status:", request.form.get("verification_status"))
    print("Comment:", repr(request.form.get("verification_comment")))

    if status not in ["Pending", "Verified", "Rejected"]:
        flash("Invalid verification status.", "danger")
        return redirect(
            url_for(
                "admissions.view_application",
                id=document.applicant.application.id
            )
        )

    if status == "Rejected" and not comment.strip():
        flash(
            "Please provide a reason for rejecting the document.",
            "warning"
        )
        return redirect(
            url_for(
                "admissions.view_application",
                id=document.applicant.application.id
            )
        )

    document.verification_status = status
    document.verification_comment = comment
    document.verified_by = current_user.id
    document.verified_at = datetime.utcnow()

    db.session.commit()
    db.session.refresh(document)

    print(document.verification_status)
    print(document.verification_comment)
    flash("Document review saved successfully.", "success")

    return redirect(
        url_for(
            "admissions.view_application",
            id=document.applicant.application.id
        )
    )
@admissions.route(
    "/applications/<int:id>/status",
    methods=["POST"]
)
@login_required
@roles_required("Admissions Officer")
def update_status(id):

    application = Application.query.get_or_404(id)

    status = request.form.get("status")

    allowed = [

        "Submitted",

        "Under Review",

        "Shortlisted",

        "Accepted",

        "Rejected"

    ]

    if status not in allowed:

        flash(

            "Invalid status.",

            "danger"

        )

        return redirect(

            url_for(

                "admissions.view_application",

                id=id

            )

        )

    
    application = Application.query.get_or_404(id)

    old_status = application.status

    new_status = request.form["status"]

    application.status = new_status

    log_application_action(
    application.id,
    "Status Changed",
    f"Status changed from '{old_status}' to '{new_status}'."
    )

    db.session.commit()

    flash("Application status updated.", "success")

    return redirect(
        url_for("admissions.view_application", id=id)
    )

@admissions.route(
    "/applications/<int:id>/review",
    methods=["POST"]
)
@login_required
@roles_required("Admissions Officer")
def save_review(id):

    application = Application.query.get_or_404(id)

    application.review_notes = request.form.get(
        "review_notes"
    )

    application.reviewed_by = current_user.id

    application.reviewed_at = datetime.now()
    log_application_action(

        application.id,

        "Review Updated",

        "Admissions review notes updated."

    )

    db.session.commit()

    flash(
        "Review saved successfully.",
        "success"
    )

    return redirect(
        url_for(
            "admissions.view_application",
            id=id
        )
    )
    

@admissions.route(
    "/applications/<int:id>/generate-letter"
)
@login_required
def generate_letter(id):

    application = Application.query.get_or_404(id)

    if application.status != "Accepted":

        flash(
            "Only accepted applications can receive admission letters.",
            "danger"
        )

        return redirect(
            url_for(
                "admissions.view_application",
                id=id
            )
        )
    existing = AdmissionLetter.query.filter_by(
        application_id=id
        ).first()

    if existing:

        flash(
        "Admission letter already exists.",
        "info"
    )

        return redirect(
        url_for(
            "admissions.view_application",
            id=id
        )
    )
    letter = AdmissionLetter(

    application_id=id,

    letter_number=f"ADM-{application.created_at.year}-{application.id:06d}",

    file_name=f"{uuid.uuid4()}.pdf",

    generated_by=current_user.id

)

    db.session.add(letter)

    db.session.flush()

    html = render_template(

    "admissions/admission_letter.html",

    application=application,

    letter=letter,

    logo_path=os.path.join(
        current_app.static_folder,
        "images/logo.png"
    )

)
    pdf_path = os.path.join(

    current_app.static_folder,

    "admission_letters",

    letter.file_name

)

    HTML(
        string=html,
        base_url=current_app.root_path
    ).write_pdf(pdf_path)

    db.session.commit()

    log_application_action(

        application.id,

        "Admission Letter Generated",

        f"Letter {letter.letter_number} generated."

    )

    db.session.commit()
    
    # return redirect(
    # url_for(
    #     "document.view_admission_letter",
    #     id=letter.id
    # )
    # )
    return redirect(
    url_for(
        "admissions.view_letter",
        id=letter.id
    )
    )

@admissions.route("/letters/<int:id>")
@login_required
def view_letter(id):

    letter = AdmissionLetter.query.get_or_404(id)

    return send_from_directory(
        os.path.join(
            current_app.static_folder,
            "admission_letters"
        ),
        letter.file_name
    )
    
