"""
src/reports/export_attendance.py

Exports attendance records to Excel (.xlsx) files using openpyxl.

Design intent (matches existing modules):
    - No UI dependency — plain functions, callable from CLI, a future API,
      or a Streamlit page.
    - Reuses list_attendance() from src.attendance.mark_attendance as the
      single source of truth for attendance data — this module does no
      direct DB querying of its own.
    - Raises exceptions on failure (ValueError for bad input, RuntimeError
      for nothing-to-export cases) rather than returning result objects,
      matching course_manager.py and mark_attendance.py conventions.
"""

import os
import sys
from datetime import datetime, timezone

from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, PatternFill
from openpyxl.utils import get_column_letter

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))

from src.attendance.mark_attendance import list_attendance
from src.utils.config import REPORTS_DIR


COLUMN_HEADERS = [
    "Student Name",
    "Matric Number",
    "Department",
    "Level",
    "Course Code",
    "Date",
    "Time Checked In",
]


def _split_recorded_at(recorded_at_iso):
    """
    recorded_at is stored as a full ISO datetime string (UTC). Splits it
    into a date and a human-readable time-of-day for the report, since
    the proposal's report format wants Date and Time as separate columns.
    """
    dt = datetime.fromisoformat(recorded_at_iso)
    return dt.date().isoformat(), dt.strftime("%H:%M:%S")


def _build_workbook(rows, title):
    """
    Builds and returns an openpyxl Workbook from a list of attendance
    row dicts (as returned by list_attendance()). Applies basic styling
    — bold header row, frozen header, auto-sized columns — so the export
    looks presentable without manual formatting after the fact.
    """
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = title[:31]  # Excel sheet name limit is 31 characters

    header_font = Font(bold=True, color="FFFFFF")
    header_fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
    header_alignment = Alignment(horizontal="center", vertical="center")

    for col_index, header in enumerate(COLUMN_HEADERS, start=1):
        cell = sheet.cell(row=1, column=col_index, value=header)
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = header_alignment

    for row_index, record in enumerate(rows, start=2):
        session_date, time_checked_in = _split_recorded_at(record["recorded_at"])
        sheet.cell(row=row_index, column=1, value=record["full_name"])
        sheet.cell(row=row_index, column=2, value=record["matric_number"])
        sheet.cell(row=row_index, column=3, value=record["department"])
        sheet.cell(row=row_index, column=4, value=record["level"])
        sheet.cell(row=row_index, column=5, value=record["course_code"])
        sheet.cell(row=row_index, column=6, value=record["session_date"])
        sheet.cell(row=row_index, column=7, value=time_checked_in)

    sheet.freeze_panes = "A2"

    for col_index, header in enumerate(COLUMN_HEADERS, start=1):
        column_letter = get_column_letter(col_index)
        max_length = max(
            [len(header)] + [len(str(sheet.cell(row=r, column=col_index).value or "")) for r in range(2, sheet.max_row + 1)]
        )
        sheet.column_dimensions[column_letter].width = max_length + 4

    return workbook


def export_attendance(course_code=None, session_date=None, output_path=None):
    """
    Exports attendance records to an .xlsx file.

    course_code:  if provided, only that course's records are included.
    session_date: if provided (YYYY-MM-DD or ISO datetime string), only
                  that session date's records are included.
    output_path:  if provided, the file is written there. Otherwise a
                  filename is auto-generated inside REPORTS_DIR, e.g.
                  "CSC301_2026-09-15.xlsx" or "attendance_export_<timestamp>.xlsx"
                  if no course_code/session_date filter was given.

    Raises RuntimeError if there are no matching attendance records to export.
    Returns the full path to the written file.
    """
    rows = list_attendance(course_code=course_code, session_date=session_date)

    if not rows:
        raise RuntimeError(
            "No attendance records found for the given filters — nothing to export."
        )

    os.makedirs(REPORTS_DIR, exist_ok=True)

    if output_path is None:
        if course_code and session_date:
            filename = f"{course_code}_{session_date}.xlsx"
        elif course_code:
            filename = f"{course_code}_all_sessions.xlsx"
        elif session_date:
            filename = f"attendance_{session_date}.xlsx"
        else:
            timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
            filename = f"attendance_export_{timestamp}.xlsx"
        output_path = os.path.join(REPORTS_DIR, filename)

    title = course_code if course_code else "Attendance"
    workbook = _build_workbook(rows, title=title)
    workbook.save(output_path)

    return output_path


if __name__ == "__main__":
    print("=== Attendance Report Export ===")
    print("Leave a field blank to skip that filter.")

    course = input("Course code (optional): ").strip() or None
    date_input = input("Session date, YYYY-MM-DD (optional): ").strip() or None

    try:
        path = export_attendance(course_code=course, session_date=date_input)
        print(f"[SUCCESS] Report exported to: {path}")
    except RuntimeError as error:
        print(f"[FAILED] {error}")