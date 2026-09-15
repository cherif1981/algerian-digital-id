"""
Flask UI for Algerian Digital ID.

- يعمل مع Python 3.7
- Flask 2.2.5
- Jinja loader مزدوج (templates/ + templates/pages/)
- يستخدم نفس طبقة الأعمال (app.core.*)
"""

from __future__ import annotations

import os
from datetime import datetime
from functools import wraps
from typing import Optional

from flask import (
    Flask,
    current_app,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from flask_wtf import FlaskForm
from jinja2 import ChoiceLoader, FileSystemLoader
from wtforms import PasswordField, StringField, SubmitField
from wtforms.validators import DataRequired, Email


# ============================================================
# Paths — مسارات مطلقة
# ============================================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")
PAGES_DIR = os.path.join(TEMPLATES_DIR, "pages")
STATIC_DIR = os.path.join(BASE_DIR, "static")


# ============================================================
# Config
# ============================================================
SECRET_KEY = os.environ.get("FLASK_SECRET_KEY", "dev-secret-change-me")


# ============================================================
# Forms
# ============================================================
class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Login")


# ============================================================
# Helpers
# ============================================================
def login_required(view):
    """Decorator: redirect to /login if no session."""
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("user_id"):
            flash("Please log in first.", "warning")
            return redirect(url_for("login", next=request.path))
        return view(*args, **kwargs)
    return wrapped


def get_current_user():
    """Return current user dict from session (demo purpose)."""
    if not session.get("user_id"):
        return None
    return {
        "id": session.get("user_id"),
        "email": session.get("email"),
        "roles": session.get("roles", []),
        "scopes": session.get("scopes", []),
    }


# ============================================================
# App factory
# ============================================================
def create_app():
    app = Flask(
        __name__,
        template_folder=TEMPLATES_DIR,
        static_folder=STATIC_DIR,
        static_url_path="/static",
    )

    # --------------------------------------------------------
    # Jinja loader مزدوج:
    # يبحث في templates/ ثم templates/pages/
    # --------------------------------------------------------
    app.jinja_loader = ChoiceLoader([
        FileSystemLoader(TEMPLATES_DIR),
        FileSystemLoader(PAGES_DIR),
    ])

    app.config.update(
        SECRET_KEY=SECRET_KEY,
        WTF_CSRF_ENABLED=True,
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
        # 👇 مهم جداً للتطوير
        TEMPLATES_AUTO_RELOAD=True,
        SEND_FILE_MAX_AGE_DEFAULT=0,
    )

    # ========================================================
    # Context processor
    # ========================================================
    @app.context_processor
    def inject_globals():
        return {
            "current_user": get_current_user(),
            "current_year": datetime.now().year,
        }

    # ========================================================
    # Debug routes
    # ========================================================
    @app.route("/_debug/static")
    def _debug_static():
        """فحص مسار الملفات الثابتة والقوالب."""
        sf = current_app.static_folder
        tf = current_app.template_folder
        return jsonify({
            "static_folder": sf,
            "static_exists": os.path.isdir(sf) if sf else False,
            "static_files": os.listdir(sf) if sf and os.path.isdir(sf) else [],
            "css_exists": os.path.isfile(os.path.join(sf, "style.css")) if sf else False,
            "css_url": url_for("static", filename="style.css"),
            "templates_folder": tf,
            "templates_exists": os.path.isdir(tf) if tf else False,
            "pages_folder": PAGES_DIR,
            "pages_exists": os.path.isdir(PAGES_DIR),
            "pages_files": os.listdir(PAGES_DIR) if os.path.isdir(PAGES_DIR) else [],
        })

    @app.route("/_debug/templates")
    def _debug_templates():
        """فحص جميع القوالب المتاحة."""
        results = {}
        for name in [
            "base.html",
            "index.html",
            "login.html",
            "dashboard.html",
            "sessions.html",
            "enroll.html",
            "pages/index.html",
            "pages/login.html",
            "pages/dashboard.html",
            "pages/sessions.html",
            "pages/enroll.html",
            "partials/head.html",
            "partials/topbar.html",
            "partials/flashes.html",
            "partials/footer.html",
            "partials/scripts.html",
        ]:
            try:
                current_app.jinja_env.get_template(name)
                results[name] = "OK"
            except Exception as e:
                results[name] = "MISSING: " + str(e)
        return jsonify(results)

    # ========================================================
    # Main routes
    # ========================================================
    @app.route("/")
    def index():
        return render_template("index.html")

    @app.route("/login", methods=["GET", "POST"])
    def login():
        form = LoginForm()
        if form.validate_on_submit():
            # ⚠️ Demo فقط — استبدل بالتحقق الحقيقي
            if form.email.data == "admin@example.com" and form.password.data == "admin":
                session["user_id"] = "demo-user-1"
                session["email"] = form.email.data
                session["roles"] = ["admin"]
                session["scopes"] = ["read", "write", "credential:issue"]
                flash("Welcome back!", "success")
                next_url = request.args.get("next") or url_for("dashboard")
                return redirect(next_url)
            else:
                flash("Invalid credentials. Try admin@example.com / admin", "danger")
        return render_template("login.html", form=form)

    @app.route("/logout")
    def logout():
        session.clear()
        flash("Logged out.", "info")
        return redirect(url_for("index"))

    @app.route("/dashboard")
    @login_required
    def dashboard():
        stats = {
            "users_total": 128,
            "credentials_issued": 342,
            "verifications_today": 57,
            "failed_logins_today": 3,
        }
        recent_events = [
            {"time": "10:23", "event": "Credential issued", "user": "user_12"},
            {"time": "10:15", "event": "Login success", "user": "user_45"},
            {"time": "09:58", "event": "Refresh reuse detected", "user": "user_09"},
            {"time": "09:42", "event": "Credential verified", "user": "user_23"},
        ]
        return render_template("dashboard.html", stats=stats, events=recent_events)

    @app.route("/sessions")
    @login_required
    def sessions_list():
        demo_sessions = [
            {
                "id": "jti-a1b2",
                "device": "Chrome / Windows",
                "ip": "192.168.1.10",
                "created": "2026-09-15 09:00",
            },
            {
                "id": "jti-c3d4",
                "device": "Firefox / Linux",
                "ip": "10.0.0.5",
                "created": "2026-09-14 22:11",
            },
        ]
        return render_template("sessions.html", sessions=demo_sessions)

    # ========================================================
    # Enrollment / NFC reader
    # ========================================================
    @app.route("/enroll")
    @login_required
    def enroll_page():
        return render_template("enroll.html")

    @app.route("/api/enrollment/reader-opened", methods=["POST"])
    @login_required
    def enrollment_reader_opened():
        """يسجّل فتح المستخدم لبوابة القراءة الرسمية."""
        data = request.get_json(silent=True) or {}
        # TODO: اربطه بـ audit log حقيقي
        return jsonify({
            "status": "ok",
            "received_at": datetime.utcnow().isoformat(),
            "client_ts": data.get("ts"),
        })

    # ========================================================
    # Health
    # ========================================================
    @app.route("/health")
    def health():
        return jsonify({
            "status": "ok",
            "time": datetime.utcnow().isoformat(),
        })

    # ========================================================
    # Error handlers
    # ========================================================
    @app.errorhandler(404)
    def not_found(e):
        return render_template("base.html", error="404 — Not Found"), 404

    @app.errorhandler(500)
    def server_error(e):
        return render_template("base.html", error="500 — Server Error"), 500

    return app