from flask import Blueprint, render_template, request
from flask_login import login_required, current_user
from app.extensions import db
from app.models.applicant_profile import ApplicantProfile
from app.models.applicant_profile import ApplicantProfile
from app.models.education_history import EducationHistory
from app.models.application import Application
from app.models.uploaded_document import UploadedDocument
from app.utils.decorators import roles_required
from app.routes.document import DOCUMENT_TYPES
from datetime import datetime
import os
from flask import (
    abort,
    current_app,
    flash,
    redirect,
    send_from_directory,
    url_for
)
applicant = Blueprint("applicant", __name__)

@applicant.route("/applicant/dashboard")
@login_required
@roles_required("Applicant")
def dashboard():

    profile = ApplicantProfile.query.filter_by(
        user_id=current_user.id
    ).first()

    profile_complete = profile is not None

    education_complete = False
    documents_complete = False
    application = None

    if profile:

        education_complete = (
            EducationHistory.query.filter_by(
                applicant_profile_id=profile.id
            ).first()
            is not None
        )

        uploaded = UploadedDocument.query.filter_by(
            applicant_profile_id=profile.id
        ).count()

        documents_complete = (
            uploaded == len(DOCUMENT_TYPES)
        )

        application = Application.query.filter_by(
            applicant_profile_id=profile.id
        ).first()

    profile = ApplicantProfile.query.filter_by(
        user_id=current_user.id
    ).first_or_404()

    application = profile.application

    letter = None

    if application:
        letter = application.admission_letter

    # return render_template(
    #     "applicant/dashboard.html",
    #     profile=profile,
    #     application=application,
    #     letter=letter
    # )
    return render_template(
        "applicant/dashboard.html",
        profile=profile,
        profile_complete=profile_complete,
        education_complete=education_complete,
        documents_complete=documents_complete,
        application=application,
        letter=letter
    )

@applicant.route("/applicant/profile", methods=["GET", "POST"])
@login_required
@roles_required("Applicant")
def profile():

    profile = ApplicantProfile.query.filter_by(
        user_id=current_user.id
    ).first()

    if request.method == "POST":

        if profile is None:

            profile = ApplicantProfile(
                user_id=current_user.id
            )

            db.session.add(profile)

        profile.first_name = request.form["first_name"].strip()

        profile.middle_name = request.form["middle_name"].strip()

        profile.last_name = request.form["last_name"].strip()

        profile.gender = request.form["gender"]

        profile.date_of_birth = datetime.strptime(request.form["date_of_birth"],"%Y-%m-%d").date()

        profile.national_id = request.form["national_id"].strip()

        profile.phone = request.form["phone"].strip()

        profile.nationality = request.form["nationality"].strip()

        profile.county = request.form["county"].strip()

        profile.city = request.form["city"].strip()

        profile.postal_address = request.form["postal_address"].strip()

      

        db.session.commit()

        flash(
            "Profile saved successfully.",
            "success"
        )

        return redirect(
            url_for("applicant.dashboard")
        )

    return render_template(
        "applicant/profile.html",
        profile=profile
    )

@applicant.route("/applicant/profile/view")
@login_required
def view_profile():

    profile = ApplicantProfile.query.filter_by(
        user_id=current_user.id
    ).first_or_404()

    return render_template(
        "applicant/view_profile.html",
        profile=profile
    )
@applicant.route("/admission-letter")
@login_required
def download_letter():

    profile = ApplicantProfile.query.filter_by(
        user_id=current_user.id
    ).first_or_404()

    application = profile.application

    if not application:
        abort(404)

    letter = application.admission_letter

    if not letter:
        flash(
            "Admission letter is not available.",
            "warning"
        )
        return redirect(
            url_for("applicant.dashboard")
        )

    return send_from_directory(
        os.path.join(
            current_app.static_folder,
            "admission_letters"
        ),
        letter.file_name,
        as_attachment=True
    )



    