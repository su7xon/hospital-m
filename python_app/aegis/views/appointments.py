"""Outpatient department scheduling."""

from __future__ import annotations

from typing import Any

import customtkinter as ctk

from .. import theme
from ..utils import compact_date, short, status_color
from ..widgets import (
    BaseView,
    Card,
    DataTable,
    PageHeader,
    PillTabs,
    StatCard,
    font,
    primary_button,
    secondary_button,
    tinted_button,
)

STATUSES = ["All", "Scheduled", "Checked-in", "In Consultation", "Completed", "Cancelled"]


class AppointmentsView(BaseView):
    def __init__(self, master: Any, app: Any) -> None:
        super().__init__(master, app)
        self.grid_rowconfigure(3, weight=1)
        self._doctor_map: dict[str, str] = {}
        self._build()
        self.refresh()

    def _build(self) -> None:
        header = PageHeader(
            self,
            "Outpatient Department Scheduling",
            "Specialist clinic bookings, patient queue management and consultation status.",
        )
        header.grid(row=0, column=0, sticky="ew", padx=18, pady=(14, 10))
        primary_button(header.actions, "+ Book New Appointment", self.app.open_appointment,
                       width=170).pack(side="right")

        stats = ctk.CTkFrame(self, fg_color="transparent")
        stats.grid(row=1, column=0, sticky="ew", padx=18, pady=(0, 10))
        for index in range(4):
            stats.grid_columnconfigure(index, weight=1, uniform="apt_stat")
        self.stat_scheduled = StatCard(stats, "Waiting / Scheduled", "0", "Pending arrival")
        self.stat_checked = StatCard(stats, "Checked-in at Clinic", "0", "In the waiting room",
                                      value_color=theme.BLUE)
        self.stat_consult = StatCard(stats, "In Consultation", "0", "Active with doctor",
                                      value_color=theme.AMBER)
        self.stat_completed = StatCard(stats, "Completed", "0", "Consultation closed",
                                       value_color=theme.EMERALD)
        for index, card in enumerate(
            [self.stat_scheduled, self.stat_checked, self.stat_consult, self.stat_completed]
        ):
            card.grid(row=0, column=index, sticky="nsew", padx=(0 if index == 0 else 5, 0 if index == 3 else 5))

        filters = Card(self)
        filters.grid(row=2, column=0, sticky="ew", padx=18, pady=(0, 10))
        filters.grid_columnconfigure(0, weight=1)

        top = ctk.CTkFrame(filters, fg_color="transparent")
        top.grid(row=0, column=0, sticky="ew", padx=12, pady=(11, 6))
        top.grid_columnconfigure(0, weight=1)

        self.search = ctk.CTkEntry(
            top,
            placeholder_text="Search by patient name, phone, appointment number or doctor...",
            height=33, corner_radius=6,
            fg_color=theme.CARD_ALT, border_color=theme.BORDER_STRONG,
            border_width=1, text_color=theme.TEXT, font=font(11),
            placeholder_text_color=theme.FAINT,
        )
        self.search.grid(row=0, column=0, sticky="ew", padx=(0, 14))
        self.search.bind("<KeyRelease>", lambda _e: self.refresh())

        ctk.CTkLabel(
            top, text="Doctor", font=font(10, bold=True), text_color=theme.MUTED,
        ).grid(row=0, column=1, padx=(0, 6))
        self.doctor_filter = ctk.CTkOptionMenu(
            top,
            values=["All Specialists"],
            width=220, height=33, corner_radius=6,
            fg_color=theme.CARD_ALT, button_color=theme.PRIMARY_SOFT,
            button_hover_color=theme.BORDER_STRONG, text_color=theme.TEXT,
            font=font(10), dropdown_font=font(10),
            command=lambda _v: self.refresh(),
        )
        self.doctor_filter.set("All Specialists")
        self.doctor_filter.grid(row=0, column=2)

        self.status_tabs = PillTabs(
            filters, STATUSES,
            command=lambda _v: self.refresh(),
            value="All",
        )
        self.status_tabs.grid(row=1, column=0, sticky="w", padx=12, pady=(4, 11))

        table_card = Card(self)
        table_card.grid(row=3, column=0, sticky="nsew", padx=18, pady=(0, 12))
        table_card.grid_rowconfigure(0, weight=1)
        table_card.grid_columnconfigure(0, weight=1)

        columns = [
            {"key": "slot", "title": "Slot / Appointment", "width": 180, "stretch": False},
            {"key": "patient", "title": "Patient Details", "width": 200},
            {"key": "doctor", "title": "Attending Specialist", "width": 170},
            {"key": "reason", "title": "Clinical Reason / Type", "width": 270},
            {"key": "status", "title": "Queue Status", "width": 115, "stretch": False, "anchor": "center"},
        ]
        self.table = DataTable(
            table_card, columns, height=12,
            on_double_click=self._open_linked_patient,
            empty_text="No appointments match the selected criteria.",
        )
        self.table.grid(row=0, column=0, sticky="nsew", padx=1, pady=(1, 0))

        footer = ctk.CTkFrame(table_card, fg_color="transparent")
        footer.grid(row=1, column=0, sticky="ew", padx=12, pady=7)
        hint = ctk.CTkLabel(
            footer, text="Select a row, then move the patient through the OPD queue.",
            font=font(9), text_color=theme.FAINT, anchor="w",
        )
        hint.pack(side="left")
        secondary_button(footer, "Open Chart", self._open_selected_patient, height=28).pack(side="right", padx=(6, 0))
        secondary_button(footer, "Cancel", lambda: self._set_status("Cancelled"), height=28).pack(side="right", padx=(6, 0))
        tinted_button(footer, "Complete", lambda: self._set_status("Completed"), height=28).pack(side="right", padx=(6, 0))
        tinted_button(footer, "Start Consultation", lambda: self._set_status("In Consultation"),
                      color=theme.AMBER, bg=theme.AMBER_BG, border=theme.AMBER_BORDER,
                      height=28).pack(side="right", padx=(6, 0))
        tinted_button(footer, "Check-in", lambda: self._set_status("Checked-in"),
                      color=theme.BLUE, bg=theme.BLUE_BG, border=theme.BLUE_BORDER,
                      height=28).pack(side="right")

    # ------------------------------------------------------------------ refresh
    def refresh(self) -> None:
        doctors = self.store.doctors
        self._doctor_map = {f"{d.get('name')} · {d.get('department')}": d["id"] for d in doctors}
        options = ["All Specialists", *self._doctor_map.keys()]
        selected_doctor = self.doctor_filter.get()
        self.doctor_filter.configure(values=options)
        if selected_doctor not in options:
            selected_doctor = "All Specialists"
            self.doctor_filter.set(selected_doctor)
        doctor_id = self._doctor_map.get(selected_doctor)

        counts = {key: 0 for key in STATUSES}
        counts["All"] = len(self.store.appointments)
        for appointment in self.store.appointments:
            appointment_status = appointment.get("status", "")
            if appointment_status in counts:
                counts[appointment_status] += 1
        self.status_tabs.refresh_options(
            [(key, f"{key}  {counts.get(key, 0)}") for key in STATUSES]
        )
        status = self.status_tabs.get() or "All"
        search = self.search.get().strip().lower()

        self.stat_scheduled.update(str(counts.get("Scheduled", 0)), "Pending arrival")
        self.stat_checked.update(str(counts.get("Checked-in", 0)), "In the waiting room")
        self.stat_consult.update(str(counts.get("In Consultation", 0)), "Active with doctor")
        self.stat_completed.update(str(counts.get("Completed", 0)), "Consultation closed")

        filtered = []
        for appointment in self.store.appointments:
            haystack = " ".join([
                str(appointment.get("patientName", "")),
                str(appointment.get("patientPhone", "")),
                str(appointment.get("appointmentNumber", "")),
                str(appointment.get("doctorName", "")),
                str(appointment.get("reason", "")),
            ]).lower()
            if search and search not in haystack:
                continue
            if doctor_id and appointment.get("doctorId") != doctor_id:
                continue
            if status != "All" and appointment.get("status") != status:
                continue
            filtered.append(appointment)

        rows = []
        for appointment in filtered:
            status_value = appointment.get("status", "")
            rows.append({
                "iid": appointment["id"],
                "record": appointment,
                "values": (
                    f"{appointment.get('timeSlot')} · {compact_date(appointment.get('date'), with_year=False)}"
                    f" · {appointment.get('appointmentNumber')}",
                    f"{appointment.get('patientName')} · {appointment.get('patientMrn') or 'Walk-in'}",
                    f"{appointment.get('doctorName')}",
                    f"{short(appointment.get('reason', ''), 34)}\n{appointment.get('type', '')} consultation",
                    status_value,
                ),
                "tags": [status_color(status_value)],
            })

        # Treeview rows are single line; flatten the two-line values for clarity.
        for row in rows:
            row["values"] = tuple(str(value).replace("\n", " · ") for value in row["values"])
        self.table.set_rows(rows)

    # ------------------------------------------------------------------ actions
    def focus_doctor(self, doctor_id: str) -> None:
        """Filter the OPD roster to one consultant (used by the roster screen)."""
        doctor = self.store.doctor(doctor_id)
        if not doctor:
            return
        label = f"{doctor.get('name')} · {doctor.get('department')}"
        self.search.delete(0, "end")
        self.status_tabs.set("All", notify=False)
        self.doctor_filter.set(label)
        self.refresh()

    def _selected(self) -> dict | None:
        appointment = self.table.selected_record()
        if not appointment:
            self.app.toast("Select an appointment row first.", error=True)
            return None
        return appointment

    def _set_status(self, status: str) -> None:
        appointment = self._selected()
        if not appointment:
            return
        self.run_action(self.store.update_appointment_status, appointment["id"], status)

    def _open_selected_patient(self) -> None:
        appointment = self._selected()
        if not appointment:
            return
        patient = self._linked_patient(appointment)
        if patient:
            self.app.open_patient(patient["id"])
        else:
            self.app.toast("No linked patient record for this walk-in appointment.", error=True)

    def _open_linked_patient(self, appointment_id: str) -> None:
        appointment = next((a for a in self.store.appointments if a.get("id") == appointment_id), None)
        if not appointment:
            return
        patient = self._linked_patient(appointment)
        if patient:
            self.app.open_patient(patient["id"])
        else:
            self.app.toast("No linked patient record for this walk-in appointment.", error=True)

    def _linked_patient(self, appointment: dict) -> dict | None:
        mrn = appointment.get("patientMrn")
        name = appointment.get("patientName")
        return next(
            (p for p in self.store.patients if (mrn and p.get("mrn") == mrn) or p.get("name") == name),
            None,
        )
