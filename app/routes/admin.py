from flask import Blueprint, render_template
from flask_login import login_required
from app.utils.decorators import roles_required

admin = Blueprint("admin", __name__)

@admin.route("/dashboard")
@login_required
@roles_required("Admin")
def dashboard():

    return render_template("dashboard.html")