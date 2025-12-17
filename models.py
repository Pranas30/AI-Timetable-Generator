from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Teacher(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    department = db.Column(db.String(100), nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

class SubjectEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    semester = db.Column(db.String(10), nullable=False)
    subject_name = db.Column(db.String(100), nullable=False)
    subject_code = db.Column(db.String(50), nullable=False)
    priority = db.Column(db.Integer, nullable=False)
    teacher_name = db.Column(db.String(100), nullable=False)
    
    # ** NEW COLUMN ADDED HERE **
    hours_per_week = db.Column(db.Integer, nullable=False)