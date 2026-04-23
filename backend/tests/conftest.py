"""Pytest fixtures for Golf For Good backend tests."""
import os
import pytest
import requests
from pathlib import Path
from dotenv import load_dotenv

# Load frontend .env to get public backend URL
load_dotenv(Path("/app/frontend/.env"))

BASE_URL = os.environ["REACT_APP_BACKEND_URL"].rstrip("/")

ADMIN_EMAIL = "admin@golfforgood.com"
ADMIN_PASSWORD = "Admin@1234"
TEST_EMAIL = "test@golfforgood.com"
TEST_PASSWORD = "Test@1234"


@pytest.fixture(scope="session")
def base_url():
    return BASE_URL


def _make_session():
    s = requests.Session()
    s.headers.update({"Content-Type": "application/json"})
    return s


@pytest.fixture(scope="session")
def admin_client():
    s = _make_session()
    r = s.post(f"{BASE_URL}/api/auth/login", json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD})
    assert r.status_code == 200, f"Admin login failed: {r.status_code} {r.text}"
    return s


@pytest.fixture(scope="session")
def user_client():
    s = _make_session()
    r = s.post(f"{BASE_URL}/api/auth/login", json={"email": TEST_EMAIL, "password": TEST_PASSWORD})
    assert r.status_code == 200, f"Test user login failed: {r.status_code} {r.text}"
    return s


@pytest.fixture
def anon_client():
    return _make_session()
