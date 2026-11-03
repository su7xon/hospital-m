"""Aegis Health desktop application shell."""

from __future__ import annotations

from datetime import datetime
from tkinter import messagebox
from typing import Any

import customtkinter as ctk

from . import theme
from .dialogs import (
    AddMedicineDialog,
    AdmitPatientDialog,
    BookAppointmentDialog,
    DispenseMedicineDialog,
    EmergencyTriageDialog,
    InvoiceDialog,
    InvoicePreview,
    LabOrderDialog,
    LabResultDialog,
    PatientChart,
)
from .store import HospitalStore
from .utils import clock_str
from .views import (
    AppointmentsView,
    BedsView,
    BillingView,
    DoctorsView,
    OverviewView,
    PatientsView,
    PharmacyLabsView,
)
from .widgets import (
    configure_table_style,
    font,
    secondary_button,
    tinted_button,
)

NAV_ITEMS = [
    ("overview", "Overview"),
    ("patients", "Patients"),
    ("beds", "Beds"),
    ("appointments", "Appointments"),
    ("pharmacy", "Pharmacy & Labs"),
    ("billing", "Billing"),
    ("doctors", "Doctors"),
]


class AegisApp(ctk.CTk):
    def __init__(self) -> None:
        super().__init__()
        ctk.set_appearance_mode("light")
        configure_table_style()

        self.store = HospitalStore()
        self.store.on_change = self._on_data_change
        self.store.on_toast = self.toast
        self.views: dict[str, Any] = {}
        self.current_key = "overview"
        self._nav_widgets: dict[str, tuple[ctk.CTkFrame, ctk.CTkButton]] = {}
        self._toast_job: str | None = None
        self._clock_job: str | None = None

        self.title("Aegis Health \u00b7 Hospital Management System")
        self.configure(fg_color=theme.BG)
        self.minsize(1120, 680)
        self._center_window(1440, 860)
        self.protocol("WM_DELETE_WINDOW", self._on_close)
        self.bind("<Control-k>", lambda _e: self._focus_search())
        self.bind("<Control-K>", lambda _e: self._focus_search())

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        self._build_sidebar()
        self._build_main()
        self._build_toast()
        self._build_views()
        self.navigate("overview")
        self._refresh_alert_chip()
        self._tick_clock()
        self.after(350, self._welcome)

    # ------------------------------------------------------------------ layout
    def _center_window(self, width: int, height: int) -> None:
        self.update_idletasks()
        scaling = ctk.ScalingTracker.get_window_scaling(self)
        screen_w = self.winfo_screenwidth()
        screen_h = self.winfo_screenheight()
        max_width = max(1120, int(screen_w - 60 / scaling))
        max_height = max(680, int(screen_h - 90 / scaling))
        width = min(width, max_width)
        height = min(height, max_height)
        x = max(0, (screen_w - width) // 2)
        y = max(0, (screen_h - height) // 2 - 8)
        self.geometry(f"{width}x{height}+{x}+{y}")

    def _build_sidebar(self) -> None:
        sidebar = ctk.CTkFrame(self, fg_color=theme.SIDEBAR_BG, corner_radius=0,
                               width=theme.SIDEBAR_WIDTH)
        sidebar.grid(row=0, column=0, rowspan=2, sticky="ns")
        sidebar.grid_propagate(False)
        sidebar.grid_rowconfigure(3, weight=1)
        sidebar.grid_columnconfigure(0, weight=1)
        self.sidebar = sidebar

        brand = ctk.CTkFrame(sidebar, fg_color="transparent")
        brand.grid(row=0, column=0, sticky="ew", padx=17, pady=(20, 16))
        logo = ctk.CTkFrame(brand, width=38, height=38, corner_radius=10,
                            fg_color=theme.EMERALD_BRIGHT)
        logo.pack(side="left")
        logo.pack_propagate(False)
        ctk.CTkLabel(
            logo, text="\u271a", font=(theme.FONT_FAMILY, 20, "bold"),
            text_color=theme.INVERSE,
        ).place(relx=0.5, rely=0.5, anchor="center")
        title_box = ctk.CTkFrame(brand, fg_color="transparent")
        title_box.pack(side="left", padx=(10, 0))
        ctk.CTkLabel(
            title_box, text="AEGIS HEALTH", font=font(13, bold=True),
            text_color=theme.INVERSE, anchor="w",
        ).pack(anchor="w")
        ctk.CTkLabel(
            title_box, text="Hospital Management", font=font(8),
            text_color=theme.SIDEBAR_MUTED, anchor="w",
        ).pack(anchor="w")

        ctk.CTkFrame(sidebar, height=1, fg_color=theme.SIDEBAR_BORDER).grid(
            row=1, column=0, sticky="ew", padx=14,
        )
        ctk.CTkLabel(
            sidebar, text="CLINICAL WORKSPACE", font=font(8, bold=True),
            text_color=theme.SIDEBAR_MUTED, anchor="w",
        ).grid(row=2, column=0, sticky="w", padx=20, pady=(18, 6))

        nav = ctk.CTkFrame(sidebar, fg_color="transparent")
        nav.grid(row=3, column=0, sticky="new", padx=10)
        nav.grid_columnconfigure(0, weight=1)
        for index, (key, label) in enumerate(NAV_ITEMS):
            row = ctk.CTkFrame(nav, fg_color="transparent", height=44)
            row.grid(row=index, column=0, sticky="ew", pady=1)
            row.grid_propagate(False)
            accent = ctk.CTkFrame(row, width=3, height=26, corner_radius=2,
                                  fg_color=theme.SIDEBAR_BG)
            accent.pack(side="left", padx=(1, 5))
            button = ctk.CTkButton(
                row,
                text=label,
                anchor="w",
                height=42,
                corner_radius=7,
                fg_color="transparent",
                hover_color=theme.SIDEBAR_ACTIVE,
                text_color=theme.SIDEBAR_TEXT,
                font=font(11, bold=True),
                command=lambda k=key: self.navigate(k),
            )
            button.pack(side="left", fill="both", expand=True)
            self._nav_widgets[key] = (accent, button)

        bottom = ctk.CTkFrame(sidebar, fg_color="transparent")
        bottom.grid(row=4, column=0, sticky="sew", padx=13, pady=(10, 14))

        status = ctk.CTkFrame(
            bottom, fg_color=theme.SIDEBAR_PANEL, corner_radius=9,
            border_width=1, border_color=theme.SIDEBAR_BORDER,
        )
        status.pack(fill="x")
        status.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(
            status, text="\u25cf", font=font(9), text_color=theme.EMERALD_BRIGHT,
            width=12,
        ).grid(row=0, column=0, sticky="w", padx=(11, 4), pady=(10, 0))
        ctk.CTkLabel(
            status, text="Local SQLite database", font=font(9, bold=True),
            text_color=theme.SIDEBAR_TEXT, anchor="w",
        ).grid(row=0, column=1, sticky="w", pady=(10, 0))
        ctk.CTkLabel(
            status, text="Demo clinical dataset active", font=font(8),
            text_color=theme.SIDEBAR_MUTED, anchor="w",
        ).grid(row=1, column=0, columnspan=2, sticky="w", padx=11, pady=(0, 4))
        ctk.CTkButton(
            status, text="Reset demo data", height=26, corner_radius=6,
            fg_color="transparent", hover_color=theme.SIDEBAR_ACTIVE,
            text_color=theme.SIDEBAR_MUTED, font=font(8, bold=True),
            anchor="w", command=self._reset_demo_data,
        ).grid(row=2, column=0, columnspan=2, sticky="ew", padx=5, pady=(1, 6))

        ctk.CTkLabel(
            bottom, text="Aegis Health v1.0.0  \u00b7  Desktop edition",
            font=font(8), text_color=theme.SIDEBAR_MUTED,
        ).pack(anchor="w", padx=3, pady=(10, 0))
        ctk.CTkLabel(
            bottom, text="Python \u00b7 CustomTkinter \u00b7 SQLite",
            font=font(8), text_color=theme.SIDEBAR_MUTED,
        ).pack(anchor="w", padx=3, pady=(1, 0))

    def _build_main(self) -> None:
        main = ctk.CTkFrame(self, fg_color=theme.BG, corner_radius=0)
        main.grid(row=0, column=1, sticky="nsew")
        main.grid_rowconfigure(1, weight=1)
        main.grid_columnconfigure(0, weight=1)
        self.main = main

        header = ctk.CTkFrame(main, fg_color=theme.CARD, corner_radius=0,
                              height=theme.HEADER_HEIGHT)
        header.grid(row=0, column=0, sticky="ew")
        header.grid_propagate(False)
        self.header = header

        search_box = ctk.CTkFrame(header, fg_color="transparent")
        search_box.pack(side="left", padx=18, pady=14)
        ctk.CTkLabel(
            search_box, text="\u2315", font=(theme.FONT_FAMILY, 15),
            text_color=theme.FAINT,
        ).pack(side="left", padx=(0, 5))
        self.search_entry = ctk.CTkEntry(
            search_box,
            placeholder_text="Search patient name, MRN or phone\u2026   (Ctrl K)",
            width=370, height=34, corner_radius=7,
            fg_color=theme.CARD_ALT, border_color=theme.BORDER_STRONG,
            border_width=1, text_color=theme.TEXT, font=font(10),
            placeholder_text_color=theme.FAINT,
        )
        self.search_entry.pack(side="left")
        self.search_entry.bind("<Return>", self._run_search)
        secondary_button(
            search_box, "Search", lambda: self._run_search(None), height=34, width=72,
        ).pack(side="left", padx=(6, 0))

        right = ctk.CTkFrame(header, fg_color="transparent")
        right.pack(side="right", padx=18, pady=12)

        avatar = ctk.CTkFrame(right, fg_color="transparent")
        avatar.pack(side="right", padx=(12, 0))
        circle = ctk.CTkFrame(avatar, width=34, height=34, corner_radius=17,
                              fg_color=theme.PRIMARY)
        circle.pack(side="left")
        circle.pack_propagate(False)
        ctk.CTkLabel(
            circle, text="AD", font=font(9, bold=True), text_color=theme.INVERSE,
        ).place(relx=0.5, rely=0.5, anchor="center")
        user_text = ctk.CTkFrame(avatar, fg_color="transparent")
        user_text.pack(side="left", padx=(8, 0))
        ctk.CTkLabel(
            user_text, text="Admin Desk", font=font(9, bold=True),
            text_color=theme.TEXT, anchor="w",
        ).pack(anchor="w")
        ctk.CTkLabel(
            user_text, text="Front Office", font=font(8),
            text_color=theme.MUTED, anchor="w",
        ).pack(anchor="w")

        ctk.CTkFrame(right, width=1, height=28, fg_color=theme.BORDER).pack(
            side="right", padx=12,
        )

        self.alert_chip = tinted_button(
            right, "All clear", self.navigate_pharmacy,
            color=theme.EMERALD, bg=theme.EMERALD_BG, border=theme.EMERALD_BORDER,
            height=30, width=112,
        )
        self.alert_chip.pack(side="right")

        clock_box = ctk.CTkFrame(right, fg_color="transparent")
        clock_box.pack(side="right", padx=(0, 12))
        self.clock_label = ctk.CTkLabel(
            clock_box, text=clock_str(), font=font(11, bold=True, mono=True),
            text_color=theme.TEXT, anchor="e",
        )
        self.clock_label.pack(anchor="e")
        self.date_label = ctk.CTkLabel(
            clock_box, text=datetime.now().strftime("%a, %d %b %Y"),
            font=font(8), text_color=theme.MUTED, anchor="e",
        )
        self.date_label.pack(anchor="e")

        ctk.CTkFrame(main, height=1, fg_color=theme.BORDER).grid(row=0, column=0, sticky="sew")

        self.content = ctk.CTkFrame(main, fg_color=theme.BG, corner_radius=0)
        self.content.grid(row=1, column=0, sticky="nsew")
        self.content.grid_rowconfigure(0, weight=1)
        self.content.grid_columnconfigure(0, weight=1)

        footer = ctk.CTkFrame(main, fg_color=theme.CARD, corner_radius=0,
                              height=theme.FOOTER_HEIGHT)
        footer.grid(row=3, column=0, sticky="ew")
        footer.grid_propagate(False)
        ctk.CTkFrame(main, height=1, fg_color=theme.BORDER).grid(
            row=2, column=0, sticky="ew",
        )
        ctk.CTkLabel(
            footer,
            text="\u25cf  Local SQLite database  \u00b7  python_app/data/aegis_health.db",
            font=font(8), text_color=theme.MUTED, anchor="w",
        ).pack(side="left", padx=16)
        ctk.CTkLabel(
            footer,
            text="Aegis Health  \u00b7  Hospital Management System",
            font=font(8), text_color=theme.FAINT, anchor="e",
        ).pack(side="right", padx=16)

    def _build_toast(self) -> None:
        self.toast_frame = ctk.CTkFrame(
            self, fg_color=theme.PRIMARY, corner_radius=9,
            border_width=1, border_color=theme.PRIMARY_HOVER,
        )
        self.toast_frame.grid_columnconfigure(1, weight=1)
        self.toast_icon = ctk.CTkLabel(
            self.toast_frame, text="\u2713", font=font(11, bold=True),
            text_color=theme.EMERALD_BRIGHT, width=20,
        )
        self.toast_icon.grid(row=0, column=0, padx=(12, 0), pady=10)
        self.toast_label = ctk.CTkLabel(
            self.toast_frame, text="", font=font(9, bold=True),
            text_color=theme.INVERSE, anchor="w", justify="left", wraplength=360,
        )
        self.toast_label.grid(row=0, column=1, padx=(2, 14), pady=10)

    def _build_views(self) -> None:
        factories = {
            "overview": OverviewView,
            "patients": PatientsView,
            "beds": BedsView,
            "appointments": AppointmentsView,
            "pharmacy": PharmacyLabsView,
            "billing": BillingView,
            "doctors": DoctorsView,
        }
        for key, factory in factories.items():
            view = factory(self.content, self)
            view.grid(row=0, column=0, sticky="nsew")
            view.grid_remove()
            self.views[key] = view

    # ------------------------------------------------------------------- nav
    def navigate(self, key: str) -> None:
        view = self.views.get(key)
        if view is None:
            return
        self.current_key = key
        for nav_key, (accent, button) in self._nav_widgets.items():
            active = nav_key == key
            accent.configure(fg_color=theme.EMERALD_BRIGHT if active else theme.SIDEBAR_BG)
            button.configure(
                fg_color=theme.SIDEBAR_ACTIVE if active else "transparent",
                hover_color=theme.SIDEBAR_ACTIVE,
                text_color=theme.INVERSE if active else theme.SIDEBAR_TEXT,
            )
        for other_key, other in self.views.items():
            if other_key != key:
                other.grid_remove()
        view.grid()
        try:
            view.refresh()
        except Exception as error:
            self.toast(f"Could not refresh this screen: {error}", error=True)
        view.tkraise()
        view.focus_set()

    def navigate_pharmacy(self) -> None:
        self.navigate("pharmacy")
        view = self.views.get("pharmacy")
        if view is not None:
            view.section_tabs.set("pharmacy")

    def _focus_search(self) -> None:
        self.search_entry.focus_set()
        self.search_entry.select_range(0, "end")

    def _run_search(self, _event: Any = None) -> None:
        query = self.search_entry.get().strip()
        self.navigate("patients")
        view = self.views["patients"]
        view.search.delete(0, "end")
        if query:
            view.search.insert(0, query)
        view.ward_filter.set("All Wards")
        view.status_tabs.set("All", notify=False)
        view.refresh()

        if not query:
            self.toast("Showing the full patient registry.")
            return
        matches = 0
        needle = query.lower()
        for patient in self.store.patients:
            haystack = " ".join([
                str(patient.get("name", "")),
                str(patient.get("mrn", "")),
                str(patient.get("phone", "")),
                str(patient.get("chiefComplaint", "")),
                " ".join(patient.get("diagnoses") or []),
            ]).lower()
            if needle in haystack:
                matches += 1
        if matches:
            self.toast(f"Found {matches} patient record(s) matching \u201c{query}\u201d.")
        else:
            self.toast(f"No patient records match \u201c{query}\u201d.", error=True)

    # --------------------------------------------------------------- dialogs
    def open_admit(self) -> None:
        AdmitPatientDialog(self)

    def open_appointment(self) -> None:
        BookAppointmentDialog(self)

    def open_emergency(self) -> None:
        EmergencyTriageDialog(self)

    def open_add_medicine(self) -> None:
        AddMedicineDialog(self)

    def open_dispense(self, medicine: dict) -> None:
        DispenseMedicineDialog(self, medicine)

    def open_lab_order(self) -> None:
        LabOrderDialog(self)

    def open_lab_result(self, order: dict) -> None:
        LabResultDialog(self, order)

    def open_invoice(self, patient_id: str | None = None) -> None:
        InvoiceDialog(self, patient_id=patient_id)

    def open_invoice_preview(self, invoice: dict) -> None:
        InvoicePreview(self, invoice)

    def open_patient(self, patient_id: str | None) -> None:
        if not patient_id:
            self.toast("No patient record is linked to this entry.", error=True)
            return
        if not self.store.patient(patient_id):
            self.toast("Patient record could not be found.", error=True)
            return
        PatientChart(self, patient_id)

    def open_doctor_schedule(self, doctor_id: str) -> None:
        doctor = self.store.doctor(doctor_id)
        if not doctor:
            self.toast("Doctor record could not be found.", error=True)
            return
        self.navigate("appointments")
        self.views["appointments"].focus_doctor(doctor_id)

    # ---------------------------------------------------------------- feedback
    def toast(self, message: str, error: bool = False) -> None:
        if self._toast_job:
            try:
                self.after_cancel(self._toast_job)
            except ValueError:
                pass
            self._toast_job = None
        if error:
            self.toast_frame.configure(fg_color=theme.ROSE_BG, border_color=theme.ROSE_BORDER)
            self.toast_icon.configure(text="\u26a0", text_color=theme.ROSE)
            self.toast_label.configure(text_color=theme.ROSE)
        else:
            self.toast_frame.configure(fg_color=theme.PRIMARY, border_color=theme.PRIMARY_HOVER)
            self.toast_icon.configure(text="\u2713", text_color=theme.EMERALD_BRIGHT)
            self.toast_label.configure(text_color=theme.INVERSE)
        self.toast_label.configure(text=message)
        self.toast_frame.place(relx=1.0, rely=1.0, anchor="se", x=-18, y=-44)
        self.toast_frame.lift()
        self._toast_job = self.after(4400, self._hide_toast)

    def _hide_toast(self) -> None:
        self._toast_job = None
        self.toast_frame.place_forget()

    def _welcome(self) -> None:
        self.toast("Welcome to Aegis Health \u2014 demo data loaded and ready.")

    def _tick_clock(self) -> None:
        self.clock_label.configure(text=clock_str())
        self.date_label.configure(text=datetime.now().strftime("%a, %d %b %Y"))
        self._clock_job = self.after(1000, self._tick_clock)

    # --------------------------------------------------------------- callbacks
    def _on_data_change(self) -> None:
        view = self.views.get(self.current_key)
        if view is not None:
            try:
                view.refresh()
            except Exception:
                pass
        self._refresh_alert_chip()

    def _refresh_alert_chip(self) -> None:
        low_stock = len([
            medicine for medicine in self.store.medicines
            if int(medicine.get("stock", 0)) <= int(medicine.get("minStock", 0))
        ])
        stat_labs = len([
            order for order in self.store.lab_orders
            if order.get("priority") == "STAT Urgent" and order.get("status") != "Completed"
        ])
        total = low_stock + stat_labs
        if total:
            label = f"{total} alert{'s' if total != 1 else ''}"
            self.alert_chip.configure(
                text=label, text_color=theme.AMBER,
                fg_color=theme.AMBER_BG, border_color=theme.AMBER_BORDER,
                hover_color=theme.AMBER_BORDER,
            )
        else:
            self.alert_chip.configure(
                text="All clear", text_color=theme.EMERALD,
                fg_color=theme.EMERALD_BG, border_color=theme.EMERALD_BORDER,
                hover_color=theme.EMERALD_BORDER,
            )

    def _reset_demo_data(self) -> None:
        if not messagebox.askyesno(
            "Reset demo data",
            "This will restore the original demo patients, beds, appointments, "
            "pharmacy stock, lab orders and invoices.\n\n"
            "Any changes you made in this session will be lost. Continue?",
            parent=self,
        ):
            return
        try:
            self.store.reset_data()
        except Exception as error:
            self.toast(f"Could not reset demo data: {error}", error=True)
            return
        view = self.views.get(self.current_key)
        if view is not None:
            view.refresh()
        self._refresh_alert_chip()

    def _on_close(self) -> None:
        if self._clock_job:
            try:
                self.after_cancel(self._clock_job)
            except ValueError:
                pass
        self.destroy()
# Implementation note 56: no functional change.
# Implementation note 57: no functional change.
# Implementation note 58: no functional change.
# Implementation note 59: no functional change.
# Implementation note 60: no functional change.
