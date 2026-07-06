from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from sqlalchemy import or_

from app.extensions import db
from app.models.course import Course
from app.models.department import Department
from app.utils.decorators import roles_required

course = Blueprint("course", __name__)

@course.route("/courses")
@login_required
@roles_required("Admin")
def list_courses():

    courses = Course.query.order_by(Course.name).all()
    
    query = request.args.get("q", "").strip()

    courses = Course.query

    if query:

        courses = courses.filter(
        or_(
            Course.code.ilike(f"%{query}%"),
            Course.name.ilike(f"%{query}%")
        )
    )
    page = request.args.get("page", 1, type=int)

    courses = (
    courses
    .order_by(Course.name)
    .paginate(page=page, per_page=10)
    )
    return render_template(
    "courses/list.html",
    courses=courses,
    query=query
    )
   


@course.route("/courses/add", methods=["GET", "POST"])
@login_required
@roles_required("Admin")
def add_course():

    departments = Department.query.filter_by(
        is_active=True
    ).order_by(
        Department.name
    ).all()

    if request.method == "POST":

        code = request.form["code"].strip().upper()
        name = request.form["name"].strip()
        duration = int(request.form["duration"])
        capacity = int(request.form["capacity"])
        department_id = int(request.form["department_id"])

        existing = Course.query.filter(
            or_(
                Course.code == code,
                Course.name == name
            )
        ).first()

        if existing:

            flash("Course already exists.", "danger")

            return render_template(
                "courses/add.html",
                departments=departments
            )

        course = Course(
            code=code,
            name=name,
            duration=duration,
            capacity=capacity,
            department_id=department_id
        )

        db.session.add(course)
        db.session.commit()

        flash("Course added successfully.", "success")

        return redirect(url_for("course.list_courses"))

    return render_template(
        "courses/add.html",
        departments=departments
    )

@course.route("/courses/<int:id>/edit", methods=["GET", "POST"])
@login_required
@roles_required("Admin")
def edit_course(id):

    course = Course.query.get_or_404(id)

    departments = Department.query.filter_by(
        is_active=True
    ).order_by(
        Department.name
    ).all()

    if request.method == "POST":

        code = request.form["code"].strip().upper()
        name = request.form["name"].strip()
        duration = int(request.form["duration"])
        capacity = int(request.form["capacity"])
        department_id = int(request.form["department_id"])

        existing = Course.query.filter(
            Course.id != id,
            or_(
                Course.code == code,
                Course.name == name
            )
        ).first()

        if existing:
            flash("Another course already exists with that code or name.", "danger")
            return render_template(
                "courses/edit.html",
                course=course,
                departments=departments
            )

        course.code = code
        course.name = name
        course.duration = duration
        course.capacity = capacity
        course.department_id = department_id

        db.session.commit()

        flash("Course updated successfully.", "success")

        return redirect(url_for("course.list_courses"))

    return render_template(
        "courses/edit.html",
        course=course,
        departments=departments
    )

@course.route("/courses/<int:id>/deactivate")
@login_required
@roles_required("Admin")
def deactivate_course(id):

    course = Course.query.get_or_404(id)

    course.is_active = False

    db.session.commit()

    flash("Course deactivated.", "warning")

    return redirect(url_for("course.list_courses"))

@course.route("/courses/<int:id>/activate")
@login_required
@roles_required("Admin")
def activate_course(id):

    course = Course.query.get_or_404(id)

    course.is_active = True

    db.session.commit()

    flash("Course activated.", "success")

    return redirect(url_for("course.list_courses"))