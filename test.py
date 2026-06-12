from flask import Flask, request, render_template, session , redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
import re
from datetime import timedelta
#used to represent a duration or the difference between two dates or times
from werkzeug.security import generate_password_hash, check_password_hash
#plain text → hashed and login time check 
from functools import wraps


app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.permanent_session_lifetime = timedelta(minutes=1)

app.config["SQLALCHEMY_DATABASE_URI"] = 'postgresql://lavanya:123@localhost:5432/post'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
# DEFAULT_USER_ID = 1

@app.route("/")
def index():
    return render_template("index.html")


#Login required
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
    return render_template("post.html")


# POST API 1: User Registration
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")

    username = request.form.get("username")
    password = request.form.get("password")

    # Step 1: Validation
    if not username or not password:
        return render_template("register.html", error="All fields are required")

    if not re.match(r'^[a-zA-Z0-9_]{3,20}$', username):
        return render_template("register.html",
                               error="Username must be 3-20 characters, only letters numbers and underscore allowed")
    
    if not re.match(r'^[A-Za-z0-9_@]{8,20}$', password):
        return render_template("register.html",
                           error="Password must be 8-20 characters, only letters, numbers, _ and @ allowed")

    # Step 2: Check existing user
    existing_user = db.session.execute(
        text("SELECT * FROM users WHERE user_name = :username"),
        {"username": username}
    ).fetchone()

    if existing_user:
        return render_template("register.html", error="Username already exists, please login")

    # Step 3: Hash password
    hashed_password = generate_password_hash(password)

    try:
        # Step 4: Insert new user
        db.session.execute(
            text("INSERT INTO users (user_name, password) VALUES (:username, :password)"),
            {"username": username, "password": hashed_password}
        )
        db.session.commit()

        # Step 5: Fetch user for session
        user = db.session.execute(
            text("SELECT * FROM users WHERE user_name = :username"),
            {"username": username}
        ).fetchone()

        # Step 6: Set session and redirect
        session.permanent = True
        session['user_id'] = user.user_id
        return redirect(url_for('post_page'))

    except Exception as e:
        db.session.rollback()
        print(e)
        return "Something went wrong", 500
  
    
@app.route("/user/profile/<int:user_id>")
@login_required
def user_profile(user_id):
    return render_template("profile.html", user_id=user_id)
    
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
            {"user_name": username}
        ).fetchone()
        
        if not user:
            return render_template("login.html", error="User not found! Please register first")
        
        if not check_password_hash(user.password,password):
            return render_template("login.html", error= "incorrect password")
        
        session.permanent = True
        session['user_id'] = user.user_id
        return redirect(url_for('get_user_posts', user_id=user.user_id))
    except Exception as e:
        return "Something went wrong", 500
    
# POST API 2: Create Post
@app.route("/create-post", methods=["POST"])
@login_required
def create_post():
    title = request.form.get("title")
    body = request.form.get("body")

    if not title or not body:
        return render_template("post.html", error="All fields are required")
    
    try:
        with db.session.begin():
            db.session.execute(
                text("INSERT INTO posts (user_id, title, body) VALUES (:user_id, :title, :body)"),
                {"user_id": session['user_id'], "title": title, "body": body}
                )
            return redirect(url_for('get_user_posts', user_id=session['user_id']))
    except:
        db.session.rollback()
        return "Something went wrong", 500

#fetch posts
@app.route("/user/<int:user_id>/posts")
# @app.route("/users/<int:user_id>/posts")
@login_required
def get_user_posts(user_id):
    try: 
        user = db.session.execute(
                text("SELECT * FROM users WHERE user_id = :user_id"),
                {"user_id": user_id}
                )
        user = user.fetchone()
        if not user:
                return "User not found", 404
        
        result = db.session.execute(
                text("SELECT * FROM posts WHERE user_id = :user_id"),
                {"user_id": user_id}
                )
        posts = result.fetchall()
        show_all = request.args.get('show_all', False)
        return render_template("single_post.html", posts=posts, show_all=show_all)    
    except Exception as e:
        print(e)
        return "Something went wrong", 500
    
if __name__ == "__main__":
    app.run(debug=True)


#create_post:http://127.0.0.1:5000/post
#fetch user post:http://127.0.0.1:5000/users/1/posts
#git rebase develop