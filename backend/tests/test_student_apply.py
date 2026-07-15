import os
import unittest

os.environ.setdefault("SQLALCHEMY_DATABASE_URI", "sqlite:///:memory:")

from datetime import date

from app import create_app
from models import Application, CompanyProfile, PlacementDrive, StudentProfile, User, db


class StudentApplyTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config.update(TESTING=True)
        self.client = self.app.test_client()

        with self.app.app_context():
            db.drop_all()
            db.create_all()

            company_user = User(name="Contoso", email="company@example.com", role="company", is_active=True)
            company_user.set_password("Password123")
            db.session.add(company_user)
            db.session.flush()

            company_profile = CompanyProfile(
                user_id=company_user.id,
                company_name="Contoso",
                hr_contact="1234567890",
                approved=True,
            )
            db.session.add(company_profile)
            db.session.flush()

            student_user = User(name="Asha", email="student@example.com", role="student", is_active=True)
            student_user.set_password("Password123")
            db.session.add(student_user)
            db.session.flush()

            student_profile = StudentProfile(
                user_id=student_user.id,
                branch="CSE",
                year="3rd Year",
                cgpa=8.5,
            )
            db.session.add(student_profile)

            drive = PlacementDrive(
                company_id=company_profile.id,
                title="SDE Intern",
                branch_eligibility="All Branches",
                year_eligibility="3rd Year",
                min_cgpa=7.0,
                application_deadline=date(2099, 12, 31),
                status="Approved",
            )
            db.session.add(drive)
            db.session.commit()

            self.drive_id = drive.id

    def test_apply_allows_students_when_eligibility_is_broad(self):
        login_response = self.client.post(
            "/api/auth/login",
            json={"email": "student@example.com", "password": "Password123"},
        )
        self.assertEqual(login_response.status_code, 200)
        token = login_response.get_json()["access_token"]

        apply_response = self.client.post(
            "/api/student/apply",
            json={"drive_id": self.drive_id},
            headers={"Authorization": f"Bearer {token}"},
        )

        self.assertEqual(apply_response.status_code, 200)
        with self.app.app_context():
            self.assertEqual(Application.query.count(), 1)


if __name__ == "__main__":
    unittest.main()
