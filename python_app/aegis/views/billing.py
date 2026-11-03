"""Patient billing and financial accounts."""

from __future__ import annotations

from typing import Any

import customtkinter as ctk

from .. import theme
from ..utils import compact_date, inr, short, status_color
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

FILTERS = ["All", "Paid", "Pending", "Partially Paid"]


class BillingView(BaseView):
    def __init__(self, master: Any, app: Any) -> None:
        super().__init__(master, app)
        self.grid_rowconfigure(3, weight=1)
        self._build()
        self.refresh()

    def _build(self) -> None:
        header = PageHeader(
            self,
            "Patient Billing & Financial Accounts",
            "Hospital tariffs, inpatient folios, itemized charges and payment settlements.",
        )
        header.grid(row=0, column=0, sticky="ew", padx=18, pady=(14, 10))
        primary_button(header.actions, "+ Generate New Bill", self.app.open_invoice, width=158).pack(side="right")

        stats = ctk.CTkFrame(self, fg_color="transparent")
        stats.grid(row=1, column=0, sticky="ew", padx=18, pady=(0, 10))
        for index in range(3):
            stats.grid_columnconfigure(index, weight=1, uniform="bill_stat")
        self.stat_billed = StatCard(stats, "Total Billed Revenue", "\u20b90", "Cumulative invoices issued")
        self.stat_collected = StatCard(stats, "Collected Payments", "\u20b90", "Settled via cash, card & TPA",
                                       value_color=theme.EMERALD)
        self.stat_pending = StatCard(stats, "Pending Receivables", "\u20b90", "Awaiting discharge settlement",
                                     value_color=theme.AMBER)
        for index, card in enumerate([self.stat_billed, self.stat_collected, self.stat_pending]):
            card.grid(row=0, column=index, sticky="nsew", padx=(0 if index == 0 else 6, 0 if index == 2 else 6))

        filters = Card(self)
        filters.grid(row=2, column=0, sticky="ew", padx=18, pady=(0, 10))
        filters.grid_columnconfigure(0, weight=1)
        self.search = ctk.CTkEntry(
            filters,
            placeholder_text="Search invoice number, patient name or MRN...",
            height=33, corner_radius=6,
            fg_color=theme.CARD_ALT, border_color=theme.BORDER_STRONG,
            border_width=1, text_color=theme.TEXT, font=font(11),
            placeholder_text_color=theme.FAINT,
        )
        self.search.grid(row=0, column=0, sticky="ew", padx=12, pady=11)
        self.search.bind("<KeyRelease>", lambda _e: self.refresh())
        self.status_tabs = PillTabs(
            filters, FILTERS,
            command=lambda _v: self.refresh(),
            value="All",
        )
        self.status_tabs.grid(row=0, column=1, padx=12, pady=8)

        table_card = Card(self)
        table_card.grid(row=3, column=0, sticky="nsew", padx=18, pady=(0, 12))
        table_card.grid_rowconfigure(0, weight=1)
        table_card.grid_columnconfigure(0, weight=1)
        columns = [
            {"key": "invoice", "title": "Invoice # & Date", "width": 185, "stretch": False},
            {"key": "patient", "title": "Patient Details", "width": 205},
            {"key": "items", "title": "Itemized Breakdown", "width": 275},
            {"key": "total", "title": "Grand Total", "width": 115, "stretch": False},
            {"key": "status", "title": "Settlement Status", "width": 130, "stretch": False},
        ]
        self.table = DataTable(
            table_card, columns, height=12,
            on_double_click=self._preview,
            empty_text="No invoices match the current search.",
        )
        self.table.grid(row=0, column=0, sticky="nsew", padx=1, pady=(1, 0))

        footer = ctk.CTkFrame(table_card, fg_color="transparent")
        footer.grid(row=1, column=0, sticky="ew", padx=12, pady=7)
        ctk.CTkLabel(
            footer, text="Double-click an invoice for the printable hospital receipt.",
            font=font(9), text_color=theme.FAINT, anchor="w",
        ).pack(side="left")
        secondary_button(footer, "Preview / Print", self._preview_selected, height=28).pack(side="right", padx=(6, 0))
        tinted_button(
            footer, "Mark Paid", self._mark_paid,
            color=theme.EMERALD, bg=theme.EMERALD_BG, border=theme.EMERALD_BORDER,
            height=28,
        ).pack(side="right")

    # ------------------------------------------------------------------ refresh
    def refresh(self) -> None:
        invoices = self.store.invoices
        total_billed = sum(float(i.get("grandTotal", 0)) for i in invoices)
        collected = sum(float(i.get("grandTotal", 0)) for i in invoices if i.get("paymentStatus") == "Paid")
        pending = total_billed - collected
        self.stat_billed.update(inr(total_billed), "Cumulative invoices issued")
        self.stat_collected.update(inr(collected), "Settled via cash, card & TPA")
        self.stat_pending.update(inr(pending), "Awaiting discharge settlement")

        counts = {key: 0 for key in FILTERS}
        counts["All"] = len(invoices)
        for invoice in invoices:
            invoice_status = invoice.get("paymentStatus", "")
            if invoice_status in counts:
                counts[invoice_status] += 1
        self.status_tabs.refresh_options([(key, f"{key}  {counts.get(key, 0)}") for key in FILTERS])
        status = self.status_tabs.get() or "All"
        search = self.search.get().strip().lower()

        rows = []
        for invoice in invoices:
            haystack = " ".join([
                str(invoice.get("invoiceNumber", "")),
                str(invoice.get("patientName", "")),
                str(invoice.get("patientMrn", "")),
            ]).lower()
            if search and search not in haystack:
                continue
            if status != "All" and invoice.get("paymentStatus") != status:
                continue
            items = invoice.get("items") or []
            descriptions = ", ".join(short(item.get("description", ""), 24) for item in items[:2])
            if len(items) > 2:
                descriptions += f" · +{len(items) - 2} more"
            rows.append({
                "iid": invoice["id"],
                "record": invoice,
                "values": (
                    f"{invoice.get('invoiceNumber')} · {compact_date(invoice.get('issuedAt'))}",
                    f"{invoice.get('patientName')}\n{invoice.get('patientMrn')} · {invoice.get('patientPhone', '')}",
                    f"{len(items)} line item(s) · {descriptions}",
                    inr(invoice.get("grandTotal", 0), 2),
                    invoice.get("paymentStatus", ""),
                ),
                "tags": [status_color(invoice.get("paymentStatus", "Pending"))],
            })
        for row in rows:
            row["values"] = tuple(str(value).replace("\n", " · ") for value in row["values"])
        self.table.set_rows(rows)

    # ------------------------------------------------------------------ actions
    def _selected(self) -> dict | None:
        invoice = self.table.selected_record()
        if not invoice:
            self.app.toast("Select an invoice row first.", error=True)
            return None
        return invoice

    def _mark_paid(self) -> None:
        invoice = self._selected()
        if not invoice:
            return
        if invoice.get("paymentStatus") == "Paid":
            self.app.toast("This invoice is already marked paid.", error=True)
            return
        self.run_action(self.store.update_invoice_payment, invoice["id"], "Paid", "UPI / Bank Transfer")

    def _preview_selected(self) -> None:
        invoice = self._selected()
        if invoice:
            self._preview(invoice["id"])

    def _preview(self, invoice_id: str) -> None:
        invoice = next((i for i in self.store.invoices if i.get("id") == invoice_id), None)
        if invoice:
            self.app.open_invoice_preview(invoice)
