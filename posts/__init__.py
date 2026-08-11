from flask import Blueprint

posts_bp = Blueprint("posts", __name__)

from posts import routes  # noqa: E402,F401