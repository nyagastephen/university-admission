from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash
from app.extensions import db
from app.models.user import User
from flask import Blueprint, render_template
from flask import request,redirect,url_for
from flask_login import login_user, logout_user, login_required

auth = Blueprint("auth", __name__)

@auth.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form["username"].strip()

        password = request.form["password"]

        user = User.query.filter_by(
            username=username
        ).first()

        if user and check_password_hash(user.password, password):

            login_user(user)

            if user.role == "Admin":
                return redirect(url_for("admin.dashboard"))

            elif user.role == "Admissions Officer":
                return redirect(url_for("admissions.dashboard"))

            elif user.role == "Applicant":
                return redirect(url_for("applicant.dashboard"))

            else:
                return redirect(url_for("main.home"))

        else:

            return render_template(
                "login.html",
                error="Invalid username or password."
            )

    return render_template("login.html")

@auth.route("/logout")
@login_required
def logout():

    logout_user()

    return redirect(url_for("main.home"))

@auth.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        username = request.form["username"]

        email = request.form["email"]

        password = request.form["password"]

        confirm = request.form["confirm"]

        if password != confirm:

            return "Passwords do not match"

        existing_user = User.query.filter_by(username=username).first()

        if existing_user:

            return "Username already exists"

        existing_email = User.query.filter_by(email=email).first()

        if existing_email:

            return "Email already exists"

        hashed_password = generate_password_hash(password)

        user = User(

            username=username,

            email=email,

            password=hashed_password,

            role="Applicant"

        )

        db.session.add(user)

        db.session.commit()

        return redirect(url_for("auth.login"))

    return render_template("register.html")