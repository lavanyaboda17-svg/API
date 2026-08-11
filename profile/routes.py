from flask import render_template

from profile import profile_bp
from utils import login_required

@profile_bp.route("/user/profile/<int:user_id>")
@login_required
def user_profile(user_id):
    return render_template("profile/profile.html", user_id=user_id)