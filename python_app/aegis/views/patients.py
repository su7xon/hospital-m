"""Patient clinical directory."""

from __future__ import annotations

import json
from pathlib import Path
from tkinter import filedialog
from typing import Any

import customtkinter as ctk

from .. import theme
from ..utils import age_gender, compact_date, patient_latest_vital, short, status_color, today_str
from ..widgets import (
    BaseView,
    Card,
    DataTable,
    PageHeader,
    PillTabs,
    font,
    primary_button,
    secondary_button,
)

STATUSES = ["All", "Admitted", "ICU", "Emergency", "Outpatient", "Discharged"]


class PatientsView(BaseView):
    def __init__(self, master: Any, app: Any) -> None:
        super().__init__(master, app)
        self.grid_rowconfigure(2, weight=1)
        self._build()
        self.refresh()

    def _build(self) -> None:
        header = PageHeader(
            self,
            "Patient Clinical Directory",
            "Electronic health records, active ward census, vitals history and intake charts.",
        )
        header.grid(row=0, column=0, sticky="ew", padx=18, pady=(14, 10))
        self.count_label = ctk.CTkLabel(
            header.actions, text="", font=font(10, mono=True),
            text_color=theme.MUTED, anchor="e",
        )
        self.count_label.pack(side="left", padx=(0, 10))
        secondary_button(header.actions, "Export JSON", self._export).pack(side="left", padx=(0, 6))
        primary_button(header.actions, "+ Admit Patient", self.app.open_admit, width=136).pack(side="left")

        filters = Card(self)
        filters.grid(row=1, column=0, sticky="ew", padx=18, pady=(0, 10))
        filters.grid_columnconfigure(0, weight=1)
        top = ctk.CTkFrame(filters, fg_color="transparent")
        top.grid(row=0, column=0, sticky="ew", padx=12, pady=(11, 6))
        top.grid_columnconfigure(0, weight=1)

        self.search = ctk.CTkEntry(
            top,
            placeholder_text="Search by patient name, MRN, phone or diagnosis...",
            height=33, corner_radius=6,
            fg_color=theme.CARD_ALT, border_color=theme.BORDER_STRONG,
            border_width=1, text_color=theme.TEXT, font=font(11),
            placeholder_text_color=theme.FAINT,
        )
        self.search.grid(row=0, column=0, sticky="ew", padx=(0, 14))
        self.search.bind("<KeyRelease>", lambda _e: self.refresh())

        ctk.CTkLabel(
            top, text="Ward", font=font(10, bold=True), text_color=theme.MUTED,
        ).grid(row=0, column=1, padx=(0, 6))
        self.ward_filter = ctk.CTkOptionMenu(
            top,
            values=[
                "All Wards", "ICU", "General Ward A", "General Ward B",
                "Private Suite", "Emergency Care",
            ],
            width=152, height=33, corner_radius=6,
            fg_color=theme.CARD_ALT, button_color=theme.PRIMARY_SOFT,
            button_hover_color=theme.BORDER_STRONG, text_color=theme.TEXT,
            font=font(10), dropdown_font=font(10),
            command=lambda _v: self.refresh(),
        )
        self.ward_filter.set("All Wards")
        self.ward_filter.grid(row=0, column=2)

        self.status_tabs = PillTabs(
            filters,
            [(status, status) for status in STATUSES],
            command=lambda _v: self.refresh(),
            value="All",
        )
        self.status_tabs.grid(row=1, column=0, sticky="w", padx=12, pady=(4, 11))

        table_card = Card(self)
        table_card.grid(row=2, column=0, sticky="nsew", padx=18, pady=(0, 12))
        table_card.grid_rowconfigure(0, weight=1)
        table_card.grid_columnconfigure(0, weight=1)

        columns = [
            {"key": "mrn", "title": "MRN / Intake", "width": 140, "stretch": False},
            {"key": "patient", "title": "Patient Details", "width": 190},
            {"key": "ward", "title": "Ward & Bed", "width": 150, "stretch": False},
            {"key": "diagnosis", "title": "Chief Complaint / Diagnosis", "width": 220},
            {"key": "doctor", "title": "Attending Doctor", "width": 150},
            {"key": "vitals", "title": "Latest Vitals", "width": 155, "stretch": False},
            {"key": "status", "title": "Status", "width": 90, "stretch": False, "anchor": "center"},
        ]
        self.table = DataTable(
            table_card, columns, height=12,
            on_double_click=self._open_patient,
            empty_text="No matching patient records found. Try adjusting the filters.",
        )
        self.table.grid(row=0, column=0, sticky="nsew", padx=1, pady=(1, 0))

        footer = ctk.CTkFrame(table_card, fg_color="transparent")
        footer.grid(row=1, column=0, sticky="ew", padx=12, pady=7)
        ctk.CTkLabel(
            footer, text="Double-click a row to open the full clinical chart.",
            font=font(9), text_color=theme.FAINT, anchor="w",
        ).pack(side="left")
        secondary_button(footer, "Open Selected Chart", self._open_selected, height=28).pack(side="right")

    # ------------------------------------------------------------------ refresh
    def refresh(self) -> None:
        search = self.search.get().strip().lower()
        ward = self.ward_filter.get()
        status = self.status_tabs.get() or "All"

        counts = {key: 0 for key in STATUSES}
        counts["All"] = len(self.store.patients)
        for patient in self.store.patients:
            patient_status = patient.get("status", "")
            if patient_status in counts:
                counts[patient_status] += 1
        self.status_tabs.refresh_options(
            [(key, f"{key}  {counts.get(key, 0)}") for key in STATUSES]
        )

        filtered = []
        for patient in self.store.patients:
            haystack = " ".join([
                str(patient.get("name", "")),
                str(patient.get("mrn", "")),
                str(patient.get("phone", "")),
                str(patient.get("chiefComplaint", "")),
                " ".join(patient.get("diagnoses") or []),
            ]).lower()
            if search and search not in haystack:
                continue
            if status != "All" and patient.get("status") != status:
                continue
            if ward != "All Wards" and patient.get("ward") != ward:
                continue
            filtered.append(patient)

        rows = []
        for patient in filtered:
            vital = patient_latest_vital(patient)
            if vital:
                vitals_text = (
                    f"BP {vital.get('bloodPressure')} · SpO2 {vital.get('spo2')}%"
                )
            else:
                vitals_text = "Pending intake"
            bed = patient.get("bedNumber")
            ward_text = f"{bed or 'OPD'} · {patient.get('ward') or 'Not assigned'}"
            diagnosis = (patient.get("diagnoses") or [patient.get("chiefComplaint", "")])[0]
            allergies = patient.get("allergies") or []
            if allergies and allergies[0] not in (
                "No known drug allergies (NKDA)", "No known allergies",
            ):
                diagnosis = f"{diagnosis}  [Allergy: {', '.join(allergies)}]"
            status_value = patient.get("status", "")
            rows.append({
                "iid": patient["id"],
                "record": patient,
                "values": (
                    f"{patient.get('mrn')} · {compact_date(patient.get('admissionDate'))}",
                    f"{patient.get('name')}  ({age_gender(patient)} · {patient.get('bloodGroup')})",
                    ward_text,
                    short(diagnosis, 40),
                    patient.get("assignedDoctorName", ""),
                    vitals_text,
                    status_value,
                ),
                "tags": [status_color(status_value)],
            })

        self.table.set_rows(rows)
        self.count_label.configure(text=f"{len(filtered)} / {len(self.store.patients)} records")

    # ------------------------------------------------------------------ actions
    def _open_patient(self, patient_id: str) -> None:
        self.app.open_patient(patient_id)

    def _open_selected(self) -> None:
        patient_id = self.table.selected_id()
        if not patient_id:
            self.app.toast("Select a patient row first.", error=True)
            return
        self.app.open_patient(patient_id)

    def _export(self) -> None:
        default_name = f"aegis_patients_registry_{today_str()}.json"
        path = filedialog.asksaveasfilename(
            parent=self.app,
            title="Export patient registry",
            defaultextension=".json",
            initialfile=default_name,
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
        )
        if not path:
            return
        try:
            Path(path).write_text(
                json.dumps(self.store.patients, indent=2, ensure_ascii=False),
                encoding="utf-8",
            )
            self.app.toast(f"Patient registry exported to {Path(path).name}.")
        except OSError as error:
            self.app.toast(f"Export failed: {error}", error=True)
