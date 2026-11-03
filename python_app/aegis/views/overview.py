"""Clinical operations overview dashboard."""

from __future__ import annotations

from typing import Any

import customtkinter as ctk

from .. import theme
from ..utils import short
from ..widgets import (
    BaseView,
    Card,
    PageHeader,
    StatCard,
    font,
    primary_button,
    secondary_button,
    tinted_button,
)


def _clear(frame: ctk.CTkFrame) -> None:
    for child in frame.winfo_children():
        child.destroy()


def _badge_color(prefix: str) -> tuple[str, str, str]:
    if prefix == "P1":
        return theme.ROSE, theme.ROSE_BG, theme.ROSE_BORDER
    if prefix == "P2":
        return theme.AMBER, theme.AMBER_BG, theme.AMBER_BORDER
    if prefix == "P3":
        return theme.BLUE, theme.BLUE_BG, theme.BLUE_BORDER
    return theme.MUTED, theme.CARD_ALT, theme.BORDER


class OverviewView(BaseView):
    def __init__(self, master: Any, app: Any) -> None:
        super().__init__(master, app)
        self._build()
        self.refresh()

    def _build(self) -> None:
        scroll = ctk.CTkScrollableFrame(
            self,
            fg_color=theme.BG,
            corner_radius=0,
            scrollbar_button_color=theme.BORDER_STRONG,
            scrollbar_button_hover_color=theme.MUTED,
        )
        scroll.pack(fill="both", expand=True)
        content = ctk.CTkFrame(scroll, fg_color="transparent")
        content.pack(fill="x", padx=18, pady=14)
        content.grid_columnconfigure(0, weight=1)

        header = PageHeader(
            content,
            "Clinical Operations Center",
            "Real-time floor occupancy, emergency triage, OPD rosters and ward status.",
        )
        header.grid(row=0, column=0, sticky="ew", pady=(0, 14))
        secondary_button(header.actions, "Log ER Intake", self.app.open_emergency).pack(side="left", padx=(0, 6))
        secondary_button(header.actions, "Book OPD", self.app.open_appointment).pack(side="left", padx=(0, 6))
        primary_button(header.actions, "+ Admit Patient", self.app.open_admit, width=136).pack(side="left")

        stats = ctk.CTkFrame(content, fg_color="transparent")
        stats.grid(row=1, column=0, sticky="ew", pady=(0, 14))
        for column in range(6):
            stats.grid_columnconfigure(column, weight=1, uniform="overview_stat")
        self.stat_census = StatCard(stats, "Admitted Census", "0", "Active inpatients")
        self.stat_beds = StatCard(stats, "Bed Occupancy", "0%", "0 / 0 beds", value_color=theme.TEXT)
        self.stat_er = StatCard(stats, "ER Triage Queue", "0", "No active cases", value_color=theme.ROSE)
        self.stat_opd = StatCard(stats, "OPD Roster", "0", "Consultations booked")
        self.stat_doctors = StatCard(stats, "Doctors on Floor", "0", "of 0 specialists")
        self.stat_pharmacy = StatCard(stats, "Pharmacy Alerts", "0", "Stock below threshold", value_color=theme.AMBER)
        for index, card in enumerate(
            [self.stat_census, self.stat_beds, self.stat_er,
             self.stat_opd, self.stat_doctors, self.stat_pharmacy]
        ):
            card.grid(row=0, column=index, sticky="nsew", padx=(0 if index == 0 else 5, 0 if index == 5 else 5))

        middle = ctk.CTkFrame(content, fg_color="transparent")
        middle.grid(row=2, column=0, sticky="nsew", pady=(0, 14))
        middle.grid_columnconfigure(0, weight=2, uniform="overview_mid")
        middle.grid_columnconfigure(1, weight=1, uniform="overview_mid")

        er_card = Card(middle)
        er_card.grid(row=0, column=0, sticky="nsew", padx=(0, 7))
        er_card.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(
            er_card, text="Emergency Triage Department (ER)",
            font=font(14, bold=True), text_color=theme.TEXT, anchor="w",
        ).grid(row=0, column=0, sticky="ew", padx=16, pady=(14, 0))
        ctk.CTkLabel(
            er_card, text="Manchester Triage System · P1 through P5",
            font=font(10), text_color=theme.MUTED, anchor="w",
        ).grid(row=1, column=0, sticky="ew", padx=16, pady=(1, 10))
        self.er_list = ctk.CTkFrame(er_card, fg_color="transparent")
        self.er_list.grid(row=2, column=0, sticky="ew", padx=16, pady=(0, 14))
        self.er_list.grid_columnconfigure(0, weight=1)

        ward_card = Card(middle)
        ward_card.grid(row=0, column=1, sticky="nsew")
        ctk.CTkLabel(
            ward_card, text="Ward Occupancy",
            font=font(14, bold=True), text_color=theme.TEXT, anchor="w",
        ).grid(row=0, column=0, sticky="ew", padx=16, pady=(14, 0))
        ctk.CTkLabel(
            ward_card, text="Live bed inventory by clinical ward",
            font=font(10), text_color=theme.MUTED, anchor="w",
        ).grid(row=1, column=0, sticky="ew", padx=16, pady=(1, 10))
        self.ward_list = ctk.CTkFrame(ward_card, fg_color="transparent")
        self.ward_list.grid(row=2, column=0, sticky="ew", padx=16)
        self.ward_list.grid_columnconfigure(0, weight=1)
        self.ward_footer = ctk.CTkLabel(
            ward_card, text="", font=font(10), text_color=theme.MUTED, anchor="w",
        )
        self.ward_footer.grid(row=3, column=0, sticky="ew", padx=16, pady=(10, 14))

        bottom = ctk.CTkFrame(content, fg_color="transparent")
        bottom.grid(row=3, column=0, sticky="nsew", pady=(0, 14))
        bottom.grid_columnconfigure(0, weight=1, uniform="overview_bottom")
        bottom.grid_columnconfigure(1, weight=1, uniform="overview_bottom")

        opd_card = Card(bottom)
        opd_card.grid(row=0, column=0, sticky="nsew", padx=(0, 7))
        opd_card.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(
            opd_card, text="Outpatient Clinic (OPD)",
            font=font(14, bold=True), text_color=theme.TEXT, anchor="w",
        ).grid(row=0, column=0, sticky="ew", padx=16, pady=(14, 0))
        ctk.CTkLabel(
            opd_card, text="Consultation queue and doctor assignments",
            font=font(10), text_color=theme.MUTED, anchor="w",
        ).grid(row=1, column=0, sticky="ew", padx=16, pady=(1, 8))
        self.opd_list = ctk.CTkFrame(opd_card, fg_color="transparent")
        self.opd_list.grid(row=2, column=0, sticky="ew", padx=16, pady=(0, 14))
        self.opd_list.grid_columnconfigure(0, weight=1)

        census_card = Card(bottom)
        census_card.grid(row=0, column=1, sticky="nsew")
        census_card.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(
            census_card, text="Inpatient Census",
            font=font(14, bold=True), text_color=theme.TEXT, anchor="w",
        ).grid(row=0, column=0, sticky="ew", padx=16, pady=(14, 0))
        ctk.CTkLabel(
            census_card, text="Currently admitted patients requiring monitoring",
            font=font(10), text_color=theme.MUTED, anchor="w",
        ).grid(row=1, column=0, sticky="ew", padx=16, pady=(1, 8))
        self.census_list = ctk.CTkFrame(census_card, fg_color="transparent")
        self.census_list.grid(row=2, column=0, sticky="ew", padx=16, pady=(0, 14))
        self.census_list.grid_columnconfigure(0, weight=1)

        self.alerts = ctk.CTkFrame(
            content, fg_color=theme.AMBER_BG, border_width=1,
            border_color=theme.AMBER_BORDER, corner_radius=10,
        )
        self.alerts.grid(row=4, column=0, sticky="ew")
        self.alerts.grid_columnconfigure(0, weight=1)
        self.alerts_label = ctk.CTkLabel(
            self.alerts, text="", font=font(11), text_color=theme.AMBER, anchor="w",
        )
        self.alerts_label.grid(row=0, column=0, sticky="ew", padx=14, pady=12)
        tinted_button(
            self.alerts, "Review inventory", self.app.navigate_pharmacy,
            color=theme.AMBER, bg=theme.CARD, border=theme.AMBER_BORDER,
            height=28,
        ).grid(row=0, column=1, padx=10, pady=8)

    # ------------------------------------------------------------------ refresh
    def refresh(self) -> None:
        patients = self.store.patients
        beds = self.store.beds
        er_cases = self.store.emergency_cases
        appointments = self.store.appointments
        doctors = self.store.doctors
        medicines = self.store.medicines
        labs = self.store.lab_orders

        admitted = [p for p in patients if p.get("status") in ("Admitted", "ICU")]
        icu = [p for p in patients if p.get("status") == "ICU"]
        occupied = [b for b in beds if b.get("status") == "Occupied"]
        available = [b for b in beds if b.get("status") == "Available"]
        cleaning = [b for b in beds if b.get("status") == "Cleaning"]
        total_beds = len(beds)
        occupancy = round(len(occupied) / total_beds * 100) if total_beds else 0

        active_er = [e for e in er_cases if e.get("status") in ("Waiting", "In Treatment")]
        critical = [e for e in er_cases if str(e.get("triageLevel", "")).startswith("P1")
                    and e.get("status") != "Discharged"]
        on_duty = [d for d in doctors if d.get("onDuty")]
        low_stock = [m for m in medicines if int(m.get("stock", 0)) <= int(m.get("minStock", 0))]
        stat_labs = [l for l in labs if l.get("priority") == "STAT Urgent" and l.get("status") != "Completed"]

        self.stat_census.update(str(len(admitted)), f"{len(icu)} in intensive care")
        self.stat_beds.update(
            f"{occupancy}%",
            f"{len(occupied)} / {total_beds} beds · {len(available)} free",
            theme.ROSE if occupancy >= 90 else theme.TEXT,
        )
        self.stat_er.update(
            str(len(active_er)),
            f"{len(critical)} critical P1 · {len(er_cases)} total logged",
            theme.ROSE if active_er else theme.EMERALD,
        )
        self.stat_opd.update(
            str(len(appointments)),
            f"{len([a for a in appointments if a.get('status') == 'Completed'])} completed · "
            f"{len([a for a in appointments if a.get('status') == 'Scheduled'])} scheduled",
        )
        self.stat_doctors.update(str(len(on_duty)), f"of {len(doctors)} specialists")
        self.stat_pharmacy.update(
            str(len(low_stock)),
            f"{len(stat_labs)} STAT lab requisition{'s' if len(stat_labs) != 1 else ''}",
            theme.AMBER if low_stock else theme.EMERALD,
        )

        self._render_er(active_er, er_cases)
        self._render_wards(beds, len(occupied), len(available))
        self._render_opd(appointments)
        self._render_census(admitted)

        if low_stock or stat_labs:
            self.alerts.grid()
            parts = []
            if low_stock:
                parts.append(
                    f"{len(low_stock)} medicine(s) below minimum stock: "
                    + ", ".join(short(m.get("name", ""), 28) for m in low_stock[:3])
                )
            if stat_labs:
                parts.append(f"{len(stat_labs)} STAT lab requisition(s) awaiting completion")
            self.alerts_label.configure(text="Hospital inventory action required · " + " · ".join(parts))
        else:
            self.alerts.grid_remove()

        if cleaning:
            self.ward_footer.configure(
                text=f"{len(occupied)} occupied · {len(available)} available · {len(cleaning)} awaiting housekeeping"
            )
        else:
            self.ward_footer.configure(text=f"{len(occupied)} occupied · {len(available)} available")

    def _render_er(self, active_er: list[dict], all_er: list[dict]) -> None:
        _clear(self.er_list)
        cases = all_er[:4]
        if not cases:
            ctk.CTkLabel(
                self.er_list, text="No emergency cases in triage.",
                font=font(11), text_color=theme.FAINT, anchor="w",
            ).grid(row=0, column=0, sticky="ew", pady=20)
            return

        for index, case in enumerate(cases):
            row = ctk.CTkFrame(self.er_list, fg_color="transparent")
            row.grid(row=index * 2, column=0, sticky="ew", pady=(0, 0))
            row.grid_columnconfigure(1, weight=1)

            triage = str(case.get("triageLevel", ""))
            prefix = triage[:2]
            color, bg, border = _badge_color(prefix)
            ctk.CTkLabel(
                row, text=triage, font=font(9, bold=True),
                text_color=color, fg_color=bg, corner_radius=5,
                padx=7, height=22,
            ).grid(row=0, column=0, sticky="nw", padx=(0, 9), pady=(8, 0))

            info = ctk.CTkFrame(row, fg_color="transparent")
            info.grid(row=0, column=1, sticky="ew")
            info.grid_columnconfigure(0, weight=1)
            name_line = ctk.CTkFrame(info, fg_color="transparent")
            name_line.grid(row=0, column=0, sticky="ew")
            ctk.CTkLabel(
                name_line,
                text=f"{case.get('patientName')}  ({case.get('age')}y / {str(case.get('gender', ''))[:1]})",
                font=font(11, bold=True), text_color=theme.TEXT, anchor="w",
            ).pack(side="left")
            ctk.CTkLabel(
                name_line, text=f"  ·  Arr {case.get('arrivalTime')}",
                font=font(9, mono=True), text_color=theme.MUTED, anchor="w",
            ).pack(side="left")
            ctk.CTkLabel(
                info, text=short(case.get("chiefComplaint", ""), 90),
                font=font(10), text_color=theme.TEXT_SECONDARY, anchor="w",
            ).grid(row=1, column=0, sticky="ew", pady=(1, 0))
            ctk.CTkLabel(
                info,
                text=f"{case.get('vitalsBrief', '')}  ·  {case.get('assignedDoctor', '')}",
                font=font(9, mono=True), text_color=theme.FAINT, anchor="w",
            ).grid(row=2, column=0, sticky="ew", pady=(1, 7))

            actions = ctk.CTkFrame(row, fg_color="transparent")
            actions.grid(row=0, column=2, sticky="e", padx=(8, 0), pady=(6, 0))
            status_menu = ctk.CTkOptionMenu(
                actions,
                values=["Waiting", "In Treatment", "Admitted", "Discharged"],
                width=120, height=27, corner_radius=6,
                fg_color=theme.CARD_ALT, button_color=theme.PRIMARY_SOFT,
                button_hover_color=theme.BORDER_STRONG, text_color=theme.TEXT,
                font=font(9), dropdown_font=font(10),
                command=lambda value, er_id=case.get("id"): self.after(
                    15, lambda: self._update_er_status(er_id, value)
                ),
            )
            status_menu.set(case.get("status", "Waiting"))
            status_menu.pack(side="left", padx=(0, 5))
            if case.get("status") not in ("Admitted", "Discharged"):
                tinted_button(
                    actions, "Admit to Bed", 
                    lambda er_id=case.get("id"): self.after(10, lambda: self._admit_er(er_id)),
                    color=theme.TEXT_SECONDARY, bg=theme.CARD_ALT, border=theme.BORDER_STRONG,
                    height=27,
                ).pack(side="left")

            if index < len(cases) - 1:
                ctk.CTkFrame(self.er_list, height=1, fg_color=theme.BORDER).grid(
                    row=index * 2 + 1, column=0, sticky="sew", pady=(0, 1)
                )

    def _render_wards(self, beds: list[dict], occupied: int, available: int) -> None:
        _clear(self.ward_list)
        wards = [
            ("ICU (Intensive Care)", "ICU"),
            ("General Ward A (Male)", "General Ward A"),
            ("General Ward B (Female)", "General Ward B"),
            ("Private Suites", "Private Suite"),
            ("Emergency Care Bay", "Emergency Care"),
        ]
        for index, (label, ward) in enumerate(wards):
            ward_beds = [b for b in beds if b.get("ward") == ward]
            total = len(ward_beds)
            occ = len([b for b in ward_beds if b.get("status") == "Occupied"])
            avail = len([b for b in ward_beds if b.get("status") == "Available"])
            clean = len([b for b in ward_beds if b.get("status") == "Cleaning"])
            pct = round(occ / total * 100) if total else 0

            line = ctk.CTkFrame(self.ward_list, fg_color="transparent")
            line.grid(row=index * 3, column=0, sticky="ew", pady=(0, 2))
            line.grid_columnconfigure(0, weight=1)
            ctk.CTkLabel(
                line, text=label, font=font(10, bold=True),
                text_color=theme.TEXT_SECONDARY, anchor="w",
            ).grid(row=0, column=0, sticky="w")
            ctk.CTkLabel(
                line, text=f"{occ}/{total} · {pct}%", font=font(9, mono=True),
                text_color=theme.MUTED, anchor="e",
            ).grid(row=0, column=1, sticky="e")

            bar = ctk.CTkProgressBar(
                self.ward_list, height=7, corner_radius=4,
                fg_color=theme.PRIMARY_SOFT, progress_color=theme.PRIMARY,
            )
            bar.grid(row=index * 3 + 1, column=0, sticky="ew", pady=(0, 2))
            bar.set(pct / 100)
            if clean:
                ctk.CTkLabel(
                    self.ward_list,
                    text=f"{avail} available · {clean} cleaning",
                    font=font(9), text_color=theme.AMBER, anchor="w",
                ).grid(row=index * 3 + 2, column=0, sticky="w", padx=1, pady=(0, 8))
            else:
                ctk.CTkLabel(
                    self.ward_list,
                    text=f"{avail} available",
                    font=font(9), text_color=theme.FAINT, anchor="w",
                ).grid(row=index * 3 + 2, column=0, sticky="w", padx=1, pady=(0, 8))

    def _render_opd(self, appointments: list[dict]) -> None:
        _clear(self.opd_list)
        items = appointments[:5]
        if not items:
            ctk.CTkLabel(
                self.opd_list, text="No outpatient appointments booked.",
                font=font(11), text_color=theme.FAINT, anchor="w",
            ).grid(row=0, column=0, sticky="ew", pady=20)
            return

        for index, appointment in enumerate(items):
            row = ctk.CTkFrame(self.opd_list, fg_color="transparent")
            row.grid(row=index * 2, column=0, sticky="ew", pady=(2, 2))
            row.grid_columnconfigure(0, weight=1)
            top = ctk.CTkFrame(row, fg_color="transparent")
            top.grid(row=0, column=0, sticky="ew")
            ctk.CTkLabel(
                top, text=appointment.get("patientName", ""), font=font(10, bold=True),
                text_color=theme.TEXT, anchor="w",
            ).pack(side="left")
            ctk.CTkLabel(
                top, text=f"  {appointment.get('timeSlot', '')}  ·  {appointment.get('type', '')}",
                font=font(9, mono=True), text_color=theme.MUTED, anchor="w",
            ).pack(side="left")
            ctk.CTkLabel(
                row,
                text=f"{appointment.get('doctorName', '')} · {appointment.get('department', '')}",
                font=font(9), text_color=theme.FAINT, anchor="w",
            ).grid(row=1, column=0, sticky="ew")

            status_menu = ctk.CTkOptionMenu(
                row,
                values=["Scheduled", "Checked-in", "In Consultation", "Completed", "Cancelled"],
                width=112, height=25, corner_radius=6,
                fg_color=theme.CARD_ALT, button_color=theme.PRIMARY_SOFT,
                button_hover_color=theme.BORDER_STRONG, text_color=theme.TEXT,
                font=font(9), dropdown_font=font(9),
                command=lambda value, apt_id=appointment.get("id"): self.after(
                    15, lambda: self._update_appointment(apt_id, value)
                ),
            )
            status_menu.set(appointment.get("status", "Scheduled"))
            status_menu.grid(row=0, column=1, rowspan=2, sticky="e", padx=(6, 0))
            if index < len(items) - 1:
                ctk.CTkFrame(self.opd_list, height=1, fg_color=theme.BORDER).grid(
                    row=index * 2 + 1, column=0, sticky="sew"
                )

    def _render_census(self, admitted: list[dict]) -> None:
        _clear(self.census_list)
        patients = admitted[:5]
        if not patients:
            ctk.CTkLabel(
                self.census_list, text="No active inpatients.",
                font=font(11), text_color=theme.FAINT, anchor="w",
            ).grid(row=0, column=0, sticky="ew", pady=20)
            return

        for index, patient in enumerate(patients):
            row = ctk.CTkFrame(self.census_list, fg_color="transparent")
            row.grid(row=index * 2, column=0, sticky="ew", pady=(3, 3))
            row.grid_columnconfigure(0, weight=1)
            name = ctk.CTkButton(
                row,
                text=patient.get("name", ""),
                font=font(10, bold=True),
                text_color=theme.TEXT,
                fg_color="transparent", hover_color=theme.CARD_HOVER,
                anchor="w", height=18, corner_radius=2,
                command=lambda pid=patient.get("id"): self.app.open_patient(pid),
            )
            name.grid(row=0, column=0, sticky="w")
            ctk.CTkLabel(
                row,
                text=f"{patient.get('mrn')} · {patient.get('bedNumber') or 'No bed'} · {patient.get('ward') or ''}",
                font=font(9, mono=True), text_color=theme.MUTED, anchor="w",
            ).grid(row=1, column=0, sticky="ew")
            vital = (patient.get("vitals") or [None])[0]
            if vital:
                vitals_text = f"HR {vital.get('heartRate')} · BP {vital.get('bloodPressure')} · SpO2 {vital.get('spo2')}%"
            else:
                vitals_text = "No vitals recorded"
            ctk.CTkLabel(
                row, text=vitals_text, font=font(9, mono=True),
                text_color=theme.FAINT, anchor="e",
            ).grid(row=0, column=1, rowspan=2, sticky="e", padx=(8, 0))
            ctk.CTkLabel(
                row, text=patient.get("assignedDoctorName", ""), font=font(9),
                text_color=theme.MUTED, anchor="e",
            ).grid(row=2, column=1, sticky="e")
            if index < len(patients) - 1:
                ctk.CTkFrame(self.census_list, height=1, fg_color=theme.BORDER).grid(
                    row=index * 2 + 1, column=0, sticky="sew"
                )

    # ------------------------------------------------------------------ actions
    def _update_er_status(self, er_id: str, status: str) -> None:
        self.run_action(self.store.update_emergency_status, er_id, status)

    def _admit_er(self, er_id: str) -> None:
        self.run_action(self.store.admit_emergency_case, er_id)

    def _update_appointment(self, appointment_id: str, status: str) -> None:
        self.run_action(self.store.update_appointment_status, appointment_id, status)
