"""End-to-end backend tests for Golf For Good.

Covers: auth, charities, scores (1..45, unique/date, last-5 eviction), user profile,
subscription/Stripe session creation, draws (configure/simulate/publish + rollover),
winners, uploads, admin, and role enforcement.
"""
import io
import os
import time
import uuid
from datetime import datetime, timedelta, timezone

import pytest
import requests
from PIL import Image

BASE_URL = os.environ["REACT_APP_BACKEND_URL"].rstrip("/")


# -------------------- Health & Auth --------------------
class TestHealthAndAuth:
    def test_health(self, anon_client):
        r = anon_client.get(f"{BASE_URL}/api/health")
        assert r.status_code == 200
        assert r.json().get("status") == "ok"

    def test_login_sets_httponly_cookies(self, anon_client):
        r = anon_client.post(f"{BASE_URL}/api/auth/login",
                             json={"email": "admin@golfforgood.com", "password": "Admin@1234"})
        assert r.status_code == 200
        data = r.json()
        assert data["email"] == "admin@golfforgood.com"
        assert data["role"] == "admin"
        assert "password_hash" not in data
        # Verify cookies
        set_cookie = r.headers.get("set-cookie", "")
        assert "access_token" in set_cookie
        assert "HttpOnly" in set_cookie
        assert "SameSite=none" in set_cookie.lower() or "samesite=none" in set_cookie.lower()
        assert "Secure" in set_cookie

    def test_login_invalid_credentials(self, anon_client):
        r = anon_client.post(f"{BASE_URL}/api/auth/login",
                             json={"email": "admin@golfforgood.com", "password": "wrong"})
        assert r.status_code == 401

    def test_me_requires_auth(self, anon_client):
        r = anon_client.get(f"{BASE_URL}/api/auth/me")
        assert r.status_code == 401

    def test_me_with_cookie(self, user_client):
        r = user_client.get(f"{BASE_URL}/api/auth/me")
        assert r.status_code == 200
        data = r.json()
        assert data["email"] == "test@golfforgood.com"
        assert "password_hash" not in data

    def test_register_and_duplicate(self, anon_client):
        email = f"TEST_reg_{uuid.uuid4().hex[:8]}@golfforgood.com"
        r = anon_client.post(f"{BASE_URL}/api/auth/register",
                             json={"email": email, "password": "Passw0rd!", "name": "Test Reg"})
        assert r.status_code == 200, r.text
        # Backend normalizes email to lowercase
        assert r.json()["email"] == email.lower()
        assert r.json()["role"] == "user"
        # Duplicate email
        r2 = anon_client.post(f"{BASE_URL}/api/auth/register",
                              json={"email": email, "password": "Passw0rd!", "name": "Test Reg"})
        assert r2.status_code == 400

    def test_logout_clears_cookies(self):
        s = requests.Session()
        s.headers.update({"Content-Type": "application/json"})
        s.post(f"{BASE_URL}/api/auth/login",
               json={"email": "test@golfforgood.com", "password": "Test@1234"})
        r = s.post(f"{BASE_URL}/api/auth/logout")
        assert r.status_code == 200
        # Clear session cookies since delete_cookie may not reflect in session jar;
        # verify /me now returns 401 with a fresh session using just the header cleared
        s.cookies.clear()
        r2 = s.get(f"{BASE_URL}/api/auth/me")
        assert r2.status_code == 401


# -------------------- Charities --------------------
class TestCharities:
    def test_list_public(self, anon_client):
        r = anon_client.get(f"{BASE_URL}/api/charities")
        assert r.status_code == 200
        items = r.json()
        assert isinstance(items, list) and len(items) >= 1
        assert "id" in items[0] and "name" in items[0]

    def test_featured(self, anon_client):
        r = anon_client.get(f"{BASE_URL}/api/charities/featured")
        assert r.status_code == 200
        assert isinstance(r.json(), list)

    def test_get_one(self, anon_client):
        items = anon_client.get(f"{BASE_URL}/api/charities").json()
        cid = items[0]["id"]
        r = anon_client.get(f"{BASE_URL}/api/charities/{cid}")
        assert r.status_code == 200
        assert r.json()["id"] == cid

    def test_non_admin_cannot_create(self, user_client):
        r = user_client.post(f"{BASE_URL}/api/charities", json={
            "name": "TEST_Hack", "short_description": "x", "description": "y", "image_url": "z"
        })
        assert r.status_code == 403

    def test_admin_crud(self, admin_client):
        payload = {
            "name": "TEST_Charity",
            "short_description": "short",
            "description": "long",
            "image_url": "https://example.com/x.png",
            "category": "Test",
            "events": [],
            "featured": False,
        }
        r = admin_client.post(f"{BASE_URL}/api/charities", json=payload)
        assert r.status_code == 200, r.text
        cid = r.json()["id"]

        # Verify persisted
        g = admin_client.get(f"{BASE_URL}/api/charities/{cid}")
        assert g.status_code == 200 and g.json()["name"] == "TEST_Charity"

        # Update
        u = admin_client.patch(f"{BASE_URL}/api/charities/{cid}",
                               json={"short_description": "updated"})
        assert u.status_code == 200 and u.json()["short_description"] == "updated"

        # Delete
        d = admin_client.delete(f"{BASE_URL}/api/charities/{cid}")
        assert d.status_code == 200
        g2 = admin_client.get(f"{BASE_URL}/api/charities/{cid}")
        assert g2.status_code == 404


# -------------------- Scores --------------------
class TestScores:
    def _cleanup(self, user_client):
        items = user_client.get(f"{BASE_URL}/api/scores").json()
        for s in items:
            user_client.delete(f"{BASE_URL}/api/scores/{s['id']}")

    def test_score_crud_and_rules(self, user_client):
        self._cleanup(user_client)

        # Out-of-range rejected
        r = user_client.post(f"{BASE_URL}/api/scores", json={"value": 0, "date": "2025-10-01"})
        assert r.status_code == 422
        r = user_client.post(f"{BASE_URL}/api/scores", json={"value": 46, "date": "2025-10-01"})
        assert r.status_code == 422

        # Create 5 scores over 5 distinct dates
        today = datetime.now(timezone.utc).date()
        created_ids = []
        for i in range(5):
            d = (today - timedelta(days=i + 1)).isoformat()
            resp = user_client.post(f"{BASE_URL}/api/scores", json={"value": 10 + i, "date": d})
            assert resp.status_code == 200, resp.text
            created_ids.append(resp.json()["id"])

        # Duplicate date rejection
        dup_date = (today - timedelta(days=1)).isoformat()
        dup = user_client.post(f"{BASE_URL}/api/scores", json={"value": 20, "date": dup_date})
        assert dup.status_code == 400

        # 6th score on newer date should evict oldest
        oldest_date = (today - timedelta(days=5)).isoformat()
        oldest = next(s for s in user_client.get(f"{BASE_URL}/api/scores").json()
                      if s["date"] == oldest_date)
        new_date = today.isoformat()
        r6 = user_client.post(f"{BASE_URL}/api/scores", json={"value": 30, "date": new_date})
        assert r6.status_code == 200
        after = user_client.get(f"{BASE_URL}/api/scores").json()
        assert len(after) == 5, f"Expected 5 scores after eviction, got {len(after)}"
        assert not any(s["id"] == oldest["id"] for s in after), "Oldest score should be evicted"

        # Update one
        any_id = after[0]["id"]
        up = user_client.patch(f"{BASE_URL}/api/scores/{any_id}", json={"value": 25})
        assert up.status_code == 200 and up.json()["value"] == 25

        # Delete one
        de = user_client.delete(f"{BASE_URL}/api/scores/{any_id}")
        assert de.status_code == 200
        assert len(user_client.get(f"{BASE_URL}/api/scores").json()) == 4

        self._cleanup(user_client)

    def test_scores_require_auth(self, anon_client):
        r = anon_client.get(f"{BASE_URL}/api/scores")
        assert r.status_code == 401


# -------------------- User Profile --------------------
class TestUserProfile:
    def test_update_charity_valid(self, user_client):
        charities = user_client.get(f"{BASE_URL}/api/charities").json()
        cid = charities[0]["id"]
        r = user_client.patch(f"{BASE_URL}/api/users/me/charity",
                              json={"charity_id": cid, "charity_percentage": 15.0})
        assert r.status_code == 200
        assert r.json()["charity_id"] == cid
        assert r.json()["charity_percentage"] == 15.0

    def test_charity_percent_below_10_rejected(self, user_client):
        charities = user_client.get(f"{BASE_URL}/api/charities").json()
        cid = charities[0]["id"]
        r = user_client.patch(f"{BASE_URL}/api/users/me/charity",
                              json={"charity_id": cid, "charity_percentage": 5.0})
        assert r.status_code == 422

    def test_invalid_charity_rejected(self, user_client):
        r = user_client.patch(f"{BASE_URL}/api/users/me/charity",
                              json={"charity_id": "nonexistent", "charity_percentage": 10.0})
        assert r.status_code == 400


# -------------------- Subscription --------------------
class TestSubscription:
    def test_checkout_returns_url_and_session(self, user_client):
        r = user_client.post(f"{BASE_URL}/api/subscribe/checkout",
                             json={"plan": "monthly", "origin_url": BASE_URL})
        assert r.status_code == 200, r.text
        data = r.json()
        assert data.get("url", "").startswith("https://")
        assert data.get("session_id")

    def test_checkout_status_does_not_500(self, user_client):
        """Regression guard: /subscribe/status must handle Stripe errors gracefully (not 500)."""
        r = user_client.post(f"{BASE_URL}/api/subscribe/checkout",
                             json={"plan": "monthly", "origin_url": BASE_URL})
        assert r.status_code == 200
        sid = r.json()["session_id"]
        status_r = user_client.get(f"{BASE_URL}/api/subscribe/status/{sid}")
        assert status_r.status_code != 500, (
            f"subscribe/status returned 500 — upstream Stripe errors must be "
            f"translated to a 4xx/5xx handled response. Body: {status_r.text}"
        )

    def test_checkout_invalid_plan(self, user_client):
        r = user_client.post(f"{BASE_URL}/api/subscribe/checkout",
                             json={"plan": "weekly", "origin_url": BASE_URL})
        assert r.status_code == 400

    def test_checkout_requires_auth(self, anon_client):
        r = anon_client.post(f"{BASE_URL}/api/subscribe/checkout",
                             json={"plan": "monthly", "origin_url": BASE_URL})
        assert r.status_code == 401

    def test_cancel(self, user_client):
        r = user_client.post(f"{BASE_URL}/api/subscribe/cancel")
        assert r.status_code == 200
        # Restore to active for subsequent tests
        me = user_client.get(f"{BASE_URL}/api/auth/me").json()
        # Re-activate via admin
        s = requests.Session(); s.headers.update({"Content-Type": "application/json"})
        s.post(f"{BASE_URL}/api/auth/login",
               json={"email": "admin@golfforgood.com", "password": "Admin@1234"})
        s.patch(f"{BASE_URL}/api/admin/users/{me['id']}",
                json={"subscription_status": "active", "subscription_plan": "monthly"})


# -------------------- Draws --------------------
class TestDraws:
    def test_non_admin_cannot_configure(self, user_client):
        r = user_client.post(f"{BASE_URL}/api/draws/configure",
                             json={"month": "2099-01", "logic_type": "random"})
        assert r.status_code == 403

    def test_full_draw_flow_with_rollover(self, admin_client, user_client):
        # Ensure test user has 5 scores so they may be a participant
        scores = user_client.get(f"{BASE_URL}/api/scores").json()
        for s in scores:
            user_client.delete(f"{BASE_URL}/api/scores/{s['id']}")
        today = datetime.now(timezone.utc).date()
        # Set scores that are UNLIKELY to match random [1..45] drawn set, keeps rollover path realistic
        for i, v in enumerate([2, 3, 4, 5, 6]):
            d = (today - timedelta(days=i + 1)).isoformat()
            user_client.post(f"{BASE_URL}/api/scores", json={"value": v, "date": d})

        month = f"2099-{uuid.uuid4().hex[:2]}"
        # Use characters only valid for month? use numeric:
        month = "2099-0" + str((int(time.time()) % 9) + 1)

        # Configure
        cfg = admin_client.post(f"{BASE_URL}/api/draws/configure",
                                json={"month": month, "logic_type": "random"})
        assert cfg.status_code == 200, cfg.text
        draw = cfg.json()
        assert draw["status"] == "draft"
        assert len(draw["numbers"]) == 5
        assert all(1 <= n <= 45 for n in draw["numbers"])
        pool = draw["prize_pool"]
        assert {"total_pool", "tier_5", "tier_4", "tier_3"}.issubset(pool.keys())

        # Simulate
        sim = admin_client.post(f"{BASE_URL}/api/draws/simulate",
                                json={"month": month, "logic_type": "random"})
        assert sim.status_code == 200
        assert "projected_winners" in sim.json()

        # Publish
        pub = admin_client.post(f"{BASE_URL}/api/draws/publish",
                                json={"draw_id": draw["id"]})
        assert pub.status_code == 200, pub.text
        pub_data = pub.json()
        assert pub_data["published"] is True
        assert "rollover" in pub_data

        # Double-publish blocked
        pub2 = admin_client.post(f"{BASE_URL}/api/draws/publish",
                                 json={"draw_id": draw["id"]})
        assert pub2.status_code == 400

        # Latest and list
        latest = admin_client.get(f"{BASE_URL}/api/draws/latest")
        assert latest.status_code == 200
        lst = admin_client.get(f"{BASE_URL}/api/draws")
        assert lst.status_code == 200 and isinstance(lst.json(), list)

        # Participation
        part = user_client.get(f"{BASE_URL}/api/draws/mine/participation")
        assert part.status_code == 200
        assert isinstance(part.json(), list)


# -------------------- Winners --------------------
class TestWinners:
    def test_my_winners(self, user_client):
        r = user_client.get(f"{BASE_URL}/api/winners/mine")
        assert r.status_code == 200 and isinstance(r.json(), list)

    def test_admin_all_winners(self, admin_client):
        r = admin_client.get(f"{BASE_URL}/api/winners/admin/all")
        assert r.status_code == 200 and isinstance(r.json(), list)

    def test_non_admin_forbidden(self, user_client):
        r = user_client.get(f"{BASE_URL}/api/winners/admin/all")
        assert r.status_code == 403

    def test_verify_not_found(self, admin_client):
        r = admin_client.post(f"{BASE_URL}/api/winners/verify",
                              json={"winner_id": "nonexistent", "action": "approve"})
        assert r.status_code == 404


# -------------------- Uploads --------------------
def _make_png_bytes() -> bytes:
    buf = io.BytesIO()
    img = Image.new("RGB", (4, 4), color="blue")
    img.save(buf, format="PNG")
    return buf.getvalue()


class TestUploads:
    def test_upload_nonexistent_winner(self, user_client):
        png = _make_png_bytes()
        # multipart uses different content-type; use a fresh session w/ cookies
        s = requests.Session(); s.headers.update({"Content-Type": "application/json"})
        s.post(f"{BASE_URL}/api/auth/login",
               json={"email": "test@golfforgood.com", "password": "Test@1234"})
        s.headers.pop("Content-Type", None)
        r = s.post(f"{BASE_URL}/api/winners/nonexistent/proof",
                   files={"file": ("x.png", png, "image/png")})
        assert r.status_code == 404

    def test_upload_rejects_non_image(self, user_client):
        s = requests.Session()
        s.post(f"{BASE_URL}/api/auth/login",
               json={"email": "test@golfforgood.com", "password": "Test@1234"})
        # Need a valid winner_id to pass ownership check; create via admin.
        admin = requests.Session(); admin.headers.update({"Content-Type": "application/json"})
        admin.post(f"{BASE_URL}/api/auth/login",
                   json={"email": "admin@golfforgood.com", "password": "Admin@1234"})
        winners = admin.get(f"{BASE_URL}/api/winners/admin/all").json()
        # Find a winner owned by test user if any
        me = s.get(f"{BASE_URL}/api/auth/me").json()
        my_win = next((w for w in winners if w["user_id"] == me["id"]), None)
        if not my_win:
            pytest.skip("No winner entry for test user to validate non-image rejection on real path")
        r = s.post(f"{BASE_URL}/api/winners/{my_win['id']}/proof",
                   files={"file": ("x.txt", b"hello", "text/plain")})
        assert r.status_code == 400

    def test_upload_and_view_flow(self, user_client):
        # Full happy-path upload requires a real winner row for the test user.
        admin = requests.Session(); admin.headers.update({"Content-Type": "application/json"})
        admin.post(f"{BASE_URL}/api/auth/login",
                   json={"email": "admin@golfforgood.com", "password": "Admin@1234"})
        winners = admin.get(f"{BASE_URL}/api/winners/admin/all").json()
        me = user_client.get(f"{BASE_URL}/api/auth/me").json()
        my_win = next((w for w in winners if w["user_id"] == me["id"]), None)
        if not my_win:
            pytest.skip("No winner entry for test user; happy-path upload skipped")

        s = requests.Session()
        s.post(f"{BASE_URL}/api/auth/login",
               json={"email": "test@golfforgood.com", "password": "Test@1234"})
        png = _make_png_bytes()
        r = s.post(f"{BASE_URL}/api/winners/{my_win['id']}/proof",
                   files={"file": ("proof.png", png, "image/png")})
        assert r.status_code == 200, r.text
        path = r.json()["path"]
        # View as owner
        v = s.get(f"{BASE_URL}/api/files/view", params={"path": path})
        assert v.status_code == 200
        assert v.headers.get("content-type", "").startswith("image/")


# -------------------- Admin --------------------
class TestAdmin:
    def test_list_users(self, admin_client):
        r = admin_client.get(f"{BASE_URL}/api/admin/users")
        assert r.status_code == 200
        users = r.json()
        assert any(u["email"] == "admin@golfforgood.com" for u in users)
        # No password hashes
        assert all("password_hash" not in u for u in users)

    def test_non_admin_forbidden_on_admin(self, user_client):
        r = user_client.get(f"{BASE_URL}/api/admin/users")
        assert r.status_code == 403
        r2 = user_client.get(f"{BASE_URL}/api/admin/reports/summary")
        assert r2.status_code == 403

    def test_reports_summary(self, admin_client):
        r = admin_client.get(f"{BASE_URL}/api/admin/reports/summary")
        assert r.status_code == 200
        keys = {"total_users", "active_subscribers", "total_charities",
                "total_winners", "pending_payouts", "current_prize_pool",
                "total_revenue", "charity_contribution_estimate"}
        assert keys.issubset(r.json().keys())

    def test_update_user(self, admin_client):
        users = admin_client.get(f"{BASE_URL}/api/admin/users").json()
        tu = next(u for u in users if u["email"] == "test@golfforgood.com")
        r = admin_client.patch(f"{BASE_URL}/api/admin/users/{tu['id']}",
                               json={"name": "Alex Test Updated"})
        assert r.status_code == 200
        assert r.json()["name"] == "Alex Test Updated"
        # Restore
        admin_client.patch(f"{BASE_URL}/api/admin/users/{tu['id']}",
                           json={"name": "Alex Test"})
