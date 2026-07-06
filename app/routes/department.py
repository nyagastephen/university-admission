from flask import Blueprint, render_template
from flask_login import login_required
from flask import flash
from flask import request
from flask import redirect
from flask import url_for
from sqlalchemy import or_
from app.models.department import Department
from app.extensions import db
from app.utils.decorators import roles_required

department = Blueprint("department", __name__)

@department.route("/departments")
@login_required
@roles_required("Admin")
def list_departments():

    query = request.args.get("q", "").strip()
    page = request.args.get("page", 1, type=int)

    departments = Department.query

    if query:
        departments = departments.filter(
            Department.name.ilike(f"%{query}%")
        )

    departments = (
        departments
        .order_by(Department.name)
        .paginate(page=page, per_page=10)
    )

    return render_template(
        "departments/list.html",
        departments=departments,
        query=query
    )


@department.route("/departments/add", methods=["GET", "POST"])
@login_required
def add_department():

    if request.method == "POST":
        
        code = request.form["code"].strip().upper()

        name = request.form["name"].strip()

        description = request.form["description"].strip()

        existing = Department.query.filter(
        or_(
        Department.code == code,
        Department.name == name
        )
        ).first()

        if existing:
            flash("Department code or name already exists.", "danger")
            return render_template("departments/add.html")

        department = Department(
            code=code,
            name=name,
            description=description
        )

        db.session.add(department)

        db.session.commit()
        flash("Department created successfully.", "success")
        return redirect(url_for("department.list_departments"))

    return render_template("departments/add.html")

@department.route("/departments/<int:id>/edit", methods=["GET", "POST"])
@login_required
def edit_department(id):

    department = Department.query.get_or_404(id)

    if request.method == "POST":

        code = request.form["code"].strip().upper()

        name = request.form["name"].strip()

        description = request.form["description"].strip()

    

        existing = Department.query.filter(
        Department.id != id,
            or_(
        Department.code == code,
        Department.name == name
            )
        ).first()



        if existing and existing.id != id:
            flash("Another department already uses that code or name.", "danger")
            return render_template(
                "departments/edit.html",
                department=department
            )

        department.code = code
        department.name = name
        department.description = description

        db.session.commit()

        flash("Department updated successfully.", "success")
        return redirect(url_for("department.list_departments"))

    return render_template("departments/edit.html", department=department)

@department.route("/departments/<int:id>/deactivate")
@login_required
@roles_required("Admin")
def deactivate_department(id):

    department = Department.query.get_or_404(id)

    department.is_active = False
    for course in department.courses:
        course.is_active = False

    db.session.commit()
    flash(
    f"{department.name} has been deactivated.",
    "warning"
        )
    return redirect(url_for("department.list_departments"))

@department.route("/departments/<int:id>/activate")
@login_required
@roles_required("Admin")
def activate_department(id):

    department = Department.query.get_or_404(id)

    department.is_active = True
    for course in department.courses:
        course.is_active = True
    db.session.commit()
    flash(
    f"{department.name} has been activated.",  
    "success"
    )
    return redirect(url_for("department.list_departments"))
