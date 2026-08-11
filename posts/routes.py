from flask import request, render_template, session, redirect, url_for
from sqlalchemy import text
import cloudinary.uploader

from posts import posts_bp
from extensions import db
from utils import login_required, allowed_file

# Show create-post page
@posts_bp.route("/post")
@login_required
def post_page():
    user = db.session.execute(
        text("SELECT * FROM users WHERE user_id = :user_id"),
        {"user_id": session["user_id"]},
    ).fetchone()
    return render_template("posts/create_post.html", username=user.user_name)


#  Create post 
@posts_bp.route("/create-post", methods=["POST"])
@login_required
def create_post():
    title = request.form.get("title")
    body = request.form.get("body")

    if not title or not body:
        return render_template("posts/create_post.html", error="All fields are required")

    file = request.files.get("image")

    if not file or file.filename == "":
        return render_template("posts/create_post.html", error="Image is required")

    if not allowed_file(file.filename):
        return render_template("posts/create_post.html", error="Invalid image type")

    try:
        result = cloudinary.uploader.upload(file)
        image_filename = result["secure_url"]
        image_public_id = result.get("public_id")
    except Exception as e:
        print("DEBUG: CLOUDINARY UPLOAD FAILED:", e)
        return f"Image upload failed: {e}", 500

    try:
        db.session.execute(
            text(
                "INSERT INTO posts (user_id, title, body, image_url, image_public_id) "
                "VALUES (:user_id, :title, :body, :image_url, :image_public_id)"
            ),
            {
                "user_id": session["user_id"],
                "title": title,
                "body": body,
                "image_url": image_filename,
                "image_public_id": image_public_id,
            },
        )
        db.session.commit()
        return redirect(url_for("posts.get_user_posts", user_id=session["user_id"]))
    except Exception as e:
        db.session.rollback()
        print(e)
        return "Something went wrong", 500


# Fetch a user's posts 
@posts_bp.route("/user/<int:user_id>/posts")
@login_required
def get_user_posts(user_id):
    try:
        user = db.session.execute(
            text("SELECT * FROM users WHERE user_id = :user_id"), {"user_id": user_id}
        ).fetchone()

        if not user:
            return "User not found", 404

        result = db.session.execute(
            text("SELECT * FROM posts WHERE user_id = :user_id ORDER BY post_id ASC"),
            {"user_id": user_id},
        )
        posts = result.fetchall()
        show_all = request.args.get("show_all", False)
        return render_template(
            "posts/view_post.html", posts=posts, show_all=show_all, username=user.user_name
        )

    except Exception as e:
        print(e)
        return "Something went wrong", 500


#Single post
@posts_bp.route("/post/<int:post_id>")
@login_required
def single_post(post_id):
    try:
        post = db.session.execute(
            text("SELECT * FROM posts WHERE post_id = :post_id"),
            {"post_id": post_id},
        ).fetchone()

        if not post:
            return "Post not found", 404

        return render_template("posts/single_post.html", post=post)

    except Exception as e:
        print(e)
        return "Something went wrong", 500


# Edit post 
@posts_bp.route("/post/<int:post_id>/edit", methods=["GET", "POST"])
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
        return render_template("posts/create_post.html", post=post)

    title = request.form.get("title")
    body = request.form.get("body")

    if not title or not body:
        return render_template("posts/create_post.html", post=post, error="All fields are required")

    file = request.files.get("image")
    image_filename = post.image_url
    image_public_id = post.image_public_id

    if file and file.filename != "":
        if not allowed_file(file.filename):
            return render_template("posts/create_post.html", post=post, error="Invalid image type")
        try:
            result = cloudinary.uploader.upload(file)
            if post.image_public_id:
                cloudinary.uploader.destroy(post.image_public_id)
            image_filename = result["secure_url"]
            image_public_id = result.get("public_id")
        except Exception as e:
            print("DEBUG: CLOUDINARY UPLOAD FAILED:", e)
            return f"Image upload failed: {e}", 500

    try:
        db.session.execute(
            text(
                "UPDATE posts SET title = :title, body = :body, image_url = :image_url, "
                "image_public_id = :image_public_id WHERE post_id = :post_id"
            ),
            {
                "title": title,
                "body": body,
                "image_url": image_filename,
                "image_public_id": image_public_id,
                "post_id": post_id,
            },
        )
        db.session.commit()
        return redirect(url_for("posts.get_user_posts", user_id=session["user_id"]))
    except Exception as e:
        db.session.rollback()
        print(e)
        return "Something went wrong", 500


# Delete post 
@posts_bp.route("/post/<int:post_id>/delete", methods=["POST"])
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
        if post.image_public_id:
            cloudinary.uploader.destroy(post.image_public_id)

        db.session.execute(
            text("DELETE FROM posts WHERE post_id = :post_id"),
            {"post_id": post_id},
        )
        db.session.commit()
        return redirect(url_for("posts.get_user_posts", user_id=session["user_id"]))
    except Exception as e:
        db.session.rollback()
        print(e)
        return "Something went wrong", 500