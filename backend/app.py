import csv
import os
import re
from datetime import date, datetime, timedelta
from flask import Flask, jsonify, request, send_file
from flask_caching import Cache
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required
from sqlalchemy import or_

from config import Config
from models import Application, CompanyProfile, InterviewSchedule, PlacementDrive, StudentProfile, User, bcrypt, db
from utils import role_required


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    CORS(
        app,
        resources={r"/api/*": {"origins": ["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:5174", "http://127.0.0.1:5174"]}},
        supports_credentials=True,
        allow_headers=["Content-Type", "Authorization", "X-Requested-With"],
        methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    )

    @app.before_request
    def handle_options():
        if request.method == "OPTIONS":
            return app.make_default_options_response()

    @app.after_request
    def add_cors_headers(response):
        origin = request.headers.get("Origin")
        allowed_origins = {"http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:5174", "http://127.0.0.1:5174"}
        if origin in allowed_origins:
            response.headers["Access-Control-Allow-Origin"] = origin
            response.headers["Access-Control-Allow-Credentials"] = "true"
            response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization, X-Requested-With"
            response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
            response.headers["Vary"] = "Origin"
        return response

    db.init_app(app)
    bcrypt.init_app(app)
    JWTManager(app)
    cache = Cache(app)

    with app.app_context():
        db.create_all()

        def normalize_text(value):
            return re.sub(r"[^a-z0-9]+", " ", str(value or "").lower()).strip()

        def is_branch_match(student_branch, eligibility):
            if not eligibility:
                return True
            allowed_values = [normalize_text(item) for item in eligibility.split(",") if normalize_text(item)]
            if not allowed_values:
                return True
            normalized_student = normalize_text(student_branch)
            if any(item in {"all", "any", "all branches", "any branch"} for item in allowed_values):
                return True
            if any(item in {"btech", "b tech", "bachelors of technology", "engineering", "be", "b e"} for item in allowed_values):
                return True
            return normalized_student in allowed_values

        def is_year_match(student_year, eligibility):
            if not eligibility:
                return True
            normalized_student = normalize_text(student_year)
            allowed_values = [normalize_text(item) for item in eligibility.split(",") if normalize_text(item)]
            if not allowed_values:
                return True
            student_num = re.search(r"\d+", normalized_student)
            for value in allowed_values:
                allowed_num = re.search(r"\d+", value)
                if student_num and allowed_num:
                    if int(student_num.group(0)) >= int(allowed_num.group(0)):
                        return True
                if normalized_student == value:
                    return True
            return False

        admin = User.query.filter_by(email="admin@institute.edu").first()
        if not admin:
            admin = User(name="Institute Admin", email="admin@institute.edu", role="admin", is_active=True)
            admin.set_password("Admin@123")
            db.session.add(admin)
            db.session.commit()

        student = User.query.filter_by(email="student@institute.edu").first()
        if not student:
            student = User(name="Demo Student", email="student@institute.edu", role="student", is_active=True)
            student.set_password("Student@123")
            db.session.add(student)
            db.session.flush()

            student_profile = StudentProfile(
                user_id=student.id,
                branch="CSE",
                year="3rd Year",
                cgpa=8.7,
                resume_url="",
                placement_history="",
            )
            db.session.add(student_profile)
            db.session.commit()

        demo_company_user = User.query.filter_by(email="demo-company@company.com").first()
        if not demo_company_user:
            demo_company_user = User(name="Demo Company", email="demo-company@company.com", role="company", is_active=True)
            demo_company_user.set_password("Company@123")
            db.session.add(demo_company_user)
            db.session.flush()

            demo_company = CompanyProfile(
                user_id=demo_company_user.id,
                company_name="Demo Corp",
                hr_contact="HR Team",
                website="https://democorp.example.com",
                description="Default approved drive for all students.",
                approved=True,
                rejected=False,
            )
            db.session.add(demo_company)
            db.session.commit()
        else:
            demo_company = demo_company_user.company
            if demo_company and not demo_company.approved:
                demo_company.approved = True
                demo_company.rejected = False
                db.session.commit()

        default_drive = PlacementDrive.query.filter_by(
            title="Campus Placement Drive",
            company_id=demo_company.id,
        ).first()
        if not default_drive:
            default_drive = PlacementDrive(
                company_id=demo_company.id,
                title="Campus Placement Drive",
                description="A default approved drive open to all students.",
                branch_eligibility="",
                min_cgpa=0.0,
                year_eligibility="",
                application_deadline=date.today() + timedelta(days=30),
                status="Approved",
            )
            db.session.add(default_drive)
            db.session.commit()
        else:
            updated = False
            if default_drive.status != "Approved":
                default_drive.status = "Approved"
                updated = True
            if default_drive.application_deadline < date.today():
                default_drive.application_deadline = date.today() + timedelta(days=30)
                updated = True
            if updated:
                db.session.commit()

    @app.route("/api/auth/login", methods=["POST"])
    def login():
        data = request.json or {}
        email = data.get("email")
        password = data.get("password")
        user = User.query.filter_by(email=email).first()
        if not user or not user.check_password(password):
            return jsonify({"message": "Invalid email or password"}), 401
        if not user.is_active or user.is_blacklisted:
            return jsonify({"message": "Account blocked"}), 403

        token = create_access_token(identity=str(user.id), expires_delta=timedelta(hours=8))
        return jsonify({
            "access_token": token,
            "user": {
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "role": user.role,
            },
        })

    @app.route("/api/auth/register_student", methods=["POST"])
    def register_student():
        data = request.json or {}
        email = data.get("email")
        if User.query.filter_by(email=email).first():
            return jsonify({"message": "Email already exists"}), 400

        user = User(name=data.get("name"), email=email, role="student", is_active=True)
        user.set_password(data.get("password"))
        db.session.add(user)
        db.session.flush()

        student = StudentProfile(
            user_id=user.id,
            branch=data.get("branch", ""),
            year=data.get("year", ""),
            cgpa=float(data.get("cgpa", 0)),
            resume_url=data.get("resume_url", ""),
            placement_history="",
        )
        db.session.add(student)
        db.session.commit()
        return jsonify({"message": "Student registered successfully"}), 201

    @app.route("/api/auth/register_company", methods=["POST"])
    def register_company():
        data = request.json or {}
        email = data.get("email")
        if User.query.filter_by(email=email).first():
            return jsonify({"message": "Email already exists"}), 400

        owner_name = data.get("contact_person") or data.get("name") or "Company Contact"
        user = User(name=owner_name, email=email, role="company", is_active=True)
        user.set_password(data.get("password"))
        db.session.add(user)
        db.session.flush()

        company = CompanyProfile(
            user_id=user.id,
            company_name=data.get("company_name"),
            hr_contact=data.get("hr_contact"),
            website=data.get("website", ""),
            description=data.get("description", ""),
        )
        db.session.add(company)
        db.session.commit()
        return jsonify({"message": "Company registered successfully. Awaiting approval."}), 201

    @app.route("/api/admin/dashboard", methods=["GET"])
    @jwt_required()
    @role_required("admin")
    def admin_dashboard(current_user):
        return jsonify({
            "total_students": User.query.filter_by(role="student").count(),
            "total_companies": User.query.filter_by(role="company").count(),
            "total_drives": PlacementDrive.query.count(),
            "approved_drives": PlacementDrive.query.filter_by(status="Approved").count(),
            "pending_drives": PlacementDrive.query.filter_by(status="Pending").count(),
            "approved_companies": CompanyProfile.query.filter_by(approved=True).count(),
            "pending_companies": CompanyProfile.query.filter_by(approved=False, rejected=False).count(),
            "total_applications": Application.query.count(),
            "confirmed_interviews": Application.query.filter_by(status="Confirmed").count(),
            "interview_scheduled": Application.query.filter_by(status="Interview Scheduled").count(),
            "selected_applications": Application.query.filter_by(status="Selected").count(),
            "rejected_applications": Application.query.filter_by(status="Rejected").count(),
        })

    @app.route("/api/admin/companies", methods=["GET"])
    @jwt_required()
    @role_required("admin")
    def get_companies(current_user):
        search = request.args.get("search", "")
        query = CompanyProfile.query.join(User).filter(
            or_(
                CompanyProfile.company_name.ilike(f"%{search}%"),
                User.email.ilike(f"%{search}%"),
                User.name.ilike(f"%{search}%"),
            )
        )
        companies = [{
            "id": c.id,
            "user_id": c.user_id,
            "company_name": c.company_name,
            "hr_contact": c.hr_contact,
            "website": c.website,
            "description": c.description,
            "approved": c.approved,
            "rejected": c.rejected,
            "email": c.user.email,
            "blacklisted": c.user.is_blacklisted,
        } for c in query.all()]
        return jsonify(companies)
    
    @app.route("/api/admin/students", methods=["GET"])
    @jwt_required()
    @role_required("admin")
    def get_students(current_user):
        search = request.args.get("search", "")
        query = StudentProfile.query.join(User).filter(
            or_(
                User.name.ilike(f"%{search}%"),
                User.email.ilike(f"%{search}%"),
                StudentProfile.branch.ilike(f"%{search}%"),
                StudentProfile.year.ilike(f"%{search}%"),
            )
        )
        students = [{
            "id": s.user.id,
            "student_profile_id": s.id,
            "name": s.user.name,
            "email" : s.user.email,
            "branch": s.branch,
            "year": s.year,
            "cgpa" : s.cgpa,
            "blacklisted": s.user.is_blacklisted,
        } for s in query.all()]
        return jsonify(students)

    @app.route("/api/admin/companies/<int:company_id>/approve", methods=["POST"])
    @jwt_required()
    @role_required("admin")
    def approve_company(current_user, company_id):
        company = CompanyProfile.query.get_or_404(company_id)
        company.approved = True
        company.rejected = False
        db.session.commit()
        return jsonify({"message": "Company approved successfully"})

    @app.route("/api/admin/companies/<int:company_id>/reject", methods=["POST"])
    @jwt_required()
    @role_required("admin")
    def reject_company(current_user, company_id):
        company = CompanyProfile.query.get_or_404(company_id)
        company.approved = False
        company.rejected = True
        db.session.commit()
        return jsonify({"message": "Company rejected successfully"})

    @app.route("/api/admin/drives", methods=["GET"])
    @jwt_required()
    @role_required("admin")
    def admin_drives(current_user):
        search = request.args.get("search", "")
        query = PlacementDrive.query.join(CompanyProfile).join(User).filter(
            or_(
                PlacementDrive.title.ilike(f"%{search}%"),
                CompanyProfile.company_name.ilike(f"%{search}%"),
                User.name.ilike(f"%{search}%"),
            )
        )
        drives = [{
            "id": d.id,
            "title": d.title,
            "company_name": d.company.company_name,
            "status": d.status,
            "deadline": d.application_deadline.isoformat(),
            "created_by": d.company.user.name,
        } for d in query.order_by(PlacementDrive.created_at.desc()).all()]
        return jsonify(drives)

    @app.route("/api/admin/drives/<int:drive_id>/approve", methods=["POST"])
    @jwt_required()
    @role_required("admin")
    def approve_drive(current_user, drive_id):
        drive = PlacementDrive.query.get_or_404(drive_id)
        drive.status = "Approved"
        db.session.commit()
        return jsonify({"message": "Placement drive approved successfully"})

    @app.route("/api/admin/drives/<int:drive_id>/reject", methods=["POST"])
    @jwt_required()
    @role_required("admin")
    def reject_drive(current_user, drive_id):
        drive = PlacementDrive.query.get_or_404(drive_id)
        drive.status = "Rejected"
        db.session.commit()
        return jsonify({"message": "Placement drive rejected successfully"})

    @app.route("/api/admin/users/<int:user_id>/toggle_blacklist", methods=["POST"])
    @jwt_required()
    @role_required("admin")
    def toggle_blacklist(current_user, user_id):
        user = User.query.get_or_404(user_id)
        user.is_blacklisted = not user.is_blacklisted
        db.session.commit()
        return jsonify({"message": "Status updated successfully", "blacklisted": user.is_blacklisted})

    @app.route("/api/admin/companies/<int:company_id>/toggle_blacklist", methods=["POST"])
    @jwt_required()
    @role_required("admin")
    def toggle_company_blacklist(current_user, company_id):
        company = CompanyProfile.query.get_or_404(company_id)
        user = User.query.get_or_404(company.user_id)
        user.is_blacklisted = not user.is_blacklisted
        db.session.commit()
        return jsonify({"message": "Company status updated successfully", "blacklisted": user.is_blacklisted})

    @app.route("/api/admin/applications", methods=["GET"])
    @jwt_required()
    @role_required("admin")
    def admin_applications(current_user):
        apps = Application.query.order_by(Application.application_date.desc()).all()
        return jsonify([{
            "id": a.id,
            "student_profile_id": a.student.id,
            "student_user_id": a.student.user.id,
            "student_name": a.student.user.name,
            "student_email": a.student.user.email,
            "student_branch": a.student.branch,
            "student_year": a.student.year,
            "company_profile_id": a.drive.company.id,
            "company_user_id": a.drive.company.user.id,
            "company_name": a.drive.company.company_name,
            "company_email": a.drive.company.user.email,
            "drive_id": a.drive.id,
            "drive_title": a.drive.title,
            "status": a.status,
            "date": a.application_date.isoformat(),
        } for a in apps])

    @app.route("/api/company/dashboard", methods=["GET"])
    @jwt_required()
    @role_required("company")
    def company_dashboard(current_user):
        profile = CompanyProfile.query.filter_by(user_id=current_user.id).first()
        if not profile:
            return jsonify({"message": "Company profile not found"}), 404

        drives = PlacementDrive.query.filter_by(company_id=profile.id).all()
        return jsonify({
            "company_name": profile.company_name,
            "approved": profile.approved,
            "drives": [{
                "id": d.id,
                "title": d.title,
                "status": d.status,
                "applicants": len(d.applications),
            } for d in drives],
        })

    @app.route("/api/company/drives", methods=["POST"])
    @jwt_required()
    @role_required("company")
    def create_drive(current_user):
        profile = CompanyProfile.query.filter_by(user_id=current_user.id).first()
        if not profile or not profile.approved:
            return jsonify({"message": "Company profile not approved"}), 403

        data = request.json or {}
        drive = PlacementDrive(
            company_id=profile.id,
            title=data.get("title"),
            description=data.get("description", ""),
            branch_eligibility=data.get("branch_eligibility", ""),
            min_cgpa=float(data.get("min_cgpa", 0)),
            year_eligibility=data.get("year_eligibility", ""),
            application_deadline=datetime.strptime(data.get("application_deadline"), "%Y-%m-%d").date(),
            status="Pending",
        )
        db.session.add(drive)
        db.session.commit()
        return jsonify({"message": "Placement drive created successfully"}), 201

    @app.route("/api/company/drives/<int:drive_id>/applications", methods=["GET"])
    @jwt_required()
    @role_required("company")
    def company_drive_applications(current_user, drive_id):
        profile = CompanyProfile.query.filter_by(user_id=current_user.id).first()
        if not profile or not profile.approved:
            return jsonify({"message": "Company profile not approved"}), 403

        drive = PlacementDrive.query.filter_by(id=drive_id, company_id=profile.id).first()
        if not drive:
            return jsonify({"message": "Drive not found"}), 404

        return jsonify([{ 
            "id": a.id,
            "student_name": a.student.user.name,
            "student_email": a.student.user.email,
            "status": a.status,
            "branch": a.student.branch,
            "cgpa": a.student.cgpa,
            "interview": {
                "id": a.interview_schedule.id if a.interview_schedule else None,
                "status": a.interview_schedule.status if a.interview_schedule else None,
                "proposed_slots": a.interview_schedule.proposed_slots.split("\n") if a.interview_schedule and a.interview_schedule.proposed_slots else [],
                "selected_slot": a.interview_schedule.selected_slot if a.interview_schedule else None,
                "student_proposed_slots": a.interview_schedule.student_proposed_slots.split("\n") if a.interview_schedule and a.interview_schedule.student_proposed_slots else [],
                "notes": a.interview_schedule.notes if a.interview_schedule else None,
            } if a.interview_schedule else None,
        } for a in drive.applications])

    @app.route("/api/company/applications/<int:app_id>/update", methods=["POST"])
    @jwt_required()
    @role_required("company")
    def update_application_status(current_user, app_id):
        data = request.json or {}
        app_obj = Application.query.get_or_404(app_id)
        profile = CompanyProfile.query.filter_by(user_id=current_user.id).first()
        if app_obj.drive.company_id != profile.id:
            return jsonify({"message": "Unauthorized access"}), 403

        app_obj.status = data.get("status", app_obj.status)
        if data.get("status") == "Interview Scheduled" and not app_obj.interview_schedule:
            schedule = InterviewSchedule(application_id=app_obj.id, status="Pending")
            db.session.add(schedule)
        db.session.commit()
        return jsonify({"message": "Application status updated successfully"})

    @app.route("/api/company/applications/<int:app_id>/schedule", methods=["POST"])
    @jwt_required()
    @role_required("company")
    def schedule_interview(current_user, app_id):
        data = request.json or {}
        app_obj = Application.query.get_or_404(app_id)
        profile = CompanyProfile.query.filter_by(user_id=current_user.id).first()
        if app_obj.drive.company_id != profile.id:
            return jsonify({"message": "Unauthorized access"}), 403

        slots = [slot.strip() for slot in data.get("proposed_slots", []) if slot and slot.strip()]
        schedule = app_obj.interview_schedule or InterviewSchedule(application_id=app_obj.id)
        schedule.proposed_slots = "\n".join(slots)
        # Companies should only propose slots. The candidate chooses and confirms the selected slot.
        # Ignore any selected_slot sent by the company to prevent company-side selection.
        schedule.status = data.get("status", "Slots Proposed")
        schedule.notes = data.get("notes", schedule.notes)
        db.session.add(schedule)
        app_obj.status = "Interview Scheduled"
        db.session.commit()
        return jsonify({"message": "Interview schedule updated successfully"})

    @app.route("/api/student/applications/<int:app_id>/respond", methods=["POST"])
    @jwt_required()
    @role_required("student")
    def respond_to_interview(current_user, app_id):
        data = request.json or {}
        app_obj = Application.query.get_or_404(app_id)
        student = StudentProfile.query.filter_by(user_id=current_user.id).first()
        if app_obj.student_id != student.id:
            return jsonify({"message": "Unauthorized access"}), 403

        schedule = app_obj.interview_schedule or InterviewSchedule(application_id=app_obj.id)
        if data.get("selected_slot"):
            schedule.selected_slot = data.get("selected_slot")
            schedule.status = "Confirmed"
            # mark the application as confirmed so company and student see the update
            app_obj.status = "Confirmed"
        elif data.get("student_proposed_slots"):
            slots = [slot.strip() for slot in data.get("student_proposed_slots", []) if slot and slot.strip()]
            schedule.student_proposed_slots = "\n".join(slots)
            schedule.status = "Reschedule Requested"
        else:
            schedule.status = "Pending"
        db.session.add(schedule)
        db.session.commit()
        return jsonify({"message": "Interview response recorded"})

    @app.route("/api/student/dashboard", methods=["GET"])
    @jwt_required()
    @role_required("student")
    def student_dashboard(current_user):
        student = StudentProfile.query.filter_by(user_id=current_user.id).first()
        if not student:
            return jsonify({"available_drives": [], "applied_drives": []})

        applied_drive_ids = {
            application.drive_id
            for application in Application.query.filter_by(student_id=student.id).all()
        }

        eligible_drives = PlacementDrive.query.filter(
            PlacementDrive.status == "Approved",
            PlacementDrive.application_deadline >= date.today(),
        ).all()

        available_drives = []
        applied_drives = []
        for drive in eligible_drives:
            branch_ok = is_branch_match(student.branch, drive.branch_eligibility)
            year_ok = is_year_match(student.year, drive.year_eligibility)
            if branch_ok and year_ok and student.cgpa >= drive.min_cgpa:
                drive_payload = {
                    "id": drive.id,
                    "title": drive.title,
                    "company_name": drive.company.company_name,
                    "deadline": drive.application_deadline.isoformat(),
                    "status": drive.status,
                }
                if drive.id in applied_drive_ids:
                    applied_drives.append(drive_payload)
                else:
                    available_drives.append(drive_payload)
        return jsonify({"available_drives": available_drives, "applied_drives": applied_drives})

    @app.route("/api/student/apply", methods=["POST"])
    @jwt_required()
    @role_required("student")
    def apply_to_drive(current_user):
        student = StudentProfile.query.filter_by(user_id=current_user.id).first()
        data = request.json or {}
        drive = PlacementDrive.query.get_or_404(data.get("drive_id"))

        if drive.status != "Approved":
            return jsonify({"message": "Drive is not open for applications"}), 400
        if Application.query.filter_by(student_id=student.id, drive_id=drive.id).first():
            return jsonify({"message": "Already applied to this drive"}), 400
        if student.cgpa < drive.min_cgpa:
            return jsonify({"message": "CGPA does not meet the minimum requirement"}), 400
        if not is_branch_match(student.branch, drive.branch_eligibility):
            return jsonify({"message": "Branch not eligible for this drive"}), 400
        if not is_year_match(student.year, drive.year_eligibility):
            return jsonify({"message": "Year not eligible for this drive"}), 400

        application = Application(student_id=student.id, drive_id=drive.id)
        db.session.add(application)
        db.session.commit()
        return jsonify({"message": "Applied to drive successfully"})

    @app.route("/api/student/applications", methods=["GET"])
    @jwt_required()
    @role_required("student")
    def student_applications(current_user):
        student = StudentProfile.query.filter_by(user_id=current_user.id).first()
        applications = Application.query.filter_by(student_id=student.id).order_by(Application.application_date.desc()).all()
        return jsonify([{
            "id": a.id,
            "drive_id": a.drive.id,
            "drive_title": a.drive.title,
            "company_name": a.drive.company.company_name,
            "status": a.status,
            "application_date": a.application_date.isoformat(),
            "interview": {
                "id": a.interview_schedule.id if a.interview_schedule else None,
                "status": a.interview_schedule.status if a.interview_schedule else None,
                "proposed_slots": a.interview_schedule.proposed_slots.split("\n") if a.interview_schedule and a.interview_schedule.proposed_slots else [],
                "selected_slot": a.interview_schedule.selected_slot if a.interview_schedule else None,
                "student_proposed_slots": a.interview_schedule.student_proposed_slots.split("\n") if a.interview_schedule and a.interview_schedule.student_proposed_slots else [],
                "notes": a.interview_schedule.notes if a.interview_schedule else None,
            } if a.interview_schedule else None,
        } for a in applications])

    @app.route("/api/student/profile", methods=["GET", "PUT"])
    @jwt_required()
    @role_required("student")
    def edit_profile(current_user):
        student = StudentProfile.query.filter_by(user_id=current_user.id).first()
        if request.method == "GET":
            return jsonify({
                "name": current_user.name,
                "email": current_user.email,
                "branch": student.branch,
                "year": student.year,
                "cgpa": student.cgpa,
                "resume_url": student.resume_url,
            })

        data = request.json or {}
        current_user.name = data.get("name", current_user.name)
        student.branch = data.get("branch", student.branch)
        student.year = data.get("year", student.year)
        student.cgpa = float(data.get("cgpa", student.cgpa))
        student.resume_url = data.get("resume_url", student.resume_url)
        db.session.commit()
        return jsonify({"message": "Profile updated successfully"})

    @app.route("/api/student/export-applications", methods=["POST"])
    @jwt_required()
    @role_required("student")
    def export_applications(current_user):
        from tasks import celery, export_application_history

        student = StudentProfile.query.filter_by(user_id=current_user.id).first()
        if not student:
            return jsonify({"message": "Student profile not found"}), 404

        try:
            result = celery.send_task("tasks.export_application_history", args=[student.id])
            return jsonify({"message": "Your export has been queued. You will receive an email when it is ready.", "task_id": result.id})
        except Exception as exc:
            # Fallback when Celery/Redis is unavailable
            export_application_history(student.id)
            return jsonify({"message": "Redis unavailable. Export generated synchronously.", "task_id": None})

    @app.route("/api/student/download-applications", methods=["GET"])
    @jwt_required()
    @role_required("student")
    def download_applications(current_user):
        student = StudentProfile.query.filter_by(user_id=current_user.id).first()
        if not student:
            return jsonify({"message": "Student profile not found"}), 404

        filename = f"student_{student.id}_applications.csv"
        filepath = os.path.join(os.path.dirname(__file__), filename)
        if not os.path.exists(filepath):
            return jsonify({"message": "Export is not ready yet. Please queue an export first."}), 404

        return send_file(filepath, as_attachment=True, mimetype="text/csv")

    @app.route("/api/drives/approved", methods=["GET"])
    @cache.cached(timeout=120, query_string=True)
    def approved_drives():
        drives = PlacementDrive.query.filter_by(status="Approved").order_by(PlacementDrive.application_deadline.asc()).all()
        return jsonify([{
            "id": d.id,
            "title": d.title,
            "company_name": d.company.company_name,
            "deadline": d.application_deadline.isoformat(),
        } for d in drives])

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5001, debug=False, use_reloader=False)
