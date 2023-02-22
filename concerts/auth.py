from flask import Blueprint, render_template, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user

from .forms import LoginForm, RegisterForm
from .models import User
from . import db


bp = Blueprint("auth", __name__)


@bp.route("/account", methods=["GET", "POST"])
def account():
    """
    Renders the login page.
    """
    error = None
    loginform = LoginForm()

    if loginform.validate_on_submit():
        email = loginform.email.data
        password = loginform.password.data

        user = User.query.filter_by(email=email).first()

        if user is None:
            error = "Incorrect email"
        elif not check_password_hash(user.hash, password):
            error = "Incorrect password"

        if error is None:
            login_user(user)
        else:
            flash(error)

        return redirect(url_for("auth.account"))

    return render_template("pages/account.jinja", loginform=loginform)


@bp.route("/register", methods=["GET", "POST"])
def register():
    """
    Renders the register page.
    """
    error = None
    registerform = RegisterForm()

    if registerform.validate_on_submit():
        username = registerform.username.data
        email = registerform.email.data
        password = registerform.password.data
        contact = registerform.contact.data
        address = registerform.address.data

        if User.query.filter_by(username=username).first():
            error = "Username already exists"
        elif User.query.filter_by(email=email).first():
            error = "Email already exists"

        if error is None:
            hash = generate_password_hash(password)
            user = User(
                username=username,
                email=email,
                hash=hash,
                contact_number=contact,
                address=address,
            )

            db.session.add(user)
            db.session.commit()

            flash("Successfully registered")
            return redirect(url_for("auth.account"))
        else:
            flash(error)

        return redirect(url_for("auth.account"))

    return render_template("pages/register.jinja", registerform=registerform)


@bp.route("/logout")
@login_required
def logout():
    """
    Logs out the user and redirects to the account page.
    """
    logout_user()
    flash("Successfully logged out")
    return redirect(url_for("auth.account"))
