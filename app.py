import os
from datetime import timedelta

from flask import Flask
from flask.cli import load_dotenv
from itsdangerous import URLSafeTimedSerializer

from config import Config
from extensions import db, mail, init_cloudinary

load_dotenv()


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    if not app.config["SECRET_KEY"]:
        raise RuntimeError("SECRET_KEY must be set in your .env file")

    if not all([app.config["DB_USER"], app.config["DB_PASSWORD"], app.config["DB_NAME"]]):
        raise RuntimeError("DB_USER, DB_PASSWORD and DB_NAME must be set in your .env file")

    app.permanent_session_lifetime = timedelta(minutes=5)

    # init extensions
    db.init_app(app)
    mail.init_app(app)
    init_cloudinary(app)

    # upload folder
    app.config["UPLOAD_FOLDER"] = os.path.join(app.root_path, "static", "uploads")
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    #serializer for password reset tokens 
    app.serializer = URLSafeTimedSerializer(app.config["SECRET_KEY"])

    #  register blueprints
    from auth import auth_bp
    from posts import posts_bp
    from profile import profile_bp
    from main import main_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(posts_bp)
    app.register_blueprint(profile_bp)
    app.register_blueprint(main_bp)

    #init db tables
    from utils import init_db
    with app.app_context():
        init_db()

    return app


app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

