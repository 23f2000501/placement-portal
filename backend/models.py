from datetime import datetime
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()
bcrypt = Bcrypt()


class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    is_blacklisted = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    company = db.relationship("CompanyProfile", back_populates="user", uselist=False)
    student_profile = db.relationship("StudentProfile", back_populates="user", uselist=False)

    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode("utf-8")

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)


class CompanyProfile(db.Model):
    __tablename__ = "companies"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    company_name = db.Column(db.String(200), nullable=False)
    hr_contact = db.Column(db.String(120), nullable=False)
    website = db.Column(db.String(200), nullable=True)
    description = db.Column(db.Text, nullable=True)
    approved = db.Column(db.Boolean, default=False)
    rejected = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship("User", back_populates="company")
    drives = db.relationship("PlacementDrive", back_populates="company")


class StudentProfile(db.Model):
    __tablename__ = "students"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    branch = db.Column(db.String(100), nullable=False)
    year = db.Column(db.String(20), nullable=False)
    cgpa = db.Column(db.Float, nullable=False)
    resume_url = db.Column(db.String(300), nullable=True)
    placement_history = db.Column(db.Text, nullable=True)

    user = db.relationship("User", back_populates="student_profile")
    applications = db.relationship("Application", back_populates="student")


class PlacementDrive(db.Model):
    __tablename__ = "placement_drives"
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey("companies.id"), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    branch_eligibility = db.Column(db.String(200), nullable=True)
    min_cgpa = db.Column(db.Float, nullable=False, default=0.0)
    year_eligibility = db.Column(db.String(100), nullable=True)
    application_deadline = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(30), default="Pending")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    company = db.relationship("CompanyProfile", back_populates="drives")
    applications = db.relationship("Application", back_populates="drive")


class Application(db.Model):
    __tablename__ = "applications"
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("students.id"), nullable=False)
    drive_id = db.Column(db.Integer, db.ForeignKey("placement_drives.id"), nullable=False)
    application_date = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(30), default="Applied")
    message = db.Column(db.String(300), nullable=True)

    student = db.relationship("StudentProfile", back_populates="applications")
    drive = db.relationship("PlacementDrive", back_populates="applications")
    interview_schedule = db.relationship("InterviewSchedule", back_populates="application", uselist=False, cascade="all, delete-orphan")


class InterviewSchedule(db.Model):
    __tablename__ = "interview_schedules"
    id = db.Column(db.Integer, primary_key=True)
    application_id = db.Column(db.Integer, db.ForeignKey("applications.id"), nullable=False, unique=True)
    proposed_slots = db.Column(db.Text, nullable=True)
    selected_slot = db.Column(db.String(255), nullable=True)
    student_proposed_slots = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(30), default="Pending")
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    application = db.relationship("Application", back_populates="interview_schedule")
