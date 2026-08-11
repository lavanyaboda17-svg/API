from flask import session, redirect, url_for
from sqlalchemy import text
from functools import wraps

from extensions import db

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    return decorated_function


def init_db():
    """Create the users and posts tables if they don't already exist."""
    db.session.execute(text("""
        CREATE TABLE IF NOT EXISTS users (
            user_id SERIAL PRIMARY KEY,
            user_name VARCHAR(20) UNIQUE NOT NULL,
            email VARCHAR(255) UNIQUE NOT NULL,
            password VARCHAR(255) NOT NULL
        );
    """))
    db.session.execute(text("""
        CREATE TABLE IF NOT EXISTS posts (
            post_id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL REFERENCES users(user_id),
            title VARCHAR(255) NOT NULL,
            body TEXT NOT NULL,
            image_url VARCHAR(255) NOT NULL,
            image_public_id VARCHAR(255)
        );
    """))
    db.session.execute(text("""
        ALTER TABLE posts ADD COLUMN IF NOT EXISTS image_public_id VARCHAR(255);
    """))
    db.session.commit()