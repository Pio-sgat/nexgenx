from pathlib import Path
import os
import sqlite3
import uuid

from flask import Flask, flash, redirect, render_template, request, url_for
from werkzeug.utils import secure_filename


BASE_DIR = Path(__file__).resolve().parent
DATABASE = BASE_DIR / "nexgenx.db"
UPLOAD_FOLDER = BASE_DIR / "uploads"
ALLOWED_EXTENSIONS = {"pdf", "doc", "docx", "xls", "xlsx", "png", "jpg", "jpeg", "zip"}

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("NEXGENX_SECRET_KEY", "nexgenx-development-key")
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024


def get_db():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    return connection


def init_db():
    UPLOAD_FOLDER.mkdir(exist_ok=True)
    with get_db() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS projects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_name TEXT NOT NULL,
                category TEXT NOT NULL,
                status TEXT NOT NULL,
                description TEXT NOT NULL,
                start_date TEXT,
                budget TEXT,
                contact_email TEXT NOT NULL,
                attachment TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/")
def index():
    with get_db() as connection:
        projects = connection.execute(
            "SELECT * FROM projects ORDER BY created_at DESC"
        ).fetchall()
    return render_template("index.html", projects=projects)


@app.post("/upload")
def upload_project():
    required_fields = ["project_name", "category", "status", "description", "contact_email"]
    missing_field = next(
        (field for field in required_fields if not request.form.get(field, "").strip()),
        None,
    )
    if missing_field:
        flash("Please complete all required fields.", "error")
        return redirect(url_for("index"))

    attachment = request.files.get("attachment")
    saved_filename = None
    if attachment and attachment.filename:
        if not allowed_file(attachment.filename):
            flash("That file type is not supported.", "error")
            return redirect(url_for("index"))
        original_name = secure_filename(attachment.filename)
        saved_filename = f"{uuid.uuid4().hex}_{original_name}"
        attachment.save(UPLOAD_FOLDER / saved_filename)

    with get_db() as connection:
        connection.execute(
            """
            INSERT INTO projects
            (project_name, category, status, description, start_date, budget, contact_email, attachment)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                request.form["project_name"].strip(),
                request.form["category"],
                request.form["status"],
                request.form["description"].strip(),
                request.form.get("start_date", ""),
                request.form.get("budget", "").strip(),
                request.form["contact_email"].strip(),
                saved_filename,
            ),
        )

    flash("Project added to the public showcase.", "success")
    return redirect(url_for("index"))


@app.errorhandler(413)
def file_too_large(_error):
    flash("The attachment is too large. Please choose a file under 16 MB.", "error")
    return redirect(url_for("index"))


init_db()


if __name__ == "__main__":
    app.run(debug=True)
