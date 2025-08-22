from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title_en = db.Column(db.String(128))
    title_ar = db.Column(db.String(128))
    description_en = db.Column(db.Text)
    description_ar = db.Column(db.Text)
    detailed_description_en = db.Column(db.Text)
    detailed_description_ar = db.Column(db.Text)
    image = db.Column(db.String(128))
    images = db.Column(db.Text)  # JSON string for multiple images
    link = db.Column(db.String(256))
    technologies = db.Column(db.String(512))  # Comma-separated technologies
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

class ProjectImage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
    image_path = db.Column(db.String(256), nullable=False)
    caption_en = db.Column(db.String(256))
    caption_ar = db.Column(db.String(256))
    order = db.Column(db.Integer, default=0)

class Visitor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ip = db.Column(db.String(64))
    visit_time = db.Column(db.DateTime, default=datetime.utcnow)
    duration = db.Column(db.Integer, default=0)
    lang = db.Column(db.String(8), default='ar')

class SocialLink(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    url = db.Column(db.String(255), nullable=False)
    icon = db.Column(db.String(100), nullable=False)  # مثال: 'fab fa-facebook'

class AboutMe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text_ar = db.Column(db.Text, nullable=False, default='')
    text_en = db.Column(db.Text, nullable=False, default='')
