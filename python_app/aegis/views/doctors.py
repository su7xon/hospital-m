"""Medical staff and consultant roster."""

from __future__ import annotations

from typing import Any

import customtkinter as ctk

from .. import theme
from ..widgets import (
    BaseView,
    Card,
    PageHeader,
    font,
    secondary_button,
    tinted_button,
)


class DoctorsView(BaseView):
    def __init__(self, master: Any, app: Any) -> None:
        super().__init__(master, app)
        self.grid_rowconfigure(2, weight=1)
        self._build()
        self.refresh()

    def _build(self) -> None:
        header = PageHeader(
            self,
            "Medical Staff & Consultant Roster",
            "Specialist clinicians, on-duty shifts and inpatient allocations.",
        )
        header.grid(row=0, column=0, sticky="ew", padx=18, pady=(14, 10))
        self.duty_label = ctk.CTkLabel(
            header.actions, text="", font=font(10, bold=True),
            text_color=theme.EMERALD, fg_color=theme.EMERALD_BG,
            corner_radius=6, padx=12, height=30,
        )
        self.duty_label.pack(side="right")

        filters = Card(self)
        filters.grid(row=1, column=0, sticky="ew", padx=18, pady=(0, 10))
        filters.grid_columnconfigure(0, weight=1)
        self.search = ctk.CTkEntry(
            filters,
            placeholder_text="Search by physician name, specialty or department...",
            height=33, corner_radius=6,
            fg_color=theme.CARD_ALT, border_color=theme.BORDER_STRONG,
            border_width=1, text_color=theme.TEXT, font=font(11),
            placeholder_text_color=theme.FAINT,
        )
        self.search.grid(row=0, column=0, sticky="ew", padx=12, pady=11)
        self.search.bind("<KeyRelease>", lambda _e: self.refresh())
        ctk.CTkLabel(
            filters, text="Department", font=font(10, bold=True), text_color=theme.MUTED,
        ).grid(row=0, column=1, padx=(0, 6))
        self.dept_filter = ctk.CTkOptionMenu(
            filters, values=["All Departments"], width=178, height=33, corner_radius=6,
            fg_color=theme.CARD_ALT, button_color=theme.PRIMARY_SOFT,
            button_hover_color=theme.BORDER_STRONG, text_color=theme.TEXT,
            font=font(10), dropdown_font=font(10),
            command=lambda _v: self.refresh(),
        )
        self.dept_filter.set("All Departments")
        self.dept_filter.grid(row=0, column=2, padx=(0, 12))

        self.scroll = ctk.CTkScrollableFrame(
            self, fg_color="transparent", corner_radius=0,
            scrollbar_button_color=theme.BORDER_STRONG,
            scrollbar_button_hover_color=theme.MUTED,
        )
        self.scroll.grid(row=2, column=0, sticky="nsew", padx=13, pady=(0, 12))
        self.grid_frame = ctk.CTkFrame(self.scroll, fg_color="transparent")
        self.grid_frame.pack(fill="both", expand=True)
        for column in range(3):
            self.grid_frame.grid_columnconfigure(column, weight=1, uniform="doctor_card")

    # ------------------------------------------------------------------ refresh
    def refresh(self) -> None:
        on_duty = len([d for d in self.store.doctors if d.get("onDuty")])
        self.duty_label.configure(text=f"{on_duty} of {len(self.store.doctors)} doctors on duty")

        departments = sorted({d.get("department", "") for d in self.store.doctors if d.get("department")})
        options = ["All Departments", *departments]
        selected = self.dept_filter.get()
        self.dept_filter.configure(values=options)
        if selected not in options:
            selected = "All Departments"
            self.dept_filter.set(selected)

        search = self.search.get().strip().lower()
        doctors = []
        for doctor in self.store.doctors:
            if selected != "All Departments" and doctor.get("department") != selected:
                continue
            haystack = " ".join([
                str(doctor.get("name", "")),
                str(doctor.get("specialty", "")),
                str(doctor.get("department", "")),
            ]).lower()
            if search and search not in haystack:
                continue
            doctors.append(doctor)

        for child in self.grid_frame.winfo_children():
            child.destroy()
        if not doctors:
            ctk.CTkLabel(
                self.grid_frame, text="No clinicians match the current filters.",
                font=font(12), text_color=theme.FAINT,
            ).grid(row=0, column=0, columnspan=3, pady=40)
            return

        for index, doctor in enumerate(doctors):
            card = self._doctor_card(doctor)
            card.grid(row=index // 3, column=index % 3, sticky="nsew", padx=5, pady=5)

    def _doctor_card(self, doctor: dict) -> Card:
        card = Card(self.grid_frame, corner_radius=10)
        card.grid_columnconfigure(0, weight=1)

        top = ctk.CTkFrame(card, fg_color="transparent")
        top.grid(row=0, column=0, sticky="ew", padx=14, pady=(12, 0))
        top.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(
            top, text=doctor.get("name", ""), font=font(13, bold=True),
            text_color=theme.TEXT, anchor="w",
        ).grid(row=0, column=0, sticky="w")
        on_duty = bool(doctor.get("onDuty"))
        tinted_button(
            top,
            "● On Floor" if on_duty else "○ Off Duty",
            lambda doctor_id=doctor.get("id"): self._toggle(doctor_id),
            color=theme.EMERALD if on_duty else theme.MUTED,
            bg=theme.EMERALD_BG if on_duty else theme.CARD_ALT,
            border=theme.EMERALD_BORDER if on_duty else theme.BORDER,
            height=25, width=86,
        ).grid(row=0, column=1, sticky="e")
        ctk.CTkLabel(
            top, text=doctor.get("qualification", ""), font=font(9),
            text_color=theme.MUTED, anchor="w", wraplength=250,
        ).grid(row=1, column=0, columnspan=2, sticky="w", pady=(1, 0))
        ctk.CTkLabel(
            top, text=doctor.get("specialty", ""), font=font(10, bold=True),
            text_color=theme.TEXT_SECONDARY, anchor="w", wraplength=250,
        ).grid(row=2, column=0, columnspan=2, sticky="w", pady=(4, 0))

        details = ctk.CTkFrame(card, fg_color=theme.CARD_ALT, corner_radius=7)
        details.grid(row=1, column=0, sticky="ew", padx=14, pady=(10, 0))
        details.grid_columnconfigure(1, weight=1)
        rows = [
            ("Department", doctor.get("department", "")),
            ("Clinic cabin", doctor.get("room", "")),
            ("Shift", doctor.get("scheduleHours", "")),
            ("Inpatients", f"{doctor.get('activePatients', 0)} under care"),
        ]
        for index, (label, value) in enumerate(rows):
            ctk.CTkLabel(
                details, text=label, font=font(9), text_color=theme.FAINT, anchor="w",
            ).grid(row=index, column=0, sticky="w", padx=(9, 10), pady=(4 if index == 0 else 1, 0))
            ctk.CTkLabel(
                details, text=str(value), font=font(9, bold=True, mono=index == 2),
                text_color=theme.TEXT_SECONDARY, anchor="w",
            ).grid(row=index, column=1, sticky="w", pady=(4 if index == 0 else 1, 0))

        ctk.CTkLabel(
            details, text=f"Phone: {doctor.get('phone', '')}", font=font(9, mono=True),
            text_color=theme.MUTED, anchor="w",
        ).grid(row=len(rows), column=0, columnspan=2, sticky="w", padx=9, pady=(5, 0))
        ctk.CTkLabel(
            details, text=f"Email: {doctor.get('email', '')}", font=font(9, mono=True),
            text_color=theme.MUTED, anchor="w",
        ).grid(row=len(rows) + 1, column=0, columnspan=2, sticky="w", padx=9, pady=(1, 7))

        secondary_button(
            card, "View Doctor Schedule",
            lambda doctor_id=doctor.get("id"): self.app.open_doctor_schedule(doctor_id),
            height=30,
        ).grid(row=2, column=0, sticky="ew", padx=14, pady=(10, 12))
        return card

    # ------------------------------------------------------------------ actions
    def _toggle(self, doctor_id: str) -> None:
        self.run_action(self.store.toggle_doctor_duty, doctor_id)
