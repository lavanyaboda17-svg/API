from flask import Flask, request, render_template
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
import re


app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = 'postgresql://lavanya:123@localhost:5432/post'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

DEFAULT_USER_ID = 1

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/post")
def post_page():
    return render_template("post.html")

# POST API 1: Create User
@app.route("/create-user", methods=["POST"])
def create_user():
    username = request.form.get("username")

    if not username:
        return "Username is required", 400

    if not re.match("^[a-zA-Z]+$", username):
        return render_template("index.html", error="Invalid username")

    try:
        db.session.execute(
            text("INSERT INTO users (user_name) VALUES (:username)"),
            {"username": username}
        )
        db.session.commit()
        return render_template("user_success.html", username=username)
    except:
        db.session.rollback()
        return "Something went wrong!", 500


# POST API 2: Create Post
@app.route("/create-post", methods=["POST"])
def create_post():
    title = request.form.get("title")
    body = request.form.get("body")

    if not title or not body:
        return "All fields are required", 400

    try:
        db.session.execute(
            text("INSERT INTO posts (user_id, title, body) VALUES (:user_id, :title, :body)"),
            {"user_id": DEFAULT_USER_ID, "title": title, "body": body}
        )
        db.session.commit()
        return render_template("post_success.html", title=title)
    except:
        db.session.rollback()
        return "Something went wrong!", 500

#fetch posts
@app.route("/users/<int:user_id>/posts")
def get_user_posts(user_id):
    with db.session.begin(): #DB operation manage
        user = db.session.execute(
        text("SELECT * FROM users WHERE user_id = :user_id"),
        {"user_id": user_id}
    )

    users = user.fetchall()

    if not users:
        return "User not found", 404

    result = db.session.execute(
        text("SELECT * FROM posts WHERE user_id = :user_id"),
        {"user_id": user_id}
    )

    posts = result.fetchall()

    return render_template("single_post.html", posts=posts)
   
    
if __name__ == "__main__":
    app.run(debug=True)


#create_post:http://127.0.0.1:5000/post
#fetch user post:http://127.0.0.1:5000/users/1/posts
#git rebase develop
