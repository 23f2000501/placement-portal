import csv
import json
import os
import urllib.request
import urllib.error
from datetime import date, timedelta

from celery import Celery
from celery.schedules import crontab
from flask_mail import Mail, Message

from app import create_app
from config import Config
from models import Application, PlacementDrive, StudentProfile, User

celery = Celery(__name__, broker=Config.REDIS_URL, backend=Config.REDIS_URL)
celery.conf.update(
    result_backend=Config.REDIS_URL,
    timezone=Config.CELERY_TIMEZONE,
    enable_utc=False,
    beat_schedule={
        "daily-deadline-reminder": {
            "task": "tasks.daily_deadline_reminder",
            "schedule": crontab(hour=Config.DAILY_REMINDER_HOUR, minute=Config.DAILY_REMINDER_MINUTE),
        },
        "monthly-placement-report": {
            "task": "tasks.monthly_report",
            "schedule": crontab(day_of_month="1", hour=Config.MONTHLY_REPORT_HOUR, minute=Config.MONTHLY_REPORT_MINUTE),
        },
    },
)
app = create_app()
mail = Mail(app)


def send_chat_webhook(text):
    if not Config.CHAT_WEBHOOK_URL:
        return {"status": "chat webhook missing"}
    payload = json.dumps({"text": text}).encode("utf-8")
    request = urllib.request.Request(
        Config.CHAT_WEBHOOK_URL,
        data=payload,
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(request, timeout=10) as response:
            return {"status": "sent", "code": response.getcode()}
    except urllib.error.URLError as exc:
        return {"status": "failed", "error": str(exc)}


def create_message(subject, recipients, body="", html=None, attachments=None):
    sender = Config.MAIL_DEFAULT_SENDER or Config.MAIL_USERNAME
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = body
    if html:
        msg.html = html
    if attachments:
        for filename, mime_type, content in attachments:
            msg.attach(filename, mime_type, content)
    return msg


@celery.task
def send_email(subject, recipients, body, html=None):
    with app.app_context():
        if not Config.MAIL_USERNAME or not Config.MAIL_PASSWORD:
            return {"status": "mail configuration missing"}
        msg = create_message(subject, recipients, body, html)
        mail.send(msg)
        return {"status": "sent"}


@celery.task
def daily_deadline_reminder():
    with app.app_context():
        tomorrow = date.today() + timedelta(days=1)
        drives = PlacementDrive.query.filter(
            PlacementDrive.application_deadline == tomorrow,
            PlacementDrive.status == "Approved",
        ).all()
        students = StudentProfile.query.all()
        recipients = [student.user.email for student in students]
        if not recipients:
            return {"status": "no students"}

        if not drives:
            body = "No placement drive deadlines are due tomorrow."
        else:
            drive_list = "\n".join([f"- {drive.title} at {drive.company.company_name} (deadline: {drive.application_deadline.isoformat()})" for drive in drives])
            body = f"Reminder: {len(drives)} drive(s) have deadlines tomorrow.\n\n{drive_list}"

        send_email.delay("Placement Drive Deadline Reminder", recipients, body)
        webhook_result = send_chat_webhook(f"Placement reminder: {len(drives)} drive(s) have deadlines tomorrow.")
        return {"status": "scheduled", "webhook": webhook_result}


@celery.task
def monthly_report():
    with app.app_context():
        start = date.today().replace(day=1) - timedelta(days=1)
        start = start.replace(day=1)
        end = date.today().replace(day=1) - timedelta(days=1)

        drives = PlacementDrive.query.filter(
            PlacementDrive.created_at >= start,
            PlacementDrive.created_at <= end,
        ).all()
        applications = Application.query.filter(
            Application.application_date >= start,
            Application.application_date <= end,
        ).all()
        selected_count = Application.query.filter(
            Application.application_date >= start,
            Application.application_date <= end,
            Application.status == "Selected",
        ).count()

        html = f"""
        <h2>Placement Activity Report</h2>
        <p>Period: {start.isoformat()} to {end.isoformat()}</p>
        <ul>
            <li>Total drives created: {len(drives)}</li>
            <li>Total applications: {len(applications)}</li>
            <li>Total students selected: {selected_count}</li>
        </ul>
        """
        admin = User.query.filter_by(role="admin").first()
        if admin:
            send_email.delay("Monthly Placement Report", [admin.email], "Please view the monthly placement report.", html)
            return {"status": "scheduled", "message": "Monthly report email scheduled"}
        return {"status": "admin email missing"}


@celery.task
def export_application_history(student_id):
    with app.app_context():
        student = StudentProfile.query.get(student_id)
        if not student:
            return {"error": "student not found"}

        applications = Application.query.filter_by(student_id=student.id).order_by(Application.application_date.desc()).all()
        filename = f"student_{student_id}_applications.csv"
        filepath = os.path.join(os.path.dirname(__file__), filename)

        with open(filepath, mode="w", newline="") as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(["Student ID", "Company Name", "Drive Title", "Application Status", "Application Date"])
            for entry in applications:
                writer.writerow([
                    student.id,
                    entry.drive.company.company_name,
                    entry.drive.title,
                    entry.status,
                    entry.application_date.isoformat(),
                ])
        return {"file_path": filepath, "message": "Export completed"}