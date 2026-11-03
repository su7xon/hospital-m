"""Pharmacy formulary and diagnostics laboratory."""

from __future__ import annotations

from typing import Any

import customtkinter as ctk

from .. import theme
from ..utils import compact_date, compact_expiry, inr, short, status_color
from ..widgets import (
    BaseView,
    Card,
    DataTable,
    PageHeader,
    PillTabs,
    font,
    primary_button,
    tinted_button,
)

CATEGORIES = ["All Categories", "Antibiotics", "Cardiovascular", "Analgesics",
              "Respiratory", "IV Fluids", "Emergency", "Vitamins"]


class PharmacyLabsView(BaseView):
    def __init__(self, master: Any, app: Any) -> None:
        super().__init__(master, app)
        self.grid_rowconfigure(2, weight=1)
        self.mode = "pharmacy"
        self._build()
        self.refresh()

    def _build(self) -> None:
        header = PageHeader(
            self,
            "Pharmacy & Diagnostics Laboratory",
            "Hospital formulary inventory, bedside dispensation and clinical diagnostic requisitions.",
        )
        header.grid(row=0, column=0, sticky="ew", padx=18, pady=(14, 8))

        self.section_tabs = PillTabs(
            self,
            [("pharmacy", "Formulary Stock"), ("labs", "Diagnostics & Labs")],
            command=self._switch_mode,
            value="pharmacy",
        )
        self.section_tabs.grid(row=1, column=0, sticky="w", padx=18, pady=(0, 10))

        self.pharmacy_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.pharmacy_frame.grid(row=2, column=0, sticky="nsew", padx=18, pady=(0, 12))
        self.pharmacy_frame.grid_rowconfigure(2, weight=1)
        self.pharmacy_frame.grid_columnconfigure(0, weight=1)

        self.labs_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.labs_frame.grid(row=2, column=0, sticky="nsew", padx=18, pady=(0, 12))
        self.labs_frame.grid_rowconfigure(2, weight=1)
        self.labs_frame.grid_columnconfigure(0, weight=1)
        self.labs_frame.grid_remove()

        self._build_pharmacy()
        self._build_labs()

    def _build_pharmacy(self) -> None:
        metrics = Card(self.pharmacy_frame)
        metrics.grid(row=0, column=0, sticky="ew", pady=(0, 9))
        metrics.grid_columnconfigure(0, weight=1)
        self.pharmacy_metrics = ctk.CTkLabel(
            metrics, text="", font=font(10), text_color=theme.TEXT_SECONDARY, anchor="w",
        )
        self.pharmacy_metrics.grid(row=0, column=0, sticky="ew", padx=14, pady=12)
        primary_button(metrics, "+ Add New Medicine", self.app.open_add_medicine, width=148).grid(
            row=0, column=1, padx=10, pady=8,
        )

        filters = Card(self.pharmacy_frame)
        filters.grid(row=1, column=0, sticky="ew", pady=(0, 9))
        filters.grid_columnconfigure(0, weight=1)
        self.med_search = ctk.CTkEntry(
            filters,
            placeholder_text="Search medication name, generic composition or code...",
            height=33, corner_radius=6,
            fg_color=theme.CARD_ALT, border_color=theme.BORDER_STRONG,
            border_width=1, text_color=theme.TEXT, font=font(11),
            placeholder_text_color=theme.FAINT,
        )
        self.med_search.grid(row=0, column=0, sticky="ew", padx=12, pady=11)
        self.med_search.bind("<KeyRelease>", lambda _e: self.refresh())
        ctk.CTkLabel(
            filters, text="Category", font=font(10, bold=True), text_color=theme.MUTED,
        ).grid(row=0, column=1, padx=(0, 6))
        self.med_category = ctk.CTkOptionMenu(
            filters, values=CATEGORIES, width=156, height=33, corner_radius=6,
            fg_color=theme.CARD_ALT, button_color=theme.PRIMARY_SOFT,
            button_hover_color=theme.BORDER_STRONG, text_color=theme.TEXT,
            font=font(10), dropdown_font=font(10),
            command=lambda _v: self.refresh(),
        )
        self.med_category.set("All Categories")
        self.med_category.grid(row=0, column=2, padx=(0, 12))

        table_card = Card(self.pharmacy_frame)
        table_card.grid(row=2, column=0, sticky="nsew")
        table_card.grid_rowconfigure(0, weight=1)
        table_card.grid_columnconfigure(0, weight=1)
        columns = [
            {"key": "name", "title": "Drug Code & Name", "width": 270},
            {"key": "generic", "title": "Generic Composition", "width": 210},
            {"key": "category", "title": "Category / Form", "width": 150},
            {"key": "stock", "title": "Stock On Hand", "width": 175, "stretch": False},
            {"key": "price", "title": "Unit Price", "width": 90, "stretch": False},
            {"key": "batch", "title": "Batch / Expiry", "width": 150, "stretch": False},
        ]
        self.med_table = DataTable(
            table_card, columns, height=12,
            on_double_click=lambda med_id: self._dispense_selected(med_id),
            empty_text="No medicines match the current filters.",
        )
        self.med_table.grid(row=0, column=0, sticky="nsew", padx=1, pady=(1, 0))

        footer = ctk.CTkFrame(table_card, fg_color="transparent")
        footer.grid(row=1, column=0, sticky="ew", padx=12, pady=7)
        ctk.CTkLabel(
            footer, text="Double-click a medicine to dispense. Low-stock items are highlighted.",
            font=font(9), text_color=theme.FAINT, anchor="w",
        ).pack(side="left")
        tinted_button(
            footer, "Dispense Selected", self._dispense_selected,
            color=theme.TEXT_SECONDARY, bg=theme.CARD_ALT, border=theme.BORDER_STRONG,
            height=28,
        ).pack(side="right")

    def _build_labs(self) -> None:
        metrics = Card(self.labs_frame)
        metrics.grid(row=0, column=0, sticky="ew", pady=(0, 9))
        metrics.grid_columnconfigure(0, weight=1)
        self.labs_metrics = ctk.CTkLabel(
            metrics, text="", font=font(10), text_color=theme.TEXT_SECONDARY, anchor="w",
        )
        self.labs_metrics.grid(row=0, column=0, sticky="ew", padx=14, pady=12)
        primary_button(metrics, "+ Order Diagnostic Test", self.app.open_lab_order, width=176).grid(
            row=0, column=1, padx=10, pady=8,
        )

        table_card = Card(self.labs_frame)
        table_card.grid(row=2, column=0, sticky="nsew")
        table_card.grid_rowconfigure(0, weight=1)
        table_card.grid_columnconfigure(0, weight=1)
        columns = [
            {"key": "order", "title": "Requisition & Date", "width": 150, "stretch": False},
            {"key": "patient", "title": "Patient Details", "width": 160},
            {"key": "test", "title": "Investigation / Department", "width": 320},
            {"key": "doctor", "title": "Ordering Doctor", "width": 150},
            {"key": "priority", "title": "Priority", "width": 95, "stretch": False},
            {"key": "status", "title": "Status & Findings", "width": 250},
        ]
        self.lab_table = DataTable(
            table_card, columns, height=12,
            on_double_click=lambda _order_id: self._open_result(),
            empty_text="No diagnostic requisitions logged.",
        )
        self.lab_table.grid(row=0, column=0, sticky="nsew", padx=1, pady=(1, 0))

        footer = ctk.CTkFrame(table_card, fg_color="transparent")
        footer.grid(row=1, column=0, sticky="ew", padx=12, pady=7)
        ctk.CTkLabel(
            footer, text="Select a requisition to log or edit diagnostic findings.",
            font=font(9), text_color=theme.FAINT, anchor="w",
        ).pack(side="left")
        tinted_button(
            footer, "Log / Edit Findings", self._open_result,
            color=theme.EMERALD, bg=theme.EMERALD_BG, border=theme.EMERALD_BORDER,
            height=28,
        ).pack(side="right")

    # ------------------------------------------------------------------ refresh
    def _switch_mode(self, mode: str) -> None:
        self.mode = mode
        if mode == "pharmacy":
            self.labs_frame.grid_remove()
            self.pharmacy_frame.grid()
        else:
            self.pharmacy_frame.grid_remove()
            self.labs_frame.grid()
        self.refresh()

    def refresh(self) -> None:
        self.section_tabs.refresh_options([
            ("pharmacy", f"Formulary Stock  {len(self.store.medicines)}"),
            ("labs", f"Diagnostics & Labs  {len(self.store.lab_orders)}"),
        ])
        if self.mode == "pharmacy":
            self._refresh_pharmacy()
        else:
            self._refresh_labs()

    def _refresh_pharmacy(self) -> None:
        medicines = self.store.medicines
        low_stock = [m for m in medicines if int(m.get("stock", 0)) <= int(m.get("minStock", 0))]
        value = sum(int(m.get("stock", 0)) * float(m.get("unitPrice", 0)) for m in medicines)
        self.pharmacy_metrics.configure(
            text=(
                f"{len(medicines)} formulary SKUs   ·   "
                f"{len(low_stock)} low-stock reorder alerts   ·   "
                f"inventory value {inr(value)}"
            )
        )

        category = self.med_category.get()
        search = self.med_search.get().strip().lower()
        rows = []
        for medicine in medicines:
            if category != "All Categories" and medicine.get("category") != category:
                continue
            haystack = " ".join([
                str(medicine.get("name", "")),
                str(medicine.get("genericName", "")),
                str(medicine.get("code", "")),
            ]).lower()
            if search and search not in haystack:
                continue
            stock = int(medicine.get("stock", 0))
            minimum = int(medicine.get("minStock", 0))
            low = stock <= minimum
            stock_text = f"{stock} {medicine.get('unit', '')}"
            if low:
                stock_text += f"  ·  LOW (min {minimum})"
            rows.append({
                "iid": medicine["id"],
                "record": medicine,
                "values": (
                    f"{medicine.get('name')}\n{medicine.get('code')}",
                    short(medicine.get("genericName", ""), 34),
                    f"{medicine.get('category')}\n{medicine.get('dosageForm')}",
                    stock_text,
                    inr(medicine.get("unitPrice", 0), 2),
                    f"{medicine.get('batchNumber')}  ·  Exp {compact_expiry(medicine.get('expiryDate'))}",
                ),
                "tags": ["amber"] if low else [],
            })
        for row in rows:
            row["values"] = tuple(str(value).replace("\n", " · ") for value in row["values"])
        self.med_table.set_rows(rows)

    def _refresh_labs(self) -> None:
        orders = self.store.lab_orders
        pending = len([o for o in orders if o.get("status") != "Completed"])
        stat = len([o for o in orders if o.get("priority") == "STAT Urgent" and o.get("status") != "Completed"])
        self.labs_metrics.configure(
            text=(
                f"{len(orders)} total requisitions   ·   {pending} pending tests   ·   "
                f"{stat} STAT urgent awaiting completion"
            )
        )

        rows = []
        for order in orders:
            status = order.get("status", "")
            result = order.get("resultSummary")
            status_text = status if not result else f"{status} · {short(result, 30)}"
            rows.append({
                "iid": order["id"],
                "record": order,
                "values": (
                    f"{order.get('orderNumber')} · {compact_date(order.get('orderedDate'), with_year=False)}",
                    f"{short(order.get('patientName', ''), 16)} · {order.get('patientMrn') or 'Walk-in'}",
                    f"{short(order.get('testName', ''), 44)}",
                    order.get("orderedBy", ""),
                    order.get("priority", "Routine"),
                    status_text,
                ),
                "tags": [
                    status_color(order.get("priority", "Routine")),
                    status_color(status),
                ],
            })
        for row in rows:
            row["values"] = tuple(str(value).replace("\n", " · ") for value in row["values"])
        self.lab_table.set_rows(rows)

    # ------------------------------------------------------------------ actions
    def _dispense_selected(self, medicine_id: str | None = None) -> None:
        medicine = None
        if medicine_id:
            medicine = next((m for m in self.store.medicines if m.get("id") == medicine_id), None)
        else:
            medicine = self.med_table.selected_record()
        if not medicine:
            self.app.toast("Select a medicine row first.", error=True)
            return
        self.app.open_dispense(medicine)

    def _open_result(self) -> None:
        order = self.lab_table.selected_record()
        if not order:
            self.app.toast("Select a lab requisition first.", error=True)
            return
        self.app.open_lab_result(order)
