from flask import render_template, session
from sqlalchemy import text

from main import main_bp
from extensions import db


def _current_username():
    if "user_id" in session:
        user = db.session.execute(
            text("SELECT * FROM users WHERE user_id = :user_id"),
            {"user_id": session["user_id"]},
        ).fetchone()
        return user.user_name if user else None
    return None


@main_bp.route("/")
def index():
    return render_template("main/index.html", username=_current_username())


@main_bp.route("/about")
def about():
    return render_template("main/about.html", username=_current_username())