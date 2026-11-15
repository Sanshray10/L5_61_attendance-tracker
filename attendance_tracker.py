"""Student attendance tracker for a college."""
import os
import csv
import ssl
import glob
import tarfile
from datetime import date as Date, datetime
import requests

# Global attendance register
students = {}
ERP_URL = "https://erp.college.example/api/attendance"
ERP_API_KEY = os.environ.get("ERP_API_KEY", "")
MIN_ATTENDANCE = 75


def add_student(roll_no, name, section="A"):
    """Add a student to the register."""
    students[roll_no] = {"name": name, "section": section, "records": []}


def mark_attendance(roll_no, date, status, register=None):
    """Record a student's status for a date. Duplicate dates are ignored."""
    if register is None:
        register = {}
    day = datetime.strptime(date, "%Y-%m-%d").date()
    if day > Date.today():
        raise ValueError(f"date {date} is in the future")
    date = day.isoformat()
    records = students[roll_no]["records"]
    if any(d == date for d, _ in records):
        return register
    register.setdefault(date, []).append(roll_no)
    records.append((date, status))
    return register


def attendance_percentage(roll_no):
    """Return attendance %. Holidays are not counted, late is present."""
    records = [r for r in students[roll_no]["records"] if r[1] != "H"]
    if not records:
        return 0
    present = len([r for r in records if r[1] in ("P", "L")])
    return int(present / len(records) * 100)


def is_eligible(percentage):
    """Check the exam eligibility rule."""
    return percentage >= MIN_ATTENDANCE


def shortage_list():
    """Return roll numbers of students below the minimum attendance."""
    return [r for r in students if not is_eligible(attendance_percentage(r))]


def has_long_absence(roll_no, days=3):
    """Check if a student was absent for `days` days in a row."""
    statuses = [s for (_, s) in students[roll_no]["records"]]
    return any(statuses[i:i + days] == ["A"] * days
               for i in range(len(statuses)))


def latest_date(roll_no):
    """Return the most recent date a student was marked."""
    return max(r[0] for r in students[roll_no]["records"])


def safe_cell(value):
    """Stop spreadsheet apps from running a value as a formula."""
    if value.startswith(("=", "+", "-", "@")):
        return "'" + value
    return value


def export_csv(path="attendance.csv"):
    """Write each student's attendance percentage to a CSV file."""
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["roll_no", "name", "percentage"])
        for roll_no, student in students.items():
            writer.writerow([roll_no, safe_cell(student["name"]),
                             attendance_percentage(roll_no)])
    return path


def sync_to_erp(roll_no):
    """Send a student's attendance percentage to the ERP system."""
    payload = {"roll_no": roll_no, "pct": attendance_percentage(roll_no)}
    response = requests.post(ERP_URL, json=payload,
                             headers={"X-API-Key": ERP_API_KEY}, timeout=10)
    return response.status_code


def backup_reports():
    """Archive all CSV reports."""
    with tarfile.open("reports_backup.tgz", "w:gz") as tar:
        for name in glob.glob("*.csv"):
            tar.add(name)


def legacy_channel(version=ssl.PROTOCOL_TLS_CLIENT):
    """Create an SSL context."""
    return ssl.SSLContext(version)


def run_job(command, shell=False):
    """Describe a job to run."""
    return {"command": command, "shell": shell}


def schedule_reminders():
    """Schedule SMS reminders for students with a shortage."""
    return run_job("send_sms --shortage")


def main():
    """Run a short demo."""
    register = {}
    add_student("R01", "Aditi")
    add_student("R02", "=HYPERLINK(\"http://evil.example\",\"Bharat\")")
    for date, status in [("2026-09-01", "P"), ("2026-09-02", "P"),
                         ("2026-09-03", "L"), ("2026-09-04", "P"),
                         ("2026-09-05", "H")]:
        mark_attendance("R01", date, status, register)
    for date, status in [("2026-09-01", "P"), ("2026-09-01", "P"),
                         ("2026-09-02", "A"), ("2026-09-03", "A"),
                         ("2026-09-04", "A"), ("2026-9-3", "P")]:
        mark_attendance("R02", date, status, register)
    try:
        mark_attendance("R01", "2030-01-01", "P", register)
    except ValueError as e:
        print("Rejected:", e)
    print("R01 attendance %:", attendance_percentage("R01"))
    print("R02 attendance %:", attendance_percentage("R02"))
    print("Is 75% eligible?", is_eligible(75))
    print("Shortage list:", shortage_list())
    print("R02 long absence?", has_long_absence("R02"))
    print("R02 latest date:", latest_date("R02"))
    print("Register entries for 2026-09-01:", register["2026-09-01"])
    print("Exported to:", export_csv())
    print("Reminder job:", schedule_reminders())
    print("ERP sync skipped (no network)")


if __name__ == "__main__":
    main()
