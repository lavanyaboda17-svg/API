import re
from flask import request, render_template, session, redirect, url_for, current_app
from sqlalchemy import text
from werkzeug.security import generate_password_hash, check_password_hash
from flask_mail import Message

from auth import auth_bp
from extensions import db, mail


# Register 
@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("auth/register.html")

    username = request.form.get("username")
    password = request.form.get("password")
    email = request.form.get("email")

    if not username or not password or not email:
        return render_template("auth/register.html", error="All fields are required")

    if not re.match(r'^[a-zA-Z0-9_]{3,20}$', username):
        return render_template(
            "auth/register.html",
            error="Username must be 3-20 characters, only letters numbers and underscore allowed",
        )
    if not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email):
        return render_template("auth/register.html", error="Enter a valid email")

    if not re.match(r'^[A-Za-z0-9_@]{8,20}$', password):
        return render_template(
            "auth/register.html",
            error="Password must be 8-20 characters, only letters, numbers, _ and @ allowed",
        )

    existing_user = db.session.execute(
        text("SELECT * FROM users WHERE user_name = :username"),
        {"username": username},
    ).fetchone()
    if existing_user:
        return render_template("auth/register.html", error="Username already exists, please login")

    existing_email = db.session.execute(
        text("SELECT * FROM users WHERE email = :email"),
        {"email": email},
    ).fetchone()
    if existing_email:
        return render_template("auth/register.html", error="Email already registered, please Login")

    hashed_password = generate_password_hash(password)

    try:
        db.session.execute(
            text("INSERT INTO users (user_name, email, password) VALUES (:username, :email, :password)"),
            {"username": username, "password": hashed_password, "email": email},
        )
        db.session.commit()

        user = db.session.execute(
            text("SELECT * FROM users WHERE user_name = :username"),
            {"username": username},
        ).fetchone()

        session.permanent = True
        session["user_id"] = user.user_id
        return redirect(url_for("posts.post_page"))

    except Exception as e:
        db.session.rollback()
        print(e)
        return "Something went wrong", 500


#Login 
@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("auth/login.html")

    username = request.form.get("username")
    password = request.form.get("password")

    if not username or not password:
        return render_template("auth/login.html", error="All fields are required")

    try:
        user = db.session.execute(
            text("SELECT * FROM users WHERE user_name = :user_name"),
            {"user_name": username},
        ).fetchone()

        if not user:
            return render_template("auth/login.html", error="User not found! Please register first")

        if not check_password_hash(user.password, password):
            return render_template("auth/login.html", error="Incorrect password")

        session.permanent = True
        session["user_id"] = user.user_id
        return redirect(url_for("posts.get_user_posts", user_id=user.user_id))

    except Exception as e:
        print(e)
        return "Something went wrong", 500


#  Logout 
@auth_bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("main.index"))


# Forgot password: send reset link
@auth_bp.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "GET":
        return render_template("auth/forgot_password.html")

    email = request.form.get("email")

    if not email:
        return render_template("auth/forgot_password.html", error="Email is required")

    user = db.session.execute(
        text("SELECT * FROM users WHERE email = :email"),
        {"email": email},
    ).fetchone()

    if not user:
        return render_template("auth/forgot_password.html", error="Email not found")

    token = current_app.serializer.dumps(email, salt="password-reset")
    reset_link = url_for("auth.reset_password", token=token, _external=True)

    msg = Message(
        "Password Reset Request",
        sender=current_app.config["MAIL_USERNAME"],
        recipients=[email],
    )
    msg.body = f"Click the link to reset your password: {reset_link}\nThis link expires in 30 minutes."

    try:
        mail.send(msg)
        return render_template("auth/forgot_password.html", message="Password reset link sent to your email!")
    except Exception as e:
        print(e)
        return render_template("auth/forgot_password.html", error="Failed to send email")


# Forgot password: set new password via token
@auth_bp.route("/reset-password/<token>", methods=["GET", "POST"])
def reset_password(token):
    try:
        email = current_app.serializer.loads(token, salt="password-reset", max_age=1800)
    except Exception:
        return "This reset link is invalid or has expired.", 400

    if request.method == "GET":
        return render_template("auth/reset_password.html", token=token)

    new_password = request.form.get("new_password")

    if not new_password or not re.match(r'^[A-Za-z0-9_@]{8,20}$', new_password):
        return render_template(
            "auth/reset_password.html",
            token=token,
            error="Password must be 8-20 characters, only letters, numbers, _ and @ allowed",
        )

    hashed_password = generate_password_hash(new_password)

    try:
        db.session.execute(
            text("UPDATE users SET password = :password WHERE email = :email"),
            {"password": hashed_password, "email": email},
        )
        db.session.commit()
        return redirect(url_for("auth.login"))
    except Exception as e:
        db.session.rollback()
        print(e)
        return "Something went wrong", 500