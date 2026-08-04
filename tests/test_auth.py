import os
import tempfile
import unittest
from pathlib import Path


os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ["AUTO_CREATE_SCHEMA"] = "true"
os.environ["DEFAULT_ADMIN_USERNAME"] = "admin"
os.environ["DEFAULT_ADMIN_PASSWORD"] = "admin123"
os.environ["DEFAULT_ADMIN_FULL_NAME"] = "Test Administrator"
os.environ["SECRET_KEY"] = "test-secret-key"
os.environ["LOG_LEVEL"] = "CRITICAL"
os.environ["LOG_FILE"] = str(Path(tempfile.gettempdir()) / "bonyancore-tests.log")

from fastapi.testclient import TestClient

from app.core.database import Base, SessionLocal, engine
from app.schemas.auth import UserCreate
from app.services.auth_service import AuthService
from app.utils.security import verify_password
from main import app


class AuthenticationTests(unittest.TestCase):
    def setUp(self):
        Base.metadata.drop_all(bind=engine)
        self.client_context = TestClient(app)
        self.client = self.client_context.__enter__()

    def tearDown(self):
        self.client_context.__exit__(None, None, None)
        Base.metadata.drop_all(bind=engine)

    def login(self, username: str, password: str):
        return self.client.post(
            "/auth/login-page",
            data={
                "username": username,
                "password": password,
                "next_url": "/auth/users",
            },
            follow_redirects=False,
        )

    def create_user(self, username: str, password: str = "123456") -> int:
        with SessionLocal() as db:
            user = AuthService.create_user(
                db,
                UserCreate(
                    username=username,
                    password=password,
                    full_name=f"{username} user",
                ),
            )
            return user.id

    def test_browser_login_accepts_valid_credentials_and_rejects_invalid(self):
        invalid = self.login("admin", "wrong-password")
        self.assertEqual(invalid.status_code, 401)

        valid = self.login("admin", "admin123")
        self.assertEqual(valid.status_code, 303)
        self.assertEqual(valid.headers["location"], "/auth/users")
        self.assertIsNotNone(valid.cookies.get("access_token"))

    def test_user_management_requires_superuser(self):
        anonymous = self.client.get("/auth/users", follow_redirects=False)
        self.assertEqual(anonymous.status_code, 303)

        self.assertEqual(self.login("admin", "admin123").status_code, 303)
        self.assertEqual(self.client.get("/auth/users").status_code, 200)

        self.create_user("operator")
        self.assertEqual(self.login("operator", "123456").status_code, 303)
        self.assertEqual(self.client.get("/auth/users").status_code, 403)

    def test_six_character_password_and_missing_email_are_supported(self):
        self.assertEqual(self.login("admin", "admin123").status_code, 303)

        response = self.client.post(
            "/auth/register-page",
            data={
                "username": "no_email",
                "password": "123456",
                "full_name": "No Email User",
                "phone": "",
            },
            follow_redirects=False,
        )
        self.assertEqual(response.status_code, 303)

        with SessionLocal() as db:
            user = AuthService.get_by_username(db, "no_email")
            self.assertIsNotNone(user)
            self.assertIsNone(user.email)
            self.assertTrue(verify_password("123456", user.hashed_password))

    def test_unchecked_active_checkbox_deactivates_user(self):
        target_id = self.create_user("checkbox_user")
        self.assertEqual(self.login("admin", "admin123").status_code, 303)

        deactivate = self.client.post(
            f"/auth/users/{target_id}/edit",
            data={"full_name": "Checkbox User", "phone": ""},
            follow_redirects=False,
        )
        self.assertEqual(deactivate.status_code, 303)
        with SessionLocal() as db:
            self.assertFalse(AuthService.get_by_id(db, target_id).is_active)

        activate = self.client.post(
            f"/auth/users/{target_id}/edit",
            data={
                "full_name": "Checkbox User",
                "phone": "",
                "is_active": "true",
            },
            follow_redirects=False,
        )
        self.assertEqual(activate.status_code, 303)
        with SessionLocal() as db:
            self.assertTrue(AuthService.get_by_id(db, target_id).is_active)


if __name__ == "__main__":
    unittest.main()
