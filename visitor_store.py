from __future__ import annotations

import csv
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any


class VisitorStore:
    def __init__(self, db_path: Path):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.initialize()

    def connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.db_path)
        connection.row_factory = sqlite3.Row
        return connection

    def initialize(self) -> None:
        with self.connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS visitors (
                    visitor_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    first_name TEXT NOT NULL,
                    last_name TEXT NOT NULL,
                    phone_number TEXT,
                    visit_purpose TEXT NOT NULL,
                    department TEXT NOT NULL,
                    entry_time TEXT NOT NULL,
                    exit_time TEXT,
                    is_student INTEGER NOT NULL DEFAULT 0,
                    university TEXT,
                    id_card_number TEXT NOT NULL,
                    host_name TEXT,
                    badge_number TEXT,
                    access_level TEXT NOT NULL DEFAULT 'Standard'
                )
                """
            )
            self._migrate(connection)
            count = connection.execute("SELECT COUNT(*) FROM visitors").fetchone()[0]
            if count == 0:
                self._seed(connection)

    def _migrate(self, connection: sqlite3.Connection) -> None:
        columns = {row["name"] for row in connection.execute("PRAGMA table_info(visitors)")}
        migrations = {
            "host_name": "ALTER TABLE visitors ADD COLUMN host_name TEXT",
            "badge_number": "ALTER TABLE visitors ADD COLUMN badge_number TEXT",
            "access_level": "ALTER TABLE visitors ADD COLUMN access_level TEXT NOT NULL DEFAULT 'Standard'",
        }
        for column, sql in migrations.items():
            if column not in columns:
                connection.execute(sql)

    def _seed(self, connection: sqlite3.Connection) -> None:
        now = datetime.now()
        seed_rows = [
            ("Amine", "Belaid", "+213 550 100 100", "Technical meeting", "IT Systems", now - timedelta(hours=3), None, 0, "", "ID-1001", "N. Rahmani", "MOB-001", "Technical"),
            ("Nour", "Kadi", "+213 661 234 987", "Internship interview", "Human Resources", now - timedelta(days=1, hours=2), now - timedelta(days=1, hours=1), 1, "USTHB", "ID-1002", "S. Benali", "MOB-002", "Standard"),
            ("Samir", "Mansouri", "+213 770 808 111", "Supplier delivery", "General Affairs", now - timedelta(days=2, hours=4), now - timedelta(days=2, hours=3), 0, "", "ID-1003", "A. Haddad", "MOB-003", "Logistics"),
            ("Lina", "Aribi", "+213 555 909 202", "Administrative request", "Finance", now - timedelta(days=3), None, 1, "University of Algiers", "ID-1004", "M. Cherif", "MOB-004", "Standard"),
        ]
        connection.executemany(
            """
            INSERT INTO visitors (
                first_name, last_name, phone_number, visit_purpose, department,
                entry_time, exit_time, is_student, university, id_card_number,
                host_name, badge_number, access_level
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                (
                    first,
                    last,
                    phone,
                    purpose,
                    department,
                    entry.isoformat(timespec="minutes"),
                    exit_time.isoformat(timespec="minutes") if exit_time else None,
                    is_student,
                    university,
                    card,
                    host,
                    badge,
                    access,
                )
                for first, last, phone, purpose, department, entry, exit_time, is_student, university, card, host, badge, access in seed_rows
            ],
        )

    def add_visitor(self, payload: dict[str, Any]) -> int:
        with self.connect() as connection:
            cursor = connection.execute(
                """
                INSERT INTO visitors (
                    first_name, last_name, phone_number, visit_purpose, department,
                    entry_time, is_student, university, id_card_number,
                    host_name, badge_number, access_level
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    payload["first_name"],
                    payload["last_name"],
                    payload.get("phone_number", ""),
                    payload["visit_purpose"],
                    payload["department"],
                    datetime.now().isoformat(timespec="minutes"),
                    int(payload.get("is_student", 0)),
                    payload.get("university", ""),
                    payload["id_card_number"],
                    payload.get("host_name", ""),
                    payload.get("badge_number", ""),
                    payload.get("access_level", "Standard"),
                ),
            )
            return int(cursor.lastrowid)

    def get_visitor(self, visitor_id: int) -> sqlite3.Row | None:
        with self.connect() as connection:
            return connection.execute("SELECT * FROM visitors WHERE visitor_id = ?", (visitor_id,)).fetchone()

    def list_visitors(self, limit: int | None = None) -> list[sqlite3.Row]:
        sql = "SELECT * FROM visitors ORDER BY entry_time DESC"
        params: tuple[Any, ...] = ()
        if limit is not None:
            sql += " LIMIT ?"
            params = (limit,)
        with self.connect() as connection:
            return list(connection.execute(sql, params))

    def search_visitors(self, query: str = "", status: str = "all") -> list[sqlite3.Row]:
        filters: list[str] = []
        params: list[Any] = []
        if query:
            filters.append(
                "(first_name LIKE ? OR last_name LIKE ? OR visit_purpose LIKE ? OR department LIKE ? OR id_card_number LIKE ?)"
            )
            params.extend([f"%{query}%"] * 5)
        if status == "inside":
            filters.append("exit_time IS NULL")
        elif status == "exited":
            filters.append("exit_time IS NOT NULL")

        sql = "SELECT * FROM visitors"
        if filters:
            sql += " WHERE " + " AND ".join(filters)
        sql += " ORDER BY entry_time DESC"

        with self.connect() as connection:
            return list(connection.execute(sql, params))

    def record_exit(self, visitor_id: int) -> None:
        with self.connect() as connection:
            connection.execute(
                "UPDATE visitors SET exit_time = ? WHERE visitor_id = ? AND exit_time IS NULL",
                (datetime.now().isoformat(timespec="minutes"), visitor_id),
            )

    def delete_visitor(self, visitor_id: int) -> None:
        with self.connect() as connection:
            connection.execute("DELETE FROM visitors WHERE visitor_id = ?", (visitor_id,))

    def dashboard_stats(self) -> dict[str, int]:
        with self.connect() as connection:
            total = connection.execute("SELECT COUNT(*) FROM visitors").fetchone()[0]
            inside = connection.execute("SELECT COUNT(*) FROM visitors WHERE exit_time IS NULL").fetchone()[0]
            students = connection.execute("SELECT COUNT(*) FROM visitors WHERE is_student = 1").fetchone()[0]
            today = datetime.now().date().isoformat()
            today_count = connection.execute(
                "SELECT COUNT(*) FROM visitors WHERE date(entry_time) = ?",
                (today,),
            ).fetchone()[0]
        return {"total": total, "inside": inside, "students": students, "today": today_count}

    def daily_counts(self) -> list[sqlite3.Row]:
        with self.connect() as connection:
            return list(
                connection.execute(
                    """
                    SELECT date(entry_time) AS day, COUNT(*) AS count
                    FROM visitors
                    GROUP BY date(entry_time)
                    ORDER BY day DESC
                    LIMIT 7
                    """
                )
            )

    def department_counts(self) -> list[sqlite3.Row]:
        with self.connect() as connection:
            return list(
                connection.execute(
                    """
                    SELECT department, COUNT(*) AS count
                    FROM visitors
                    GROUP BY department
                    ORDER BY count DESC, department
                    """
                )
            )

    def report_summary(self) -> dict[str, Any]:
        daily = self.daily_counts()
        departments = self.department_counts()
        stats = self.dashboard_stats()
        total = max(stats["total"], 1)
        peak_day = max(daily, key=lambda row: row["count"], default=None)
        top_department = max(departments, key=lambda row: row["count"], default=None)
        student_share = round((stats["students"] / total) * 100)

        with self.connect() as connection:
            avg_duration = connection.execute(
                """
                SELECT AVG((julianday(exit_time) - julianday(entry_time)) * 24 * 60)
                FROM visitors
                WHERE exit_time IS NOT NULL
                """
            ).fetchone()[0]
            active_rows = list(
                connection.execute(
                    """
                    SELECT first_name, last_name, department, entry_time, host_name, badge_number, access_level
                    FROM visitors
                    WHERE exit_time IS NULL
                    ORDER BY entry_time DESC
                    """
                )
            )
            recent_exits = list(
                connection.execute(
                    """
                    SELECT first_name, last_name, department, exit_time
                    FROM visitors
                    WHERE exit_time IS NOT NULL
                    ORDER BY exit_time DESC
                    LIMIT 4
                    """
                )
            )

        return {
            "stats": stats,
            "daily": daily,
            "departments": departments,
            "peak_day": peak_day,
            "top_department": top_department,
            "student_share": student_share,
            "average_duration": int(avg_duration or 0),
            "active_rows": active_rows,
            "recent_exits": recent_exits,
            "max_daily": max([row["count"] for row in daily] + [1]),
            "max_department": max([row["count"] for row in departments] + [1]),
        }

    def export_csv(self, destination: Path) -> Path:
        rows = self.list_visitors()
        destination.parent.mkdir(parents=True, exist_ok=True)
        with destination.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.writer(handle)
            writer.writerow(
                [
                    "visitor_id",
                    "first_name",
                    "last_name",
                    "phone_number",
                    "visit_purpose",
                    "department",
                    "entry_time",
                    "exit_time",
                    "is_student",
                    "university",
                    "id_card_number",
                ]
            )
            for row in rows:
                writer.writerow([row[key] for key in row.keys()])
        return destination
