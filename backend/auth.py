# backend/auth.py
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash
from backend.models import db, User

auth_bp = Blueprint("auth", __name__)
login_manager = LoginManager()
login_manager.login_view = "auth.login" 

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("routes.dashboard"))

    if request.method == "POST":
        sicil_no = request.form.get("sicil_no", "").strip()
        password = request.form.get("password", "")

        user = User.query.filter_by(sicil_no=sicil_no).first()
        if not user or not check_password_hash(user.password, password):
            flash("Hatalı giriş denemesi", "danger")
            return render_template("login.html"), 401

        login_user(user)
        return redirect(url_for("routes.dashboard"))

    return render_template("login.html")

@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("auth.login"))
