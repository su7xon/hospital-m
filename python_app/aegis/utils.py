"""Small formatting / validation helpers used across the app."""

from __future__ import annotations

from datetime import datetime
from typing import Any


def now_str() -> str:
    """Timestamp in the same shape as the original app: YYYY-MM-DD HH:MM."""
    return datetime.now().strftime("%Y-%m-%d %H:%M")


def today_str() -> str:
    return datetime.now().strftime("%Y-%m-%d")


def compact_date(value: Any, with_year: bool = True) -> str:
    """Format an ISO date for dense table cells, leaving other strings untouched."""
    text = str(value or "").strip()
    try:
        parsed = datetime.strptime(text[:10], "%Y-%m-%d")
    except (TypeError, ValueError):
        return text
    return parsed.strftime("%d/%m/%Y" if with_year else "%d/%m")


def compact_expiry(value: Any) -> str:
    """Format an ISO date as MM/YY for compact batch/expiry cells."""
    text = str(value or "").strip()
    try:
        parsed = datetime.strptime(text[:10], "%Y-%m-%d")
    except (TypeError, ValueError):
        return text
    return parsed.strftime("%m/%y")


def clock_str() -> str:
    return datetime.now().strftime("%H:%M:%S")


def inr(value: Any, decimals: int = 0) -> str:
    """Format a number with Indian digit grouping, prefixed by the rupee sign."""
    try:
        amount = float(value or 0)
    except (TypeError, ValueError):
        amount = 0.0

    sign = "-" if amount < 0 else ""
    amount = abs(amount)
    text = f"{amount:,.{decimals}f}"
    integer, _, fraction = text.partition(".")

    if len(integer) > 3:
        head, tail = integer[:-3], integer[-3:]
        groups: list[str] = []
        while len(head) > 2:
            groups.insert(0, head[-2:])
            head = head[:-2]
        if head:
            groups.insert(0, head)
        integer = ",".join(groups) + "," + tail

    result = f"{sign}\u20b9{integer}"
    if decimals > 0:
        result += "." + fraction
    return result


def initials(name: str) -> str:
    parts = [part for part in (name or "").replace("Dr.", "").split() if part]
    if not parts:
        return "?"
    if len(parts) == 1:
        return parts[0][:2].upper()
    return (parts[0][0] + parts[-1][0]).upper()


def short(text: str, length: int = 54) -> str:
    text = " ".join(str(text or "").split())
    if len(text) <= length:
        return text
    return text[: max(0, length - 1)].rstrip() + "\u2026"


def age_gender(patient: dict) -> str:
    gender = (patient.get("gender") or "")[:1]
    return f"{patient.get('age', '?')}y / {gender or '?'}"


def patient_latest_vital(patient: dict) -> dict | None:
    vitals = patient.get("vitals") or []
    return vitals[0] if vitals else None


def safe_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(str(value).replace(",", "").strip())
    except (TypeError, ValueError):
        return default


def safe_int(value: Any, default: int = 0) -> int:
    try:
        return int(float(str(value).strip()))
    except (TypeError, ValueError):
        return default


def triage_color(triage: str) -> str:
    if triage.startswith("P1"):
        return "rose"
    if triage.startswith("P2"):
        return "amber"
    if triage.startswith("P3"):
        return "blue"
    return "muted"


def status_color(status: str) -> str:
    mapping = {
        "ICU": "rose",
        "Emergency": "amber",
        "Admitted": "text",
        "Outpatient": "blue",
        "Discharged": "muted",
        "Available": "emerald",
        "Occupied": "text",
        "Cleaning": "amber",
        "Maintenance": "muted",
        "Scheduled": "text",
        "Checked-in": "blue",
        "In Consultation": "amber",
        "Completed": "emerald",
        "Cancelled": "muted",
        "Paid": "emerald",
        "Pending": "amber",
        "Partially Paid": "blue",
        "Waiting": "amber",
        "In Treatment": "rose",
        "Admitted ": "text",
        "Routine": "muted",
        "STAT Urgent": "rose",
        "On Duty": "emerald",
        "Off Duty": "muted",
    }
    return mapping.get((status or "").strip(), "text")
