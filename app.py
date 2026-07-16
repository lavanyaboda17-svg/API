from flask import Flask, request, render_template, session , redirect, url_for
from flask.cli import load_dotenv
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
import re
from datetime import timedelta
#used to represent a duration or the difference between two dates or times
from werkzeug.security import generate_password_hash, check_password_hash
#plain text → hashed and login time check 
from functools import wraps
import os

app = Flask(__name__)
load_dotenv()
app.secret_key = os.getenv("SECRET_KEY")
if not app.secret_key:
    raise RuntimeError("FLASK_SECRET_KEY must be set in your .env file")
app.permanent_session_lifetime = timedelta(minutes=5)

DB_USER = os.environ.get("DB_USER")
DB_PASSWORD = os.environ.get("DB_PASSWORD")
DB_HOST = os.environ.get("DB_HOST", "localhost")  # not secret, safe to default
DB_PORT = os.environ.get("DB_PORT", "5432")        # not secret, safe to default
DB_NAME = os.environ.get("DB_NAME")
 
if not all([DB_USER, DB_PASSWORD, DB_NAME]):
    raise RuntimeError(
        "DB_USER, DB_PASSWORD and DB_NAME must be set in your .env file"
    )
 
app.config["SQLALCHEMY_DATABASE_URI"] = (
    f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
 
db = SQLAlchemy(app)
# DEFAULT_USER_ID = 1


def init_db():
    """Create the users and posts tables if they don't already exist."""
    with app.app_context():
        db.session.execute(text("""
            CREATE TABLE IF NOT EXISTS users (
                user_id SERIAL PRIMARY KEY,
                user_name VARCHAR(20) UNIQUE NOT NULL,
                password VARCHAR(255) NOT NULL
            );
        """))
        db.session.execute(text("""
            CREATE TABLE IF NOT EXISTS posts (
                post_id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL REFERENCES users(user_id),
                title VARCHAR(255) NOT NULL,
                body TEXT NOT NULL
            );
        """))
        db.session.commit()


@app.route("/")
def index():
    username = None
    if "user_id" in session:
        user = db.session.execute(
            text("SELECT * FROM users WHERE user_id = :user_id"),
            {"user_id": session["user_id"]},
        ).fetchone()
        username = user.user_name
    return render_template("index.html", username=username)


@app.route("/about")
def about():
    username = None
    if "user_id" in session:
        user = db.session.execute(
            text("SELECT * FROM users WHERE user_id = :user_id"),
            {"user_id": session["user_id"]},
        ).fetchone()
        username = user.user_name
    return render_template("about.html", username=username)


# Login required decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))  
        return f(*args, **kwargs)
    return decorated_function


@app.route("/post")
@login_required
def post_page():
    user = db.session.execute(
        text("SELECT * FROM users WHERE user_id = :user_id"),
        {"user_id": session["user_id"]},
    ).fetchone()
    return render_template("create_post.html", username=user.user_name)


# Register
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")

    username = request.form.get("username")
    password = request.form.get("password")

    if not username or not password:
        return render_template("register.html", error="All fields are required")

    if not re.match(r'^[a-zA-Z0-9_]{3,20}$', username):
        return render_template("register.html",
                               error="Username must be 3-20 characters, only letters numbers and underscore allowed")
    
    if not re.match(r'^[A-Za-z0-9_@]{8,20}$', password):
        return render_template("register.html",
                           error="Password must be 8-20 characters, only letters, numbers, _ and @ allowed")

    existing_user = db.session.execute(
        text("SELECT * FROM users WHERE user_name = :username"),
        {"username": username}
    ).fetchone()

    if existing_user:
        return render_template("register.html", error="Username already exists, please login")
    
    hashed_password = generate_password_hash(password)

    try:
        db.session.execute(
            text(
                "INSERT INTO users (user_name, password) VALUES (:username, :password)"
            ),
            {"username": username, "password": hashed_password},
        )
        db.session.commit()

        user = db.session.execute(
            text("SELECT * FROM users WHERE user_name = :username"),
            {"username": username},
        ).fetchone()

        session.permanent = True
        session["user_id"] = user.user_id
        return redirect(url_for("post_page"))

    except Exception as e:
        db.session.rollback()
        print(e)
        return "Something went wrong", 500


@app.route("/user/profile/<int:user_id>")
@login_required
def user_profile(user_id):
    return render_template("profile.html", user_id=user_id)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))


# Login
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")

    username = request.form.get("username")
    password = request.form.get("password")

    if not username or not password:
        return render_template("login.html", error="All fields are required")

    try:
        user = db.session.execute(
            text("SELECT * FROM users WHERE user_name = :user_name"),
            {"user_name": username},
        ).fetchone()

        if not user:
            return render_template(
                "login.html", error="User not found! Please register first"
            )

        if not check_password_hash(user.password, password):
            return render_template("login.html", error="Incorrect password")

        session.permanent = True
        session["user_id"] = user.user_id
        return redirect(url_for("get_user_posts", user_id=user.user_id))

    except Exception as e:
        print(e)
        return "Something went wrong", 500


# Create post
@app.route("/create-post", methods=["POST"])
@login_required
def create_post():
    title = request.form.get("title")
    body = request.form.get("body")

    if not title or not body:
        return render_template("create_post.html", error="All fields are required")

    try:
        db.session.execute(
            text(
                "INSERT INTO posts (user_id, title, body) VALUES (:user_id, :title, :body)"
            ),
            {"user_id": session["user_id"], "title": title, "body": body},
        )
        db.session.commit()
        return redirect(url_for("get_user_posts", user_id=session["user_id"]))
    except Exception as e:
        db.session.rollback()
        print(e)
        return "Something went wrong", 500


# Fetch posts
@app.route("/user/<int:user_id>/posts")
@login_required
def get_user_posts(user_id):
    try:
        user = db.session.execute(
            text("SELECT * FROM users WHERE user_id = :user_id"), {"user_id": user_id}
        ).fetchone()

        if not user:
            return "User not found", 404

        result = db.session.execute(
            text("SELECT * FROM posts WHERE user_id = :user_id"), {"user_id": user_id}
        )
        posts = result.fetchall()
        show_all = request.args.get("show_all", False)
        return render_template(
            "view_post.html", posts=posts, show_all=show_all, username=user.user_name
        )

    except Exception as e:
        print(e)
        return "Something went wrong", 500
    


if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000, debug=True)
else:
    init_db()
    
# create_post:http://127.0.0.1:5000/post
# fetch user post:http://127.0.0.1:5000/users/1/posts
# git rebase develop