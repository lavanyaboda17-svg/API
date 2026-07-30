from flask import Flask, request, render_template, session, redirect, url_for
from flask.cli import load_dotenv
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
import re
from datetime import timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from functools import wraps
import os
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer

app = Flask(__name__)
load_dotenv()
app.secret_key = os.getenv("SECRET_KEY")
if not app.secret_key:
    raise RuntimeError("FLASK_SECRET_KEY must be set in your .env file")
app.permanent_session_lifetime = timedelta(minutes=5)

DB_USER = os.environ.get("DB_USER")
DB_PASSWORD = os.environ.get("DB_PASSWORD")
DB_HOST = os.environ.get("DB_HOST", "localhost")
DB_PORT = os.environ.get("DB_PORT", "5432")
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

# ---- Mail config ----
app.config["MAIL_SERVER"] = os.getenv("MAIL_SERVER")
app.config["MAIL_PORT"] = int(os.getenv("MAIL_PORT"))
app.config["MAIL_USE_TLS"] = os.getenv("MAIL_USE_TLS") == "True"
app.config["MAIL_USERNAME"] = os.getenv("MAIL_USERNAME")
app.config["MAIL_PASSWORD"] = os.getenv("MAIL_PASSWORD")

mail = Mail(app)
serializer = URLSafeTimedSerializer(app.secret_key)

# ---- Image upload config ----
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}
UPLOAD_FOLDER = os.path.join(app.root_path, "static", "uploads")
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

# ---- Image upload config ----
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}
UPLOAD_FOLDER = os.path.join(app.root_path, "static", "uploads")
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

def init_db():
    """Create the users and posts tables if they don't already exist."""
    with app.app_context():
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
                image_url VARCHAR(255) NOT NULL
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
    email = request.form.get("email")

    if not username or not password or not email:
        return render_template("register.html", error="All fields are required")

    if not re.match(r'^[a-zA-Z0-9_]{3,20}$', username):
        return render_template("register.html",
                               error="Username must be 3-20 characters, only letters numbers and underscore allowed")
    if not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email):
        return render_template("register.html", error="Enter a valid email")

    if not re.match(r'^[A-Za-z0-9_@]{8,20}$', password):
        return render_template("register.html",
                           error="Password must be 8-20 characters, only letters, numbers, _ and @ allowed")

    existing_user = db.session.execute(
        text("SELECT * FROM users WHERE user_name = :username"),
        {"username": username}
    ).fetchone()

    if existing_user:
        return render_template("register.html", error="Username already exists, please login")

    existing_email = db.session.execute(
        text("SELECT * FROM users WHERE email = :email"),
        {"email": email}
    ).fetchone()

    if existing_email:
        return render_template("register.html", error="Email already registered, please Login")

    hashed_password = generate_password_hash(password)

    try:
        db.session.execute(
            text(
                "INSERT INTO users (user_name, email, password) VALUES (:username, :email, :password)"
            ),
            {"username": username, "password": hashed_password, "email": email},
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


# Forgot Password - Step 1: send reset link
@app.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "GET":
        return render_template("forgot_password.html")

    email = request.form.get("email")

    if not email:
        return render_template("forgot_password.html", error="Email is required")

    user = db.session.execute(
        text("SELECT * FROM users WHERE email = :email"),
        {"email": email}
    ).fetchone()

    if not user:
        return render_template("forgot_password.html", error="Email not found")

    token = serializer.dumps(email, salt="password-reset")
    reset_link = url_for("reset_password", token=token, _external=True)

    msg = Message("Password Reset Request",
                  sender=app.config["MAIL_USERNAME"],
                  recipients=[email])
    msg.body = f"Click the link to reset your password: {reset_link}\nThis link expires in 30 minutes."

    try:
        mail.send(msg)
        return render_template("forgot_password.html", message="Password reset link sent to your email!")
    except Exception as e:
        print(e)
        return render_template("forgot_password.html", error="Failed to send email")


# Forgot Password - Step 2: set new password via token
@app.route("/reset-password/<token>", methods=["GET", "POST"])
def reset_password(token):
    try:
        email = serializer.loads(token, salt="password-reset", max_age=1800)
    except Exception:
        return "This reset link is invalid or has expired.", 400

    if request.method == "GET":
        return render_template("reset_password.html", token=token)

    new_password = request.form.get("new_password")

    if not new_password or not re.match(r'^[A-Za-z0-9_@]{8,20}$', new_password):
        return render_template("reset_password.html", token=token,
                               error="Password must be 8-20 characters, only letters, numbers, _ and @ allowed")

    hashed_password = generate_password_hash(new_password)

    try:
        db.session.execute(
            text("UPDATE users SET password = :password WHERE email = :email"),
            {"password": hashed_password, "email": email},
        )
        db.session.commit()
        return redirect(url_for("login"))
    except Exception as e:
        db.session.rollback()
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

    file = request.files.get("image")

    if not file or file.filename == "":
        return render_template("create_post.html", error="Image is required")

    if not allowed_file(file.filename):
        return render_template("create_post.html", error="Invalid image type")

    image_filename = secure_filename(file.filename)
    save_path = os.path.join(app.config["UPLOAD_FOLDER"], image_filename)

    try:
        file.save(save_path)
    except Exception as e:
        print("DEBUG: SAVE FAILED WITH ERROR:", e)
        return f"Image save failed: {e}", 500

    try:
        db.session.execute(
            text(
                "INSERT INTO posts (user_id, title, body, image_url) "
                "VALUES (:user_id, :title, :body, :image_url)"
            ),
            {
                "user_id": session["user_id"],
                "title": title,
                "body": body,
                "image_url": image_filename,
            },
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
            text("SELECT * FROM posts WHERE user_id = :user_id ORDER BY post_id ASC"), {"user_id": user_id}
        )
        posts = result.fetchall()
        show_all = request.args.get("show_all", False)
        return render_template(
            "view_post.html", posts=posts, show_all=show_all, username=user.user_name
        )

    except Exception as e:
        print(e)
        return "Something went wrong", 500


# Edit post
@app.route("/post/<int:post_id>/edit", methods=["GET", "POST"])
@login_required
def edit_post(post_id):
    post = db.session.execute(
        text("SELECT * FROM posts WHERE post_id = :post_id"),
        {"post_id": post_id},
    ).fetchone()

    if not post:
        return "Post not found", 404

    if post.user_id != session["user_id"]:
        return "Not authorized", 403

    if request.method == "GET":
        return render_template("create_post.html", post=post)

    title = request.form.get("title")
    body = request.form.get("body")

    if not title or not body:
        return render_template("create_post.html", post=post, error="All fields are required")

    file = request.files.get("image")
    image_filename = post.image_url

    if file and file.filename != "":
        if not allowed_file(file.filename):
            return render_template("create_post.html", post=post, error="Invalid image type")
        image_filename = secure_filename(file.filename)
        save_path = os.path.join(app.config["UPLOAD_FOLDER"], image_filename)
        try:
            file.save(save_path)
        except Exception as e:
            print("DEBUG: SAVE FAILED WITH ERROR:", e)
            return f"Image save failed: {e}", 500

    try:
        db.session.execute(
            text(
                "UPDATE posts SET title = :title, body = :body, image_url = :image_url "
                "WHERE post_id = :post_id"
            ),
            {
                "title": title,
                "body": body,
                "image_url": image_filename,
                "post_id": post_id,
            },
        )
        db.session.commit()
        return redirect(url_for("get_user_posts", user_id=session["user_id"]))
    except Exception as e:
        db.session.rollback()
        print(e)
        return "Something went wrong", 500


# Delete post
@app.route("/post/<int:post_id>/delete", methods=["POST"])
@login_required
def delete_post(post_id):
    post = db.session.execute(
        text("SELECT * FROM posts WHERE post_id = :post_id"),
        {"post_id": post_id},
    ).fetchone()

    if not post:
        return "Post not found", 404

    if post.user_id != session["user_id"]:
        return "Not authorized", 403

    try:
        db.session.execute(
            text("DELETE FROM posts WHERE post_id = :post_id"),
            {"post_id": post_id},
        )
        db.session.commit()
        return redirect(url_for("get_user_posts", user_id=session["user_id"]))
    except Exception as e:
        db.session.rollback()
        print(e)
        return "Something went wrong", 500

    try:
        db.session.execute(
            text("DELETE FROM posts WHERE post_id = :post_id"),
            {"post_id": post_id},
        )
        db.session.commit()
        return redirect(url_for("get_user_posts", user_id=session["user_id"]))
    except Exception as e:
        db.session.rollback()
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