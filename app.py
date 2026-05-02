from __future__ import annotations

from datetime import datetime
from pathlib import Path

from flask import Flask, flash, redirect, render_template, request, send_file, url_for

from visitor_store import VisitorStore


BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "data" / "visitors.db"

app = Flask(__name__)
app.config["SECRET_KEY"] = "visitor-management-prototype"
store = VisitorStore(DB_PATH)


@app.context_processor
def inject_now():
    return {"now": datetime.now}


@app.route("/")
def dashboard():
    stats = store.dashboard_stats()
    recent_visitors = store.list_visitors(limit=8)
    return render_template("dashboard.html", stats=stats, recent_visitors=recent_visitors)


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        payload = {
            "first_name": request.form.get("first_name", "").strip(),
            "last_name": request.form.get("last_name", "").strip(),
            "phone_number": request.form.get("phone_number", "").strip(),
            "visit_purpose": request.form.get("visit_purpose", "").strip(),
            "department": request.form.get("department", "").strip(),
            "host_name": request.form.get("host_name", "").strip(),
            "badge_number": request.form.get("badge_number", "").strip(),
            "access_level": request.form.get("access_level", "Standard").strip(),
            "is_student": 1 if request.form.get("is_student") == "on" else 0,
            "university": request.form.get("university", "").strip(),
            "id_card_number": request.form.get("id_card_number", "").strip(),
        }
        errors = validate_visitor(payload)
        if errors:
            for error in errors:
                flash(error, "error")
            return render_template("register.html", form=payload)

        visitor_id = store.add_visitor(payload)
        flash(f"Visitor #{visitor_id} registered successfully.", "success")
        return redirect(url_for("records"))

    return render_template("register.html", form={})


@app.route("/records")
def records():
    query = request.args.get("q", "").strip()
    status = request.args.get("status", "all")
    visitors = store.search_visitors(query=query, status=status)
    return render_template("records.html", visitors=visitors, query=query, status=status)


@app.route("/visitor/<int:visitor_id>/exit", methods=["POST"])
def record_exit(visitor_id: int):
    store.record_exit(visitor_id)
    flash("Exit time recorded.", "success")
    return redirect(request.referrer or url_for("records"))


@app.route("/visitor/<int:visitor_id>/badge")
def badge(visitor_id: int):
    visitor = store.get_visitor(visitor_id)
    if visitor is None:
        flash("Visitor not found.", "error")
        return redirect(url_for("records"))
    return render_template("badge.html", visitor=visitor)


@app.route("/visitor/<int:visitor_id>/delete", methods=["POST"])
def delete_visitor(visitor_id: int):
    store.delete_visitor(visitor_id)
    flash("Visitor record deleted.", "success")
    return redirect(url_for("records"))


@app.route("/reports")
def reports():
    summary = store.report_summary()
    return render_template("reports.html", **summary)


@app.route("/export.csv")
def export_csv():
    csv_path = store.export_csv(BASE_DIR / "data" / "visitor_export.csv")
    return send_file(csv_path, as_attachment=True, download_name="visitor_export.csv")


def validate_visitor(payload: dict[str, object]) -> list[str]:
    errors: list[str] = []
    required_fields = {
        "first_name": "First name",
        "last_name": "Last name",
        "visit_purpose": "Visit purpose",
        "department": "Department",
        "host_name": "Host name",
        "id_card_number": "ID card number",
    }
    for key, label in required_fields.items():
        if not str(payload.get(key, "")).strip():
            errors.append(f"{label} is required.")

    phone = str(payload.get("phone_number", "")).strip()
    if phone and not phone.replace("+", "").replace(" ", "").isdigit():
        errors.append("Phone number must contain only digits, spaces, or a leading plus sign.")

    if payload.get("is_student") and not str(payload.get("university", "")).strip():
        errors.append("University is required when the visitor is marked as a student.")

    return errors


if __name__ == "__main__":
    store.initialize()
    app.run(debug=True)
