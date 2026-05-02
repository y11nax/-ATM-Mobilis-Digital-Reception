from __future__ import annotations

from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    Image,
    PageBreak,
    Paragraph,
    Preformatted,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "Rapport3.pdf"
SCREENSHOTS = ROOT / "docs" / "screenshots"


def make_styles():
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="TitleCenter", parent=styles["Title"], alignment=TA_CENTER, fontSize=20, leading=26, spaceAfter=16))
    styles.add(ParagraphStyle(name="SubtitleCenter", parent=styles["Normal"], alignment=TA_CENTER, fontSize=12, leading=17, spaceAfter=10))
    styles.add(ParagraphStyle(name="BodyJustify", parent=styles["BodyText"], alignment=TA_JUSTIFY, fontSize=10.5, leading=15, spaceAfter=8))
    styles.add(ParagraphStyle(name="Section", parent=styles["Heading1"], fontSize=16, leading=20, spaceBefore=10, spaceAfter=8))
    styles.add(ParagraphStyle(name="SubSection", parent=styles["Heading2"], fontSize=13, leading=16, spaceBefore=8, spaceAfter=6))
    styles.add(ParagraphStyle(name="Caption", parent=styles["Italic"], alignment=TA_CENTER, fontSize=9, textColor=colors.HexColor("#4d5965")))
    return styles


def add_page_number(canvas, doc):
    canvas.saveState()
    canvas.setFont("Helvetica", 9)
    canvas.setFillColor(colors.HexColor("#4d5965"))
    canvas.drawRightString(A4[0] - 1.8 * cm, 1.2 * cm, f"Page {doc.page}")
    canvas.restoreState()


def para(text: str, styles):
    return Paragraph(text, styles["BodyJustify"])


def image_block(name: str, caption: str, styles):
    path = SCREENSHOTS / name
    if not path.exists():
        return [para(f"Screenshot placeholder: {caption}.", styles)]
    return [
        Image(str(path), width=15.8 * cm, height=8.9 * cm),
        Paragraph(caption, styles["Caption"]),
        Spacer(1, 8),
    ]


def code_excerpt(path: Path, max_lines: int = 55) -> str:
    lines = path.read_text(encoding="utf-8").splitlines()
    return "\n".join(lines[:max_lines])


def build():
    styles = make_styles()
    doc = SimpleDocTemplate(
        str(OUTPUT),
        pagesize=A4,
        rightMargin=1.8 * cm,
        leftMargin=1.8 * cm,
        topMargin=1.6 * cm,
        bottomMargin=1.8 * cm,
        title="Rapport 3 - Digital Visitor Management System",
    )
    story = []

    story += [
        Spacer(1, 4 * cm),
        Paragraph("Digital Visitor Management System", styles["TitleCenter"]),
        Paragraph("Prototype Application and Implementation Report", styles["SubtitleCenter"]),
        Paragraph("Contribution Part: Realisation", styles["SubtitleCenter"]),
        Spacer(1, 1 * cm),
        Paragraph("Prepared by:", styles["SubtitleCenter"]),
        Paragraph("Serrar Lokmane<br/>Laouar Younes<br/>Bouakaken Sif Eddine", styles["SubtitleCenter"]),
        Spacer(1, 0.5 * cm),
        Paragraph("Academic Year: 2025-2026<br/>Department of Computer Science and Software Engineering<br/>May 02, 2026", styles["SubtitleCenter"]),
        PageBreak(),
    ]

    contents = [
        ["1", "Introduction", "3"],
        ["2", "Development Tools and Environment", "4"],
        ["3", "Prototype Application Overview", "5"],
        ["4", "Database and Application Logic", "6"],
        ["5", "Application Interfaces", "7"],
        ["6", "Source Code Extracts", "10"],
        ["7", "Testing and Validation", "12"],
        ["8", "Conclusion", "13"],
    ]
    story += [
        Paragraph("Contents", styles["Section"]),
        Table(contents, colWidths=[1.2 * cm, 12 * cm, 1.2 * cm], style=TableStyle([
            ("FONT", (0, 0), (-1, -1), "Helvetica", 10),
            ("LINEBELOW", (0, 0), (-1, -1), 0.25, colors.HexColor("#d7dde4")),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
        ])),
        PageBreak(),
    ]

    story += [
        Paragraph("Abstract", styles["Section"]),
        para("This report presents the realisation phase of the Digital Visitor Management System proposed in the previous design report. The application is implemented as a Python web prototype using Flask for the presentation and application layers and SQLite for persistent storage. Its objective is to replace the manual paper-based visitor log used at the reception service with a structured digital workflow that supports registration, search, exit tracking, reporting, and export.", styles),
        para("The prototype follows the UML design defined in Rapport 2. It implements the main Visitor entity and the visitor management operations: adding a visitor, searching records, recording departures, generating statistics, and exporting data. The report also describes the tools used, presents the application interfaces, and includes representative source code extracts.", styles),
        Paragraph("1 Introduction", styles["Section"]),
        para("The first report identified the operational problem at the reception desk: visitor information is recorded manually in paper logbooks, which creates delays, weak traceability, poor data reliability, and limited reporting. The second report proposed a digital visitor management system using UML and a three-tier architecture.", styles),
        para("This third report completes the project cycle by implementing a working prototype. The application is intentionally simple and focused on the core needs of reception staff: registering visitors quickly, storing records reliably, locating visitor history, tracking current occupancy, and providing basic management indicators.", styles),
        PageBreak(),
    ]

    tool_rows = [
        ["Tool", "Role in the prototype"],
        ["Python 3", "Main programming language used to implement the application logic."],
        ["Flask", "Lightweight web framework used for routing, templates, forms, and responses."],
        ["SQLite", "Embedded relational database used to store visitor records locally."],
        ["HTML/CSS", "Presentation layer used to create the dashboard, forms, tables, and reports."],
        ["ReportLab", "Python library used to generate this PDF report."],
    ]
    story += [
        Paragraph("2 Development Tools and Environment", styles["Section"]),
        para("The prototype was developed with a small and portable Python stack. This choice makes the application easy to run on a local workstation without requiring a complex server installation.", styles),
        Table(tool_rows, colWidths=[4 * cm, 11 * cm], repeatRows=1, style=TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#172635")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#cbd4dd")),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("FONT", (0, 0), (-1, -1), "Helvetica", 9.5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
        ])),
        Paragraph("3 Prototype Application Overview", styles["Section"]),
        para("The application is organized around four main screens: a reception dashboard, a visitor registration form, a searchable records page, and a reporting page. The dashboard summarizes current activity. The registration form captures identity and visit data. The records screen supports search, filtering, exit tracking, and CSV export. The reports page provides daily and departmental statistics.", styles),
        para("The interface was designed for repeated operational use: restrained colors, compact tables, clear buttons, and stable page layouts. The goal is to help reception staff complete tasks quickly while giving administrators a direct overview of visitor activity.", styles),
        PageBreak(),
    ]

    story += [
        Paragraph("4 Database and Application Logic", styles["Section"]),
        para("The database contains one main table named visitors. Each record includes a unique identifier, visitor name, phone number, purpose, target department, entry time, optional exit time, student status, university, and ID card number. The exit time remains empty while the visitor is still inside the building.", styles),
        para("The VisitorStore class centralizes all database operations. This separation keeps SQL operations outside the route functions and follows the VisitorManager concept described in the UML model. The Flask routes call this class to add records, retrieve filtered lists, update exit times, calculate statistics, and export CSV files.", styles),
        Paragraph("5 Application Interfaces", styles["Section"]),
    ]
    story += image_block("dashboard.png", "Figure 1: Reception dashboard with current visitor indicators and recent records.", styles)
    story += image_block("register.png", "Figure 2: Visitor registration interface with identity, purpose, department, and student fields.", styles)
    story.append(PageBreak())
    story += image_block("records.png", "Figure 3: Searchable records table with visitor status and exit action.", styles)
    story += image_block("reports.png", "Figure 4: Reporting page showing daily and department-based visitor statistics.", styles)
    story += image_block("badge.png", "Figure 5: Visitor badge preview with Mobilis branding, host, access level, and entry details.", styles)
    story.append(PageBreak())

    story += [
        Paragraph("6 Source Code Extracts", styles["Section"]),
        para("The following extracts show the principal implementation elements. The complete source code is included in the project folder.", styles),
        Paragraph("6.1 Flask Routes", styles["SubSection"]),
        Preformatted(code_excerpt(ROOT / "app.py", 65), styles["Code"]),
        PageBreak(),
        Paragraph("6.2 SQLite Data Access", styles["SubSection"]),
        Preformatted(code_excerpt(ROOT / "visitor_store.py", 65), styles["Code"]),
        PageBreak(),
        Paragraph("7 Testing and Validation", styles["Section"]),
        para("The prototype was tested by launching the Flask server locally, opening each main interface, verifying that seed records were loaded, registering a new visitor, checking that the record appeared in the table, and confirming that the reporting page updated its counters from the database.", styles),
        para("Validation rules were also checked on the registration form. Required fields prevent incomplete records, phone numbers are constrained to simple numeric formats, and the university field becomes mandatory when a visitor is marked as a student. These controls reduce the risk of missing or inconsistent data compared with the manual paper log.", styles),
        Paragraph("8 Conclusion", styles["Section"]),
        para("The realised prototype demonstrates that the proposed digital visitor management system can solve the main reception problems identified during the internship: slow manual registration, lack of searchability, weak traceability, and absence of basic statistics. By using Python, Flask, and SQLite, the solution remains simple, understandable, and portable while still implementing the core workflow required by reception staff.", styles),
        para("Future improvements may include user authentication, role-based access control, badge printing, appointment pre-registration, cloud deployment, and integration with physical access control devices. Even in its current prototype form, the application provides a practical foundation for replacing the paper register with a structured digital system.", styles),
    ]

    doc.build(story, onFirstPage=add_page_number, onLaterPages=add_page_number)
    print(OUTPUT)


if __name__ == "__main__":
    build()
