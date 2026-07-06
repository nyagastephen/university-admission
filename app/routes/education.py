from datetime import datetime

from flask import Blueprint
from flask import render_template
from flask import request
from flask import redirect
from flask import url_for
from flask import flash

from flask_login import login_required
from flask_login import current_user

from app.extensions import db

from app.models.applicant_profile import ApplicantProfile
from app.models.education_history import EducationHistory

education = Blueprint("education", __name__)

KCSE_GRADES = [
    "A",
    "A-",
    "B+",
    "B",
    "B-",
    "C+",
    "C",
    "C-",
    "D+",
    "D",
    "D-",
    "E"
]

MIN_EXAM_YEAR = 1990


@education.route("/education", methods=["GET", "POST"])
@login_required
def education_form():

    profile = ApplicantProfile.query.filter_by(
        user_id=current_user.id
    ).first()

    if not profile:

        flash(
            "Complete your profile first.",
            "warning"
        )

        return redirect(url_for("applicant.profile"))

    education = EducationHistory.query.filter_by(
        applicant_profile_id=profile.id
    ).first()

    if request.method == "POST":

        # Read form values
        school_name = request.form["school_name"].strip()
        index_number = request.form["index_number"].strip()
        exam_year = int(request.form["exam_year"])
        mean_grade = request.form["mean_grade"]
        certificate_number = request.form["certificate_number"].strip()

        # Validate exam year
        current_year = datetime.now().year

        if exam_year < MIN_EXAM_YEAR or exam_year > current_year:

            flash("Invalid examination year.", "danger")

            return render_template(
                "education/form.html",
                education=education,
                grades=KCSE_GRADES,
                current_year=current_year
            )

        # Validate grade
        if mean_grade not in KCSE_GRADES:

            flash("Please select a valid KCSE grade.", "danger")

            return render_template(
                "education/form.html",
                education=education,
                grades=KCSE_GRADES,
                current_year=current_year
            )

        # Check duplicate index number
        existing = EducationHistory.query.filter_by(
            index_number=index_number
        ).first()

        if existing and (education is None or existing.id != education.id):

            flash("KCSE Index Number already exists.", "danger")

            return render_template(
                "education/form.html",
                education=education,
                grades=KCSE_GRADES,
                current_year=current_year
            )

        # Create record if it doesn't exist
        if education is None:

            education = EducationHistory(
                applicant_profile_id=profile.id
            )

            db.session.add(education)

        # Save values
        education.school_name = school_name
        education.index_number = index_number
        education.exam_year = exam_year
        education.mean_grade = mean_grade
        education.certificate_number = certificate_number

        db.session.commit()

        flash(
            "Education history saved successfully.",
            "success"
        )

        return redirect(
            url_for("applicant.dashboard")
        )

    return render_template(
        "education/form.html",
        education=education,
        grades=KCSE_GRADES,
        current_year=datetime.now().year
    )