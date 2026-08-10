from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
import cloudinary

db = SQLAlchemy()
mail = Mail()


def init_cloudinary(app):
    cloudinary.config(
        cloud_name=app.config.get("CLOUDINARY_CLOUD_NAME"),
        api_key=app.config.get("CLOUDINARY_API_KEY"),
        api_secret=app.config.get("CLOUDINARY_API_SECRET"),
    )