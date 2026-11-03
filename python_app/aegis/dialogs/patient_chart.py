"""Full patient chart window: summary, vitals, notes, transfer and discharge."""

from __future__ import annotations

from typing import Any

import customtkinter as ctk

from .. import theme
from ..utils import age_gender, inr, safe_float, safe_int, status_color
from ..widgets import (
    Card,
    DataTable,
    font,
    primary_button,
    secondary_button,
    danger_button,
    field,
    tinted_button,
    value,
)


def _clear(frame: ctk.CTkFrame) -> None:
    for child in frame.winfo_children():
        child.destroy()


class PatientChart(ctk.CTkToplevel):
    def __init__(self, app: Any, patient_id: str) -> None:
        super().__init__(app)
        self.app = app
        self.store = app.store
        self.patient_id = patient_id
        self.current_tab = "summary"
        self.tab_buttons: dict[str, ctk.CTkButton] = {}

        self.title("Patient Clinical Chart")
        self.configure(fg_color=theme.BG)
        self.minsize(980, 680)
        self.transient(app)
        self.protocol("WM_DELETE_WINDOW", self.close)
        self.bind("<Escape>", lambda _e: self.close())

        self.update_idletasks()
        width, height = 1120, 800
        x = app.winfo_rootx() + max(0, (app.winfo_width() - width) // 2)
        y = app.winfo_rooty() + max(0, (app.winfo_height() - height) // 2)
        x = min(max(10, x), max(10, self.winfo_screenwidth() - width - 10))
        y = min(max(10, y), max(10, self.winfo_screenheight() - height - 40))
        self.geometry(f"{width}x{height}+{x}+{y}")

        self._build_shell()
        self.render()
        self.after(40, self._activate)

    def _activate(self) -> None:
        try:
            self.grab_set()
            self.focus_force()
        except Exception:
            pass

    def _patient(self) -> dict | None:
        return self.store.patient(self.patient_id)

    # ------------------------------------------------------------------ shell
    def _build_shell(self) -> None:
        self.header = ctk.CTkFrame(self, fg_color=theme.CARD, corner_radius=0, height=108)
        self.header.pack(fill="x")
        self.header.pack_propagate(False)
        self.header.grid_columnconfigure(0, weight=1)
        self.title_label = ctk.CTkLabel(
            self.header, text="", font=font(19, bold=True), text_color=theme.TEXT, anchor="w",
        )
        self.title_label.grid(row=0, column=0, sticky="w", padx=20, pady=(13, 0))
        self.meta_label = ctk.CTkLabel(
            self.header, text="", font=font(10), text_color=theme.MUTED, anchor="w",
        )
        self.meta_label.grid(row=1, column=0, sticky="w", padx=20, pady=(2, 0))
        self.status_chip = ctk.CTkLabel(
            self.header, text="", font=font(10, bold=True),
            corner_radius=6, padx=10, height=24,
        )
        self.status_chip.grid(row=0, column=1, sticky="e", padx=(8, 12), pady=(13, 0))
        ctk.CTkButton(
            self.header, text="✕", width=34, height=34, corner_radius=6,
            fg_color="transparent", hover_color=theme.CARD_HOVER,
            text_color=theme.MUTED, font=font(14), command=self.close,
        ).grid(row=0, column=2, rowspan=2, padx=(0, 14), pady=20)

        self.allergy_bar = ctk.CTkLabel(
            self, text="", font=font(10, bold=True), text_color=theme.ROSE,
            fg_color=theme.ROSE_BG, anchor="w", height=30, corner_radius=0,
        )
        self.allergy_bar.pack(fill="x")

        self.tab_bar = ctk.CTkFrame(self, fg_color=theme.CARD, corner_radius=0, height=44)
        self.tab_bar.pack(fill="x")
        self.tab_bar.pack_propagate(False)
        tabs = [
            ("summary", "Clinical Summary"),
            ("vitals", "Vitals History"),
            ("notes", "Clinical Notes"),
            ("transfer", "Transfer Bed"),
            ("discharge", "Discharge"),
        ]
        for key, label in tabs:
            button = ctk.CTkButton(
                self.tab_bar, text=label, font=font(10, bold=True),
                fg_color="transparent", hover_color=theme.CARD_HOVER,
                text_color=theme.MUTED, height=42, corner_radius=0,
                command=lambda k=key: self.show_tab(k),
            )
            button.pack(side="left", padx=(4, 0))
            self.tab_buttons[key] = button

        self.footer = ctk.CTkFrame(self, fg_color=theme.CARD, corner_radius=0, height=58)
        self.footer.pack(fill="x", side="bottom")
        self.footer.pack_propagate(False)
        secondary_button(
            self.footer, "Generate Bill / Invoice", self._generate_bill,
            height=32, width=170,
        ).pack(side="left", padx=16, pady=13)
        primary_button(
            self.footer, "Close Chart", self.close,
            height=32, width=110,
        ).pack(side="right", padx=16, pady=13)

        self.content = ctk.CTkScrollableFrame(
            self, fg_color=theme.BG, corner_radius=0,
            scrollbar_button_color=theme.BORDER_STRONG,
            scrollbar_button_hover_color=theme.MUTED,
        )
        self.content.pack(fill="both", expand=True)

    def render(self) -> None:
        patient = self._patient()
        if not patient:
            self.close()
            return
        self.title_label.configure(text=f"{patient.get('name')}   ·   {patient.get('mrn')}")
        location = (
            f"{patient.get('bedNumber')} ({patient.get('ward')})"
            if patient.get("bedNumber") else "Outpatient / no bed"
        )
        self.meta_label.configure(
            text=(
                f"{age_gender(patient)}  ·  {patient.get('gender')}  ·  Blood {patient.get('bloodGroup')}  ·  "
                f"{location}  ·  Admitted {patient.get('admissionDate')}  ·  "
                f"{patient.get('assignedDoctorName')} ({patient.get('department')})"
            )
        )
        status = patient.get("status", "")
        color = status_color(status)
        palette = {
            "rose": (theme.ROSE, theme.ROSE_BG),
            "amber": (theme.AMBER, theme.AMBER_BG),
            "emerald": (theme.EMERALD, theme.EMERALD_BG),
            "blue": (theme.BLUE, theme.BLUE_BG),
            "muted": (theme.MUTED, theme.CARD_ALT),
            "text": (theme.TEXT, theme.CARD_ALT),
        }
        fg, bg = palette.get(color, palette["text"])
        self.status_chip.configure(text=f" {status} ", text_color=fg, fg_color=bg)

        allergies = patient.get("allergies") or []
        if allergies and allergies[0] not in ("No known drug allergies (NKDA)", "No known allergies"):
            self.allergy_bar.configure(text=f"  ⚠  Documented allergies: {', '.join(allergies)}")
            self.allergy_bar.pack(fill="x", before=self.tab_bar)
        else:
            self.allergy_bar.pack_forget()

    def show_tab(self, tab: str) -> None:
        self.current_tab = tab
        for key, button in self.tab_buttons.items():
            selected = key == tab
            button.configure(
                fg_color=theme.PRIMARY_SOFT if selected else "transparent",
                text_color=theme.TEXT if selected else theme.MUTED,
                font=font(10, bold=True),
            )
        _clear(self.content)
        try:
            self.content._parent_canvas.yview_moveto(0)
        except Exception:
            pass
        patient = self._patient()
        if not patient:
            self.close()
            return
        if tab == "summary":
            self._render_summary(patient)
        elif tab == "vitals":
            self._render_vitals(patient)
        elif tab == "notes":
            self._render_notes(patient)
        elif tab == "transfer":
            self._render_transfer(patient)
        elif tab == "discharge":
            self._render_discharge(patient)

    # ------------------------------------------------------------------ summary
    def _render_summary(self, patient: dict) -> None:
        content = ctk.CTkFrame(self.content, fg_color="transparent")
        content.pack(fill="x", padx=18, pady=14)
        content.grid_columnconfigure(0, weight=1)
        content.grid_columnconfigure(1, weight=1)

        vitals = patient.get("vitals") or []
        vitals_card = Card(content)
        vitals_card.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 12))
        vitals_card.grid_columnconfigure(0, weight=1)
        header = ctk.CTkFrame(vitals_card, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=15, pady=(12, 0))
        header.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(
            header, text="Current Vital Signs", font=font(13, bold=True),
            text_color=theme.TEXT, anchor="w",
        ).grid(row=0, column=0, sticky="w")
        tinted_button(
            header, "+ Record Reading", lambda: self.show_tab("vitals"),
            color=theme.TEXT_SECONDARY, bg=theme.CARD_ALT, border=theme.BORDER_STRONG,
            height=26,
        ).grid(row=0, column=1, sticky="e")

        if vitals:
            current = vitals[0]
            metrics = ctk.CTkFrame(vitals_card, fg_color="transparent")
            metrics.grid(row=1, column=0, sticky="ew", padx=10, pady=(8, 12))
            for index in range(5):
                metrics.grid_columnconfigure(index, weight=1, uniform="vital_metric")
            cards = [
                ("Heart Rate", str(current.get("heartRate", "—")), "bpm", theme.TEXT),
                ("Blood Pressure", str(current.get("bloodPressure", "—")), "mmHg", theme.TEXT),
                ("Oxygen SpO2", str(current.get("spo2", "—")), "%", theme.EMERALD),
                ("Temperature", str(current.get("temperature", "—")), "°F", theme.TEXT),
                ("Respiratory", str(current.get("respiratoryRate", "—")), "/min", theme.TEXT),
            ]
            for index, (label, number, unit, color) in enumerate(cards):
                metric = ctk.CTkFrame(metrics, fg_color=theme.CARD_ALT, corner_radius=8)
                metric.grid(row=0, column=index, sticky="nsew", padx=5)
                ctk.CTkLabel(
                    metric, text=label, font=font(9), text_color=theme.MUTED, anchor="w",
                ).pack(fill="x", padx=11, pady=(8, 0))
                ctk.CTkLabel(
                    metric, text=f"{number}  {unit}", font=font(17, bold=True),
                    text_color=color, anchor="w",
                ).pack(fill="x", padx=11)
                ctk.CTkLabel(
                    metric, text="", font=font(8), text_color=theme.FAINT, anchor="w",
                ).pack(fill="x", padx=11, pady=(0, 7))
            ctk.CTkLabel(
                vitals_card,
                text=f"Last recorded at {current.get('recordedAt')} by {current.get('recordedBy')}",
                font=font(9, mono=True), text_color=theme.FAINT, anchor="w",
            ).grid(row=2, column=0, sticky="w", padx=15, pady=(0, 10))
        else:
            ctk.CTkLabel(
                vitals_card, text="No vitals recorded yet.", font=font(10),
                text_color=theme.FAINT, anchor="w",
            ).grid(row=1, column=0, sticky="w", padx=16, pady=16)

        complaint_card = Card(content)
        complaint_card.grid(row=1, column=0, sticky="nsew", padx=(0, 6), pady=(0, 12))
        ctk.CTkLabel(
            complaint_card, text="Chief Complaint on Admission", font=font(12, bold=True),
            text_color=theme.TEXT, anchor="w",
        ).pack(fill="x", padx=15, pady=(12, 4))
        ctk.CTkLabel(
            complaint_card, text=patient.get("chiefComplaint", ""), font=font(10),
            text_color=theme.TEXT_SECONDARY, anchor="w", justify="left", wraplength=470,
        ).pack(fill="x", padx=15, pady=(0, 13))

        diagnosis_card = Card(content)
        diagnosis_card.grid(row=1, column=1, sticky="nsew", padx=(6, 0), pady=(0, 12))
        ctk.CTkLabel(
            diagnosis_card, text="Clinical Diagnoses", font=font(12, bold=True),
            text_color=theme.TEXT, anchor="w",
        ).pack(fill="x", padx=15, pady=(12, 4))
        for diagnosis in patient.get("diagnoses") or ["Pending clinical evaluation"]:
            ctk.CTkLabel(
                diagnosis_card, text=f"•  {diagnosis}", font=font(10),
                text_color=theme.TEXT_SECONDARY, anchor="w", justify="left", wraplength=470,
            ).pack(fill="x", padx=15, pady=(0, 2))
        ctk.CTkFrame(diagnosis_card, height=6, fg_color="transparent").pack()

        team_card = Card(content)
        team_card.grid(row=2, column=0, sticky="nsew", padx=(0, 6), pady=(0, 12))
        ctk.CTkLabel(
            team_card, text="Care Team", font=font(12, bold=True),
            text_color=theme.TEXT, anchor="w",
        ).pack(fill="x", padx=15, pady=(12, 4))
        ctk.CTkLabel(
            team_card, text=patient.get("assignedDoctorName", ""), font=font(11, bold=True),
            text_color=theme.TEXT_SECONDARY, anchor="w",
        ).pack(fill="x", padx=15)
        ctk.CTkLabel(
            team_card, text=f"Department of {patient.get('department', '')}", font=font(9),
            text_color=theme.MUTED, anchor="w",
        ).pack(fill="x", padx=15, pady=(0, 13))

        contact_card = Card(content)
        contact_card.grid(row=2, column=1, sticky="nsew", padx=(6, 0), pady=(0, 12))
        contact = patient.get("emergencyContact") or {}
        ctk.CTkLabel(
            contact_card, text="Emergency Contact / Next of Kin", font=font(12, bold=True),
            text_color=theme.TEXT, anchor="w",
        ).pack(fill="x", padx=15, pady=(12, 4))
        ctk.CTkLabel(
            contact_card,
            text=f"{contact.get('name', '—')} ({contact.get('relation', '—')})",
            font=font(11, bold=True), text_color=theme.TEXT_SECONDARY, anchor="w",
        ).pack(fill="x", padx=15)
        ctk.CTkLabel(
            contact_card, text=contact.get("phone", "") or "—", font=font(9, mono=True),
            text_color=theme.MUTED, anchor="w",
        ).pack(fill="x", padx=15, pady=(0, 13))

        labs = [
            lab for lab in self.store.lab_orders
            if lab.get("patientMrn") == patient.get("mrn") or lab.get("patientName") == patient.get("name")
        ]
        labs_card = Card(content)
        labs_card.grid(row=3, column=0, columnspan=2, sticky="ew", pady=(0, 12))
        labs_card.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(
            labs_card, text=f"Laboratory Investigations ({len(labs)})", font=font(12, bold=True),
            text_color=theme.TEXT, anchor="w",
        ).grid(row=0, column=0, sticky="w", padx=15, pady=(12, 4))
        if labs:
            for index, lab in enumerate(labs, start=1):
                row = ctk.CTkFrame(labs_card, fg_color="transparent")
                row.grid(row=index, column=0, sticky="ew", padx=15, pady=(0, 4))
                row.grid_columnconfigure(0, weight=1)
                ctk.CTkLabel(
                    row, text=f"{lab.get('testName')} · {lab.get('status')}",
                    font=font(10, bold=True), text_color=theme.TEXT_SECONDARY, anchor="w",
                ).grid(row=0, column=0, sticky="w")
                if lab.get("resultSummary"):
                    ctk.CTkLabel(
                        row, text=lab.get("resultSummary"), font=font(9, mono=True),
                        text_color=theme.MUTED, anchor="w", justify="left", wraplength=920,
                    ).grid(row=1, column=0, sticky="w", pady=(1, 3))
        else:
            ctk.CTkLabel(
                labs_card, text="No laboratory requisitions ordered for this patient.",
                font=font(9), text_color=theme.FAINT, anchor="w",
            ).grid(row=1, column=0, sticky="w", padx=15, pady=(0, 12))
        ctk.CTkFrame(labs_card, height=6, fg_color="transparent").grid(row=2, column=0)

        notes_card = Card(content)
        notes_card.grid(row=4, column=0, columnspan=2, sticky="ew")
        notes_header = ctk.CTkFrame(notes_card, fg_color="transparent")
        notes_header.grid(row=0, column=0, sticky="ew", padx=15, pady=(12, 4))
        notes_header.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(
            notes_header, text=f"Recent Clinical Notes ({len(patient.get('notes') or [])})",
            font=font(12, bold=True), text_color=theme.TEXT, anchor="w",
        ).grid(row=0, column=0, sticky="w")
        tinted_button(
            notes_header, "+ Add Note", lambda: self.show_tab("notes"),
            color=theme.TEXT_SECONDARY, bg=theme.CARD_ALT, border=theme.BORDER_STRONG,
            height=24,
        ).grid(row=0, column=1, sticky="e")
        notes = patient.get("notes") or []
        if notes:
            for index, note in enumerate(notes[:6], start=1):
                ctk.CTkLabel(
                    notes_card, text=f"•  {note}", font=font(9),
                    text_color=theme.TEXT_SECONDARY, anchor="w", justify="left",
                    wraplength=980,
                ).grid(row=index, column=0, sticky="w", padx=15, pady=(0, 2))
            if len(notes) > 6:
                ctk.CTkLabel(
                    notes_card, text=f"+ {len(notes) - 6} earlier notes available in Clinical Notes",
                    font=font(9), text_color=theme.FAINT, anchor="w",
                ).grid(row=7, column=0, sticky="w", padx=15, pady=(0, 4))
        else:
            ctk.CTkLabel(
                notes_card, text="No clinical notes recorded.", font=font(9),
                text_color=theme.FAINT, anchor="w",
            ).grid(row=1, column=0, sticky="w", padx=15, pady=(0, 12))
        ctk.CTkFrame(notes_card, height=8, fg_color="transparent").grid(row=8, column=0)

    # ------------------------------------------------------------------ vitals
    def _render_vitals(self, patient: dict) -> None:
        content = ctk.CTkFrame(self.content, fg_color="transparent")
        content.pack(fill="x", padx=18, pady=14)
        content.grid_columnconfigure(0, weight=1)

        form_card = Card(content)
        form_card.grid(row=0, column=0, sticky="ew", pady=(0, 12))
        ctk.CTkLabel(
            form_card, text="Log New Clinical Vital Signs", font=font(13, bold=True),
            text_color=theme.TEXT, anchor="w",
        ).grid(row=0, column=0, columnspan=6, sticky="w", padx=15, pady=(12, 4))
        for column in range(6):
            form_card.grid_columnconfigure(column, weight=1, uniform="vital_form")

        self.new_hr = field(form_card, "Heart rate (bpm)", 1, 0, default=76)
        self.new_bp = field(form_card, "Blood pressure", 1, 1, default="120/80", mono=True)
        self.new_spo2 = field(form_card, "SpO2 (%)", 1, 2, default=98)
        self.new_temp = field(form_card, "Temperature (°F)", 1, 3, default="98.6")
        self.new_rr = field(form_card, "Respiratory rate (/min)", 1, 4, default=16)
        self.new_recorder = field(form_card, "Recorded by", 1, 5, default="Staff Nurse")
        buttons = ctk.CTkFrame(form_card, fg_color="transparent")
        buttons.grid(row=2, column=0, columnspan=6, sticky="e", padx=15, pady=(4, 12))
        primary_button(buttons, "Save Vitals Reading", self._save_vitals, height=30).pack(side="right")

        history_card = Card(content)
        history_card.grid(row=1, column=0, sticky="ew")
        history_card.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(
            history_card, text="Vitals History", font=font(13, bold=True),
            text_color=theme.TEXT, anchor="w",
        ).grid(row=0, column=0, sticky="w", padx=15, pady=(12, 4))
        columns = [
            {"key": "time", "title": "Recorded At", "width": 150, "stretch": False},
            {"key": "hr", "title": "Heart Rate", "width": 100, "stretch": False},
            {"key": "bp", "title": "Blood Pressure", "width": 120, "stretch": False},
            {"key": "spo2", "title": "SpO2", "width": 90, "stretch": False},
            {"key": "temp", "title": "Temp", "width": 90, "stretch": False},
            {"key": "rr", "title": "Resp. Rate", "width": 100, "stretch": False},
            {"key": "recorder", "title": "Recorded By", "width": 160},
        ]
        table = DataTable(history_card, columns, height=6,
                          empty_text="No vitals recorded for this patient.")
        table.grid(row=1, column=0, sticky="ew", padx=14, pady=(0, 14))
        rows = []
        for index, vital in enumerate(patient.get("vitals") or []):
            rows.append({
                "iid": vital.get("id", f"v-{index}"),
                "record": vital,
                "values": (
                    vital.get("recordedAt", ""),
                    f"{vital.get('heartRate', '')} bpm",
                    vital.get("bloodPressure", ""),
                    f"{vital.get('spo2', '')}%",
                    f"{vital.get('temperature', '')}°F",
                    f"{vital.get('respiratoryRate', '')}/min",
                    vital.get("recordedBy", ""),
                ),
            })
        table.set_rows(rows)

    def _save_vitals(self) -> None:
        patient = self._patient()
        if not patient:
            return
        data = {
            "heartRate": safe_int(value(self.new_hr), 0),
            "bloodPressure": value(self.new_bp),
            "spo2": safe_int(value(self.new_spo2), 0),
            "temperature": safe_float(value(self.new_temp), 0),
            "respiratoryRate": safe_int(value(self.new_rr), 0),
            "recordedBy": value(self.new_recorder) or "Staff Nurse",
        }
        if not data["bloodPressure"]:
            self.app.toast("Blood pressure is required.", error=True)
            return
        try:
            self.store.add_vital(patient["id"], data)
        except Exception as error:
            self.app.toast(str(error), error=True)
            return
        self.show_tab("vitals")

    # -------------------------------------------------------------------- notes
    def _render_notes(self, patient: dict) -> None:
        content = ctk.CTkFrame(self.content, fg_color="transparent")
        content.pack(fill="x", padx=18, pady=14)
        content.grid_columnconfigure(0, weight=1)

        form_card = Card(content)
        form_card.grid(row=0, column=0, sticky="ew", pady=(0, 12))
        form_card.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(
            form_card, text="Add Doctor / Nursing Progress Note", font=font(13, bold=True),
            text_color=theme.TEXT, anchor="w",
        ).grid(row=0, column=0, sticky="w", padx=15, pady=(12, 4))
        self.note_box = ctk.CTkTextbox(
            form_card, height=90, corner_radius=6, border_width=1,
            border_color=theme.BORDER_STRONG, fg_color=theme.CARD_ALT,
            text_color=theme.TEXT, font=font(10),
        )
        self.note_box.grid(row=1, column=0, sticky="ew", padx=15, pady=(2, 8))
        self.note_box.insert("1.0", "")
        primary_button(form_card, "Post Progress Note", self._save_note, height=30).grid(
            row=2, column=0, sticky="e", padx=15, pady=(0, 12),
        )

        notes_card = Card(content)
        notes_card.grid(row=1, column=0, sticky="ew")
        notes_card.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(
            notes_card, text=f"Clinical Notes Timeline ({len(patient.get('notes') or [])})",
            font=font(13, bold=True), text_color=theme.TEXT, anchor="w",
        ).grid(row=0, column=0, sticky="w", padx=15, pady=(12, 6))
        notes = patient.get("notes") or []
        if notes:
            for index, note in enumerate(notes, start=1):
                note_frame = ctk.CTkFrame(notes_card, fg_color=theme.CARD_ALT, corner_radius=7)
                note_frame.grid(row=index, column=0, sticky="ew", padx=15, pady=(0, 6))
                ctk.CTkLabel(
                    note_frame, text=note, font=font(10), text_color=theme.TEXT_SECONDARY,
                    anchor="w", justify="left", wraplength=960,
                ).pack(fill="x", padx=11, pady=8)
        else:
            ctk.CTkLabel(
                notes_card, text="No clinical notes recorded for this patient.",
                font=font(10), text_color=theme.FAINT, anchor="w",
            ).grid(row=1, column=0, sticky="w", padx=15, pady=(0, 12))
        ctk.CTkFrame(notes_card, height=8, fg_color="transparent").grid(row=len(notes) + 1, column=0)

    def _save_note(self) -> None:
        note = self.note_box.get("1.0", "end").strip() if hasattr(self, "note_box") else ""
        if not note:
            self.app.toast("Please write a clinical note first.", error=True)
            return
        patient = self._patient()
        if not patient:
            return
        try:
            self.store.add_note(patient["id"], note)
        except Exception as error:
            self.app.toast(str(error), error=True)
            return
        self.show_tab("notes")

    # ----------------------------------------------------------------- transfer
    def _render_transfer(self, patient: dict) -> None:
        content = ctk.CTkFrame(self.content, fg_color="transparent")
        content.pack(fill="x", padx=18, pady=14)
        content.grid_columnconfigure(0, weight=1)

        card = Card(content)
        card.grid(row=0, column=0, sticky="ew")
        ctk.CTkLabel(
            card, text="Transfer Patient to Another Ward or Bed", font=font(14, bold=True),
            text_color=theme.TEXT, anchor="w",
        ).pack(fill="x", padx=16, pady=(14, 4))
        ctk.CTkLabel(
            card,
            text=f"Current location: {patient.get('bedNumber') or 'No bed'} ({patient.get('ward') or 'Outpatient'})",
            font=font(10), text_color=theme.MUTED, anchor="w",
        ).pack(fill="x", padx=16, pady=(0, 8))

        available = [b for b in self.store.beds if b.get("status") == "Available"]
        labels = [
            f"{bed.get('code')} · {bed.get('ward')} · {inr(bed.get('dailyRate'))}/day · {bed.get('floor')}"
            for bed in available
        ]
        self._transfer_beds = dict(zip(labels, available))
        if not labels:
            ctk.CTkLabel(
                card, text="No beds are currently available for transfer.",
                font=font(10), text_color=theme.AMBER, anchor="w",
            ).pack(fill="x", padx=16, pady=(8, 14))
            return

        wrapper = ctk.CTkFrame(card, fg_color="transparent")
        wrapper.pack(fill="x", padx=16, pady=(0, 14))
        ctk.CTkLabel(
            wrapper, text="Select new available bed", font=font(10, bold=True),
            text_color=theme.TEXT_SECONDARY, anchor="w",
        ).pack(fill="x", pady=(0, 4))
        self.transfer_option = ctk.CTkOptionMenu(
            wrapper, values=labels, height=34, corner_radius=6,
            fg_color=theme.CARD_ALT, button_color=theme.PRIMARY_SOFT,
            button_hover_color=theme.BORDER_STRONG, text_color=theme.TEXT,
            font=font(10), dropdown_font=font(10),
        )
        self.transfer_option.pack(fill="x")
        self.transfer_option.set(labels[0])
        primary_button(
            wrapper, "Execute Bed Transfer", self._do_transfer, height=32,
        ).pack(anchor="e", pady=(10, 0))
        ctk.CTkLabel(
            wrapper,
            text="The previous bed is automatically released to housekeeping / cleaning.",
            font=font(9), text_color=theme.FAINT, anchor="w",
        ).pack(fill="x", pady=(6, 0))

    def _do_transfer(self) -> None:
        patient = self._patient()
        if not patient:
            return
        bed = self._transfer_beds.get(self.transfer_option.get())
        if not bed:
            self.app.toast("Please select a target bed.", error=True)
            return
        try:
            self.store.transfer_bed(patient["id"], bed["id"])
        except Exception as error:
            self.app.toast(str(error), error=True)
            return
        self.show_tab("transfer")
        self.render()

    # ----------------------------------------------------------------- discharge
    def _render_discharge(self, patient: dict) -> None:
        content = ctk.CTkFrame(self.content, fg_color="transparent")
        content.pack(fill="x", padx=18, pady=14)
        content.grid_columnconfigure(0, weight=1)

        card = Card(content)
        card.grid(row=0, column=0, sticky="ew")
        ctk.CTkLabel(
            card, text="Patient Discharge Clearance", font=font(14, bold=True),
            text_color=theme.TEXT, anchor="w",
        ).pack(fill="x", padx=16, pady=(14, 4))

        if patient.get("status") == "Discharged":
            ctk.CTkLabel(
                card, text=f"Patient discharged on {patient.get('dischargeDate')}.",
                font=font(11), text_color=theme.EMERALD, anchor="w",
            ).pack(fill="x", padx=16, pady=(4, 16))
            return

        ctk.CTkLabel(
            card,
            text=(
                f"Discharging will mark the patient as Discharged, update the inpatient census and "
                f"release bed {patient.get('bedNumber') or '(none)'} for cleaning."
            ),
            font=font(10), text_color=theme.TEXT_SECONDARY, anchor="w",
            justify="left", wraplength=900,
        ).pack(fill="x", padx=16, pady=(0, 8))
        ctk.CTkLabel(
            card, text="Discharge summary & home care advice", font=font(10, bold=True),
            text_color=theme.TEXT_SECONDARY, anchor="w",
        ).pack(fill="x", padx=16, pady=(2, 4))
        self.discharge_box = ctk.CTkTextbox(
            card, height=140, corner_radius=6, border_width=1,
            border_color=theme.BORDER_STRONG, fg_color=theme.CARD_ALT,
            text_color=theme.TEXT, font=font(10),
        )
        self.discharge_box.pack(fill="x", padx=16, pady=(0, 10))
        danger_button(
            card, "Confirm Discharge & Release Bed", self._do_discharge,
            height=34, width=250,
        ).pack(anchor="e", padx=16, pady=(0, 16))

    def _do_discharge(self) -> None:
        patient = self._patient()
        if not patient:
            return
        summary = self.discharge_box.get("1.0", "end").strip() if hasattr(self, "discharge_box") else ""
        if not summary:
            self.app.toast("Please enter a clinical discharge summary.", error=True)
            return
        try:
            self.store.discharge_patient(patient["id"], summary)
        except Exception as error:
            self.app.toast(str(error), error=True)
            return
        self.close()

    # ------------------------------------------------------------------- actions
    def _generate_bill(self) -> None:
        patient = self._patient()
        if not patient:
            return
        self.app.open_invoice(patient_id=patient["id"])

    def close(self) -> None:
        try:
            self.grab_release()
        except Exception:
            pass
        self.destroy()
