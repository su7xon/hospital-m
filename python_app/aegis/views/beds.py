"""Bed and ward allocation management."""

from __future__ import annotations

from tkinter import messagebox
from typing import Any

import customtkinter as ctk

from .. import theme
from ..utils import inr, short, status_color
from ..widgets import (
    BaseView,
    Card,
    PageHeader,
    PillTabs,
    StatCard,
    font,
    primary_button,
    secondary_button,
    tinted_button,
    danger_button,
)

WARDS = [
    ("All Wards", "All Wards"),
    ("ICU (Intensive Care)", "ICU"),
    ("General Ward A (Male)", "General Ward A"),
    ("General Ward B (Female)", "General Ward B"),
    ("Private Suites", "Private Suite"),
    ("Emergency Care Bay", "Emergency Care"),
]
STATUSES = ["All", "Available", "Occupied", "Cleaning", "Maintenance"]


class BedsView(BaseView):
    def __init__(self, master: Any, app: Any) -> None:
        super().__init__(master, app)
        self.grid_rowconfigure(3, weight=1)
        self._build()
        self.refresh()

    def _build(self) -> None:
        header = PageHeader(
            self,
            "Bed & Ward Allocation",
            "Live inpatient bed inventory, housekeeping cycle and occupancy status.",
        )
        header.grid(row=0, column=0, sticky="ew", padx=18, pady=(14, 10))
        primary_button(header.actions, "+ Admit Patient to Bed", self.app.open_admit, width=178).pack(side="right")

        stats = ctk.CTkFrame(self, fg_color="transparent")
        stats.grid(row=1, column=0, sticky="ew", padx=18, pady=(0, 10))
        for index in range(5):
            stats.grid_columnconfigure(index, weight=1, uniform="bed_stat")
        self.stat_total = StatCard(stats, "Total Hospital Beds", "0", "Operational capacity")
        self.stat_occupied = StatCard(stats, "Occupied Beds", "0", "0% occupancy")
        self.stat_available = StatCard(stats, "Available (Ready)", "0", "Immediate intake ready",
                                       value_color=theme.EMERALD)
        self.stat_cleaning = StatCard(stats, "Disinfection / Cleaning", "0", "Sanitization in progress",
                                      value_color=theme.AMBER)
        self.stat_maintenance = StatCard(stats, "Maintenance", "0", "Biomedical repair",
                                         value_color=theme.MUTED)
        for index, card in enumerate(
            [self.stat_total, self.stat_occupied, self.stat_available,
             self.stat_cleaning, self.stat_maintenance]
        ):
            card.grid(row=0, column=index, sticky="nsew", padx=(0 if index == 0 else 5, 0 if index == 4 else 5))

        filters = Card(self)
        filters.grid(row=2, column=0, sticky="ew", padx=18, pady=(0, 10))
        filters.grid_columnconfigure(0, weight=1)

        self.ward_tabs = PillTabs(
            filters,
            [(value, label) for label, value in WARDS],
            command=lambda _v: self.refresh(),
            value="All Wards",
        )
        self.ward_tabs.grid(row=0, column=0, sticky="w", padx=12, pady=(10, 5))

        status_row = ctk.CTkFrame(filters, fg_color="transparent")
        status_row.grid(row=1, column=0, sticky="ew", padx=12, pady=(4, 10))
        ctk.CTkLabel(
            status_row, text="Status", font=font(10, bold=True), text_color=theme.MUTED,
        ).pack(side="left", padx=(0, 8))
        self.status_tabs = PillTabs(
            status_row, STATUSES,
            command=lambda _v: self.refresh(),
            value="All",
        )
        self.status_tabs.pack(side="left")

        self.bed_scroll = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent",
            corner_radius=0,
            scrollbar_button_color=theme.BORDER_STRONG,
            scrollbar_button_hover_color=theme.MUTED,
        )
        self.bed_scroll.grid(row=3, column=0, sticky="nsew", padx=13, pady=(0, 12))
        self.bed_grid = ctk.CTkFrame(self.bed_scroll, fg_color="transparent")
        self.bed_grid.pack(fill="both", expand=True)
        for column in range(4):
            self.bed_grid.grid_columnconfigure(column, weight=1, uniform="bed_card")

    # ------------------------------------------------------------------ refresh
    def refresh(self) -> None:
        beds = self.store.beds
        total = len(beds)
        occupied = len([b for b in beds if b.get("status") == "Occupied"])
        available = len([b for b in beds if b.get("status") == "Available"])
        cleaning = len([b for b in beds if b.get("status") == "Cleaning"])
        maintenance = len([b for b in beds if b.get("status") == "Maintenance"])

        self.stat_total.update(str(total), "Operational capacity")
        self.stat_occupied.update(
            str(occupied),
            f"{round(occupied / total * 100) if total else 0}% occupancy rate",
        )
        self.stat_available.update(str(available), "Immediate intake ready")
        self.stat_cleaning.update(str(cleaning), "Sanitization in progress")
        self.stat_maintenance.update(str(maintenance), "Biomedical repair")

        self.ward_tabs.refresh_options(
            [(value, f"{label}  {len([b for b in beds if value == 'All Wards' or b.get('ward') == value])}")
             for label, value in WARDS]
        )

        ward = self.ward_tabs.get() or "All Wards"
        status = self.status_tabs.get() or "All"
        filtered = [
            bed for bed in beds
            if (ward == "All Wards" or bed.get("ward") == ward)
            and (status == "All" or bed.get("status") == status)
        ]

        for child in self.bed_grid.winfo_children():
            child.destroy()

        if not filtered:
            ctk.CTkLabel(
                self.bed_grid, text="No beds match the current filters.",
                font=font(12), text_color=theme.FAINT,
            ).grid(row=0, column=0, columnspan=4, pady=40)
            return

        for index, bed in enumerate(filtered):
            card = self._bed_card(bed)
            card.grid(
                row=index // 4, column=index % 4,
                sticky="nsew", padx=5, pady=5,
            )

    def _bed_card(self, bed: dict) -> Card:
        status = bed.get("status", "")
        border = theme.BORDER
        if status == "Occupied":
            border = theme.BORDER_STRONG
        elif status == "Cleaning":
            border = theme.AMBER_BORDER
        elif status == "Available":
            border = theme.EMERALD_BORDER
        elif status == "Maintenance":
            border = theme.BORDER

        card = Card(self.bed_grid, border_color=border, corner_radius=10)
        card.grid_columnconfigure(0, weight=1)

        top = ctk.CTkFrame(card, fg_color="transparent")
        top.grid(row=0, column=0, sticky="ew", padx=13, pady=(11, 0))
        top.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(
            top, text=bed.get("code", ""), font=font(16, bold=True, mono=True),
            text_color=theme.TEXT, anchor="w",
        ).grid(row=0, column=0, sticky="w")
        color = status_color(status)
        palette = {
            "emerald": (theme.EMERALD, theme.EMERALD_BG),
            "amber": (theme.AMBER, theme.AMBER_BG),
            "rose": (theme.ROSE, theme.ROSE_BG),
            "muted": (theme.MUTED, theme.CARD_ALT),
            "text": (theme.TEXT, theme.CARD_ALT),
        }
        fg, bg = palette.get(color, palette["text"])
        ctk.CTkLabel(
            top, text=status, font=font(9, bold=True),
            text_color=fg, fg_color=bg, corner_radius=5, padx=7, height=20,
        ).grid(row=0, column=1, sticky="e")
        ctk.CTkLabel(
            top, text=f"{bed.get('ward')} · {bed.get('floor')}",
            font=font(9), text_color=theme.MUTED, anchor="w",
        ).grid(row=1, column=0, columnspan=2, sticky="w", pady=(1, 0))
        ctk.CTkLabel(
            top, text=f"Rate: {inr(bed.get('dailyRate'))} / day",
            font=font(9, mono=True), text_color=theme.TEXT_SECONDARY, anchor="w",
        ).grid(row=2, column=0, columnspan=2, sticky="w", pady=(4, 0))

        if status == "Occupied":
            detail = ctk.CTkFrame(card, fg_color=theme.CARD_ALT, corner_radius=7)
            detail.grid(row=1, column=0, sticky="ew", padx=13, pady=(9, 0))
            detail.grid_columnconfigure(0, weight=1)
            ctk.CTkLabel(
                detail, text="ADMITTED PATIENT", font=font(8, bold=True),
                text_color=theme.FAINT, anchor="w",
            ).grid(row=0, column=0, sticky="w", padx=9, pady=(7, 0))
            patient_button = ctk.CTkButton(
                detail, text=bed.get("patientName", ""), font=font(10, bold=True),
                text_color=theme.TEXT, fg_color="transparent",
                hover_color=theme.PRIMARY_SOFT, anchor="w", height=20,
                corner_radius=2,
                command=lambda pid=bed.get("patientId"): self.app.open_patient(pid),
            )
            patient_button.grid(row=1, column=0, sticky="w", padx=5)
            ctk.CTkLabel(
                detail,
                text=f"{bed.get('patientMrn')} · Since {bed.get('admittedSince')}",
                font=font(9, mono=True), text_color=theme.MUTED, anchor="w",
            ).grid(row=2, column=0, sticky="w", padx=9, pady=(0, 7))
        elif status == "Cleaning":
            ctk.CTkLabel(
                card, text="Bed stripped and awaiting housekeeping sterilization.",
                font=font(9), text_color=theme.AMBER, anchor="w", wraplength=220,
            ).grid(row=1, column=0, sticky="ew", padx=13, pady=(9, 0))
        else:
            spacer = ctk.CTkFrame(card, fg_color="transparent", height=8)
            spacer.grid(row=1, column=0, sticky="ew")

        actions = ctk.CTkFrame(card, fg_color="transparent")
        actions.grid(row=2, column=0, sticky="ew", padx=13, pady=(10, 11))
        if status == "Available":
            tinted_button(
                actions, "+ Assign Patient", self.app.open_admit,
                color=theme.EMERALD, bg=theme.EMERALD_BG, border=theme.EMERALD_BORDER,
                height=28,
            ).pack(fill="x")
            secondary_button(
                actions, "Mark Maintenance", lambda bed_id=bed.get("id"): self._set_status(bed_id, "Maintenance"),
                height=24,
            ).pack(fill="x", pady=(4, 0))
        elif status == "Occupied":
            secondary_button(
                actions, "Open Chart", lambda pid=bed.get("patientId"): self.app.open_patient(pid),
                height=28,
            ).pack(side="left", fill="x", expand=True, padx=(0, 4))
            danger_button(
                actions, "Release Bed", lambda bed_id=bed.get("id"): self._release(bed_id),
                height=28,
            ).pack(side="left", fill="x", expand=True)
        elif status == "Cleaning":
            tinted_button(
                actions, "Mark Cleaned & Ready",
                lambda bed_id=bed.get("id"): self._set_status(bed_id, "Available"),
                height=28,
            ).pack(fill="x")
        elif status == "Maintenance":
            secondary_button(
                actions, "Set Operational",
                lambda bed_id=bed.get("id"): self._set_status(bed_id, "Available"),
                height=28,
            ).pack(fill="x")
        return card

    # ------------------------------------------------------------------ actions
    def _set_status(self, bed_id: str, status: str) -> None:
        self.run_action(self.store.update_bed_status, bed_id, status)

    def _release(self, bed_id: str) -> None:
        bed = self.store.bed(bed_id)
        if not bed:
            return
        if messagebox.askyesno(
            "Release bed",
            f"Release bed {bed.get('code')} to cleaning?",
            parent=self.app,
        ):
            self.run_action(self.store.update_bed_status, bed_id, "Cleaning")
