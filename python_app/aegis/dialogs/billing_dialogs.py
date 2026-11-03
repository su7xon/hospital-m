"""Invoice creation, receipt preview and printable HTML export."""

from __future__ import annotations

import html
import tempfile
import tkinter as tk
import webbrowser
from datetime import datetime
from pathlib import Path
from string import Template
from tkinter import filedialog
from typing import Any

import customtkinter as ctk

from .. import theme
from ..utils import inr, safe_float, status_color
from ..widgets import (
    BaseDialog,
    Card,
    font,
    primary_button,
    secondary_button,
    section_label,
    tinted_button,
    two_column_form,
)

ITEM_CATEGORIES = ["Room / Bed", "Consultation", "Medication", "Lab Test", "Nursing", "Procedure"]
PAYMENT_STATUSES = ["Pending", "Paid", "Partially Paid"]
PAYMENT_METHODS = ["Cash", "Card", "UPI / Bank Transfer", "Insurance / TPA"]


def _clear(frame: ctk.CTkFrame) -> None:
    for child in frame.winfo_children():
        child.destroy()


def _status_palette(status: str) -> tuple[str, str]:
    color = status_color(status)
    palette = {
        "emerald": (theme.EMERALD, theme.EMERALD_BG),
        "amber": (theme.AMBER, theme.AMBER_BG),
        "blue": (theme.BLUE, theme.BLUE_BG),
        "rose": (theme.ROSE, theme.ROSE_BG),
    }
    return palette.get(color, (theme.TEXT_SECONDARY, theme.CARD_ALT))


class _ItemRow(ctk.CTkFrame):
    """Editable invoice line item bound to the parent dialog's calculator."""

    def __init__(self, master: Any, dialog: "InvoiceDialog", item: dict) -> None:
        super().__init__(master, fg_color=theme.CARD_ALT, corner_radius=7)
        self.dialog = dialog
        self.item_id = item.get("id")
        self.grid_columnconfigure(0, weight=1)
        for column, weight in ((1, 0), (2, 0), (3, 0), (4, 0), (5, 0)):
            self.grid_columnconfigure(column, weight=weight)

        self.description = tk.StringVar(value=str(item.get("description", "")))
        self.quantity = tk.StringVar(value=str(item.get("quantity", 1)))
        self.price = tk.StringVar(value=str(item.get("unitPrice", 0)))

        entry_kwargs = dict(
            height=29, corner_radius=5, fg_color=theme.CARD,
            border_color=theme.BORDER_STRONG, border_width=1,
            text_color=theme.TEXT, font=font(10),
        )
        self.desc_entry = ctk.CTkEntry(self, textvariable=self.description, **entry_kwargs)
        self.desc_entry.grid(row=0, column=0, sticky="ew", padx=(8, 5), pady=6)

        self.category = ctk.CTkOptionMenu(
            self,
            values=ITEM_CATEGORIES,
            width=122, height=29, corner_radius=5,
            fg_color=theme.CARD, button_color=theme.PRIMARY_SOFT,
            button_hover_color=theme.BORDER_STRONG, text_color=theme.TEXT,
            font=font(9), dropdown_font=font(10),
            command=lambda _v: self.dialog.recalculate(),
        )
        self.category.set(item.get("category", "Consultation"))
        self.category.grid(row=0, column=1, padx=(0, 5), pady=6)

        self.qty_entry = ctk.CTkEntry(
            self, textvariable=self.quantity, width=52, justify="right", **entry_kwargs,
        )
        self.qty_entry.grid(row=0, column=2, padx=(0, 5), pady=6)

        self.price_entry = ctk.CTkEntry(
            self, textvariable=self.price, width=82, justify="right", **entry_kwargs,
        )
        self.price_entry.grid(row=0, column=3, padx=(0, 5), pady=6)

        self.total_label = ctk.CTkLabel(
            self, text=inr(0, 2), font=font(10, bold=True, mono=True),
            text_color=theme.TEXT, anchor="e", width=78,
        )
        self.total_label.grid(row=0, column=4, sticky="e", padx=(0, 6))

        ctk.CTkButton(
            self, text="✕", width=26, height=26, corner_radius=5,
            fg_color="transparent", hover_color=theme.ROSE_BG,
            text_color=theme.MUTED, font=font(11),
            command=lambda: self.dialog.remove_row(self),
        ).grid(row=0, column=5, padx=(0, 6))

        for variable in (self.description, self.quantity, self.price):
            variable.trace_add("write", lambda *_args: self.dialog.recalculate())

    def values(self) -> dict:
        return {
            "id": self.item_id,
            "description": self.description.get().strip(),
            "category": self.category.get(),
            "quantity": safe_float(self.quantity.get(), 0),
            "unitPrice": safe_float(self.price.get(), 0),
        }


class InvoiceDialog(BaseDialog):
    def __init__(self, app: Any, patient_id: str | None = None) -> None:
        super().__init__(
            app,
            "Generate Patient Invoice",
            "Build an itemized inpatient / OPD folio with live tax and settlement details.",
            width=920,
            height=830,
        )
        self.rows: list[_ItemRow] = []
        self._auto_items = True

        self._patient_labels = [
            f"{patient.get('name')} · {patient.get('mrn')} · "
            f"{patient.get('bedNumber') or 'OPD'} · {patient.get('status', '')}"
            for patient in self.store.patients
        ]
        self._patient_by_label = dict(zip(self._patient_labels, self.store.patients))

        patient_section = Card(self.body, corner_radius=10)
        patient_section.pack(fill="x", padx=2, pady=(2, 10))
        patient_section.grid_columnconfigure(0, weight=1)
        section_label(patient_section, "Patient record", 0, colspan=2)

        self.patient = ctk.CTkOptionMenu(
            patient_section,
            values=self._patient_labels or ["No patients registered"],
            height=34, corner_radius=6,
            fg_color=theme.CARD_ALT, button_color=theme.PRIMARY_SOFT,
            button_hover_color=theme.BORDER_STRONG, text_color=theme.TEXT,
            font=font(10), dropdown_font=font(10),
            command=self._patient_changed,
        )
        self.patient.grid(row=1, column=0, sticky="ew", padx=12, pady=(0, 8))
        ctk.CTkLabel(
            patient_section,
            text="Selecting a patient suggests standard charges. Edit quantities and rates below.",
            font=font(9), text_color=theme.FAINT, anchor="w",
        ).grid(row=2, column=0, sticky="w", padx=12, pady=(0, 10))

        self.patient_banner = ctk.CTkLabel(
            patient_section, text="", font=font(9, mono=True),
            text_color=theme.MUTED, fg_color=theme.CARD_ALT,
            corner_radius=6, anchor="w", justify="left", padx=11, height=42,
        )
        self.patient_banner.grid(row=1, column=1, rowspan=2, sticky="ew", padx=(0, 12), pady=(0, 10))

        items_card = Card(self.body, corner_radius=10)
        items_card.pack(fill="x", padx=2, pady=(0, 10))
        items_card.grid_columnconfigure(0, weight=1)
        heading = ctk.CTkFrame(items_card, fg_color="transparent")
        heading.grid(row=0, column=0, sticky="ew", padx=13, pady=(11, 4))
        heading.grid_columnconfigure(0, weight=1)
        self.items_title = ctk.CTkLabel(
            heading, text="Invoice Line Items (0)", font=font(13, bold=True),
            text_color=theme.TEXT, anchor="w",
        )
        self.items_title.grid(row=0, column=0, sticky="w")
        tinted_button(
            heading, "+ Add Line Item", self._add_blank_row,
            color=theme.TEXT_SECONDARY, bg=theme.CARD_ALT, border=theme.BORDER_STRONG,
            height=27,
        ).grid(row=0, column=1, sticky="e")

        column_header = ctk.CTkFrame(items_card, fg_color="transparent")
        column_header.grid(row=1, column=0, sticky="ew", padx=15)
        column_header.grid_columnconfigure(0, weight=1)
        for column, weight in ((1, 0), (2, 0), (3, 0), (4, 0), (5, 0)):
            column_header.grid_columnconfigure(column, weight=weight)
        for column, (label, width, anchor) in enumerate((
            ("DESCRIPTION", 0, "w"),
            ("CATEGORY", 122, "w"),
            ("QTY", 52, "e"),
            ("UNIT PRICE", 82, "e"),
            ("AMOUNT", 78, "e"),
            ("", 26, "center"),
        )):
            ctk.CTkLabel(
                column_header, text=label, font=font(8, bold=True),
                text_color=theme.FAINT, anchor=anchor, width=width,
            ).grid(row=0, column=column, sticky="ew", padx=(0, 5), pady=(0, 3))

        self.rows_frame = ctk.CTkFrame(items_card, fg_color="transparent")
        self.rows_frame.grid(row=2, column=0, sticky="ew", padx=8)
        self.rows_frame.grid_columnconfigure(0, weight=1)

        self.empty_label = ctk.CTkLabel(
            items_card, text="No line items yet. Add a charge to begin the invoice.",
            font=font(10), text_color=theme.FAINT,
        )
        self.empty_label.grid(row=3, column=0, pady=10)

        totals = ctk.CTkFrame(items_card, fg_color="transparent")
        totals.grid(row=4, column=0, sticky="ew", padx=14, pady=(8, 12))
        totals.grid_columnconfigure(0, weight=1)
        totals.grid_columnconfigure(1, weight=1)

        tax_box = ctk.CTkFrame(totals, fg_color="transparent")
        tax_box.grid(row=0, column=0, sticky="nw")
        ctk.CTkLabel(
            tax_box, text="GST rate (%)", font=font(9, bold=True),
            text_color=theme.TEXT_SECONDARY, anchor="w",
        ).pack(anchor="w", pady=(0, 3))
        self.tax_percent = ctk.CTkEntry(
            tax_box, width=84, height=31, corner_radius=6,
            fg_color=theme.CARD_ALT, border_color=theme.BORDER_STRONG,
            border_width=1, text_color=theme.TEXT, font=font(10, mono=True),
        )
        self.tax_percent.pack(anchor="w")
        self.tax_percent.insert(0, "5")
        self.tax_percent.bind("<KeyRelease>", lambda _e: self.recalculate())

        ctk.CTkLabel(
            tax_box, text="Discount (₹)", font=font(9, bold=True),
            text_color=theme.TEXT_SECONDARY, anchor="w",
        ).pack(anchor="w", pady=(8, 3))
        self.discount = ctk.CTkEntry(
            tax_box, width=140, height=31, corner_radius=6,
            fg_color=theme.CARD_ALT, border_color=theme.BORDER_STRONG,
            border_width=1, text_color=theme.TEXT, font=font(10, mono=True),
        )
        self.discount.insert(0, "0")
        self.discount.pack(anchor="w")
        self.discount.bind("<KeyRelease>", lambda _e: self.recalculate())

        self.summary = ctk.CTkFrame(totals, fg_color=theme.CARD_ALT, corner_radius=8)
        self.summary.grid(row=0, column=1, sticky="ne", padx=(18, 0))
        self.summary.grid_columnconfigure(0, weight=1)
        self.summary_labels: dict[str, ctk.CTkLabel] = {}
        for index, key in enumerate(("subtotal", "tax", "discount", "grand")):
            if key == "grand":
                ctk.CTkFrame(
                    self.summary, height=1, fg_color=theme.BORDER,
                ).grid(row=index * 2, column=0, columnspan=2, sticky="ew", padx=12, pady=(4, 3))
                row_index = index * 2 + 1
                label_font = font(11, bold=True)
                value_font = font(14, bold=True, mono=True)
            else:
                row_index = index
                label_font = font(9)
                value_font = font(9, mono=True)
            names = {
                "subtotal": "Subtotal",
                "tax": "GST",
                "discount": "Discount",
                "grand": "Grand total",
            }
            ctk.CTkLabel(
                self.summary, text=names[key], font=label_font,
                text_color=theme.TEXT_SECONDARY, anchor="w",
            ).grid(row=row_index, column=0, sticky="w", padx=(13, 24), pady=(6 if index == 0 else 1, 1))
            label = ctk.CTkLabel(
                self.summary, text=inr(0, 2), font=value_font,
                text_color=theme.TEXT if key != "discount" else theme.EMERALD,
                anchor="e",
            )
            label.grid(row=row_index, column=1, sticky="e", padx=(0, 13), pady=(6 if index == 0 else 1, 1))
            self.summary_labels[key] = label
        ctk.CTkFrame(self.summary, height=6, fg_color="transparent").grid(row=8, column=0)

        settlement = Card(self.body, corner_radius=10)
        settlement.pack(fill="x", padx=2, pady=(0, 6))
        settlement.grid_columnconfigure(0, weight=1)
        settlement.grid_columnconfigure(1, weight=1)
        section_label(settlement, "Settlement & notes", 0, colspan=2)

        status_fields = ctk.CTkFrame(settlement, fg_color="transparent")
        status_fields.grid(row=1, column=0, columnspan=2, sticky="ew")
        two_column_form(status_fields, 2)
        self.status = _labelled_option(
            status_fields, "Payment status", PAYMENT_STATUSES, "Pending", 0, 0,
        )
        self.method = _labelled_option(
            status_fields, "Payment method", PAYMENT_METHODS, "Cash", 0, 1,
        )
        self.insurance = _labelled_entry(
            status_fields, "Insurance / TPA provider & claim no.", "e.g. Star Health · Claim #ST-88192", 1, 0,
        )
        self.notes = _labelled_entry(
            status_fields, "Invoice notes", "e.g. Discharge cleared, cashless TPA pre-authorization.", 1, 1,
        )

        # Populate patient selection and initial suggested charges.
        if patient_id:
            for label, patient in self._patient_by_label.items():
                if patient.get("id") == patient_id:
                    self.patient.set(label)
                    break
        elif self._patient_labels:
            self.patient.set(self._patient_labels[0])
        self._patient_changed(self.patient.get())
        self.add_footer("Generate Invoice", self.submit)

    # ------------------------------------------------------------------ items
    def _add_row(self, item: dict) -> None:
        row = _ItemRow(self.rows_frame, self, item)
        row.grid(row=len(self.rows), column=0, sticky="ew", pady=2)
        self.rows.append(row)
        self._refresh_rows_view()

    def _add_blank_row(self) -> None:
        self._auto_items = False
        self._add_row({"description": "", "category": "Consultation", "quantity": 1, "unitPrice": 1000})
        self.rows[-1].desc_entry.focus_set()

    def remove_row(self, row: _ItemRow) -> None:
        self._auto_items = False
        if row in self.rows:
            self.rows.remove(row)
        row.destroy()
        for index, remaining in enumerate(self.rows):
            remaining.grid_configure(row=index)
        self._refresh_rows_view()

    def _refresh_rows_view(self) -> None:
        self.items_title.configure(text=f"Invoice Line Items ({len(self.rows)})")
        if self.rows:
            self.empty_label.grid_remove()
        else:
            self.empty_label.grid()
        self.recalculate()

    def recalculate(self) -> None:
        subtotal = 0.0
        for row in self.rows:
            qty = safe_float(row.quantity.get(), 0)
            price = safe_float(row.price.get(), 0)
            total = qty * price
            subtotal += total
            row.total_label.configure(text=inr(total, 2))
        tax = subtotal * safe_float(self.tax_percent.get(), 0) / 100
        discount = safe_float(self.discount.get(), 0)
        grand = subtotal + tax - discount
        self.summary_labels["subtotal"].configure(text=inr(subtotal, 2))
        self.summary_labels["tax"].configure(text=inr(tax, 2))
        self.summary_labels["discount"].configure(
            text=("-" if discount else "") + inr(discount, 2)
        )
        self.summary_labels["grand"].configure(
            text=inr(grand, 2), text_color=theme.ROSE if grand < 0 else theme.TEXT,
        )

    # ----------------------------------------------------------------- patient
    def _patient_changed(self, label: str) -> None:
        patient = self._patient_by_label.get(label)
        if not patient:
            self.patient_banner.configure(text="No patient selected.")
            return
        contact = patient.get("emergencyContact") or {}
        location = patient.get("bedNumber") or "OPD / no bed"
        self.patient_banner.configure(
            text=(
                f"{patient.get('mrn')} · {patient.get('status')} · {location}\n"
                f"{patient.get('assignedDoctorName', '—')} · {patient.get('department', '')} · "
                f"{patient.get('phone', '')}"
            )
        )
        if self._auto_items:
            self._load_suggested_items(patient)

    def _load_suggested_items(self, patient: dict) -> None:
        for row in self.rows:
            row.destroy()
        self.rows.clear()

        bed = self.store.bed_by_code(patient.get("bedNumber") or "")
        if bed:
            admission = str(patient.get("admissionDate", ""))[:10]
            days = 2
            try:
                admitted = datetime.strptime(admission, "%Y-%m-%d").date()
                days = max(1, (datetime.now().date() - admitted).days + 1)
            except ValueError:
                pass
            rate = float(bed.get("dailyRate", 1800))
            self._add_row({
                "description": f"Room & Nursing Charges ({patient.get('ward')} · Bed {bed.get('code')})",
                "category": "Room / Bed",
                "quantity": days,
                "unitPrice": rate,
            })
            self._add_row({
                "description": f"Attending Doctor Inpatient Care ({patient.get('assignedDoctorName')})",
                "category": "Consultation",
                "quantity": days,
                "unitPrice": 1000,
            })
            self._add_row({
                "description": "Nursing care, monitoring & dressing consumables",
                "category": "Nursing",
                "quantity": days,
                "unitPrice": 650,
            })
        else:
            self._add_row({
                "description": "General Consultation / Physician Rounds",
                "category": "Consultation",
                "quantity": 1,
                "unitPrice": 1000,
            })
        self._refresh_rows_view()

    # ------------------------------------------------------------------ submit
    def submit(self) -> None:
        patient = self._patient_by_label.get(self.patient.get())
        if not patient:
            self.app.toast("Please select a patient.", error=True)
            return
        if not self.rows:
            self.app.toast("Please add at least one line item to the bill.", error=True)
            return

        items = []
        for index, row in enumerate(self.rows, start=1):
            entry = row.values()
            if not entry["description"]:
                self.app.toast(f"Line item {index} needs a description.", error=True)
                return
            if entry["quantity"] <= 0:
                self.app.toast(f"Line item {index} quantity must be greater than zero.", error=True)
                return
            if entry["unitPrice"] < 0:
                self.app.toast(f"Line item {index} unit price cannot be negative.", error=True)
                return
            items.append(entry)

        tax_rate = safe_float(self.tax_percent.get(), 0)
        discount = safe_float(self.discount.get(), 0)
        subtotal = sum(item["quantity"] * item["unitPrice"] for item in items)
        tax = subtotal * tax_rate / 100
        grand = subtotal + tax - discount
        if tax_rate < 0:
            self.app.toast("GST rate cannot be negative.", error=True)
            return
        if discount < 0:
            self.app.toast("Discount cannot be negative.", error=True)
            return
        if grand < 0:
            self.app.toast("Discount exceeds the invoice total.", error=True)
            return

        status = self.status.get()
        method = self.method.get()
        insurance = self.insurance.get().strip()
        if method == "Insurance / TPA" and not insurance:
            self.app.toast("Please enter the insurance / TPA provider and claim number.", error=True)
            return

        try:
            invoice = self.store.create_invoice(
                patient["id"],
                items,
                tax,
                discount,
                status,
                method,
                insurance or None,
                self.notes.get().strip(),
            )
        except Exception as error:
            self.app.toast(str(error), error=True)
            return
        self.close()
        self.app.after(90, lambda: self.app.open_invoice_preview(invoice))


def _labelled_option(
    parent: Any, label: str, options: list[str], default: str, row: int, column: int,
) -> ctk.CTkOptionMenu:
    wrapper = ctk.CTkFrame(parent, fg_color="transparent")
    wrapper.grid(row=row, column=column, sticky="ew", padx=7, pady=5)
    ctk.CTkLabel(
        wrapper, text=label, font=font(10, bold=True),
        text_color=theme.TEXT_SECONDARY, anchor="w",
    ).pack(fill="x", pady=(0, 4))
    widget = ctk.CTkOptionMenu(
        wrapper, values=options, height=32, corner_radius=6,
        fg_color=theme.CARD_ALT, button_color=theme.PRIMARY_SOFT,
        button_hover_color=theme.BORDER_STRONG, text_color=theme.TEXT,
        dropdown_fg_color=theme.CARD, dropdown_hover_color=theme.CARD_HOVER,
        dropdown_text_color=theme.TEXT, font=font(11), dropdown_font=font(11),
    )
    widget.set(default)
    widget.pack(fill="x")
    return widget


def _labelled_entry(
    parent: Any, label: str, placeholder: str, row: int, column: int,
) -> ctk.CTkEntry:
    wrapper = ctk.CTkFrame(parent, fg_color="transparent")
    wrapper.grid(row=row, column=column, sticky="ew", padx=7, pady=5)
    ctk.CTkLabel(
        wrapper, text=label, font=font(10, bold=True),
        text_color=theme.TEXT_SECONDARY, anchor="w",
    ).pack(fill="x", pady=(0, 4))
    widget = ctk.CTkEntry(
        wrapper, height=32, corner_radius=6, placeholder_text=placeholder,
        fg_color=theme.CARD_ALT, border_color=theme.BORDER_STRONG, border_width=1,
        text_color=theme.TEXT, placeholder_text_color=theme.FAINT, font=font(11),
    )
    widget.pack(fill="x")
    return widget


class InvoicePreview(ctk.CTkToplevel):
    """Printable, browser-style receipt with HTML print / export support."""

    def __init__(self, app: Any, invoice: dict) -> None:
        super().__init__(app)
        self.app = app
        self.store = app.store
        self.invoice = invoice

        self.title(f"Receipt · {invoice.get('invoiceNumber', 'Invoice')}")
        self.configure(fg_color=theme.BG)
        self.minsize(820, 640)
        self.transient(app)
        self.protocol("WM_DELETE_WINDOW", self.close)
        self.bind("<Escape>", lambda _e: self.close())

        self.update_idletasks()
        width, height = 900, 840
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

    def _build_shell(self) -> None:
        header = ctk.CTkFrame(self, fg_color=theme.CARD, corner_radius=0, height=74)
        header.pack(fill="x")
        header.pack_propagate(False)
        header.grid_columnconfigure(0, weight=1)
        self.title_label = ctk.CTkLabel(
            header, text="", font=font(16, bold=True), text_color=theme.TEXT, anchor="w",
        )
        self.title_label.grid(row=0, column=0, sticky="w", padx=20, pady=(14, 0))
        self.subtitle_label = ctk.CTkLabel(
            header, text="", font=font(9, mono=True), text_color=theme.MUTED, anchor="w",
        )
        self.subtitle_label.grid(row=1, column=0, sticky="w", padx=20, pady=(1, 0))
        self.status_chip = ctk.CTkLabel(
            header, text="", font=font(10, bold=True),
            corner_radius=6, padx=11, height=25,
        )
        self.status_chip.grid(row=0, column=1, rowspan=2, sticky="e", padx=(8, 14))

        self.footer = ctk.CTkFrame(self, fg_color=theme.CARD, corner_radius=0, height=64)
        self.footer.pack(fill="x", side="bottom")
        self.footer.pack_propagate(False)
        primary_button(
            self.footer, "Open Printable Receipt", self.print_receipt, width=182, height=34,
        ).pack(side="right", padx=(6, 16), pady=15)
        secondary_button(
            self.footer, "Save HTML", self.save_html, width=100, height=34,
        ).pack(side="right", pady=15)
        self.paid_button = tinted_button(
            self.footer, "Mark as Paid", self.mark_paid,
            color=theme.EMERALD, bg=theme.EMERALD_BG, border=theme.EMERALD_BORDER,
            height=34, width=118,
        )
        secondary_button(self.footer, "Close", self.close, width=88, height=34).pack(
            side="right", padx=(0, 6), pady=15,
        )

        self.body = ctk.CTkScrollableFrame(
            self, fg_color=theme.BG, corner_radius=0,
            scrollbar_button_color=theme.BORDER_STRONG,
            scrollbar_button_hover_color=theme.MUTED,
        )
        self.body.pack(fill="both", expand=True, padx=14, pady=14)

    # ------------------------------------------------------------------ render
    def render(self) -> None:
        invoice = self.invoice
        self.title_label.configure(text=f"Hospital Receipt · {invoice.get('invoiceNumber')}")
        self.subtitle_label.configure(
            text=(
                f"Issued {invoice.get('issuedAt')}  ·  {invoice.get('patientName')} "
                f"({invoice.get('patientMrn')})"
            )
        )
        fg, bg = _status_palette(invoice.get("paymentStatus", "Pending"))
        self.status_chip.configure(
            text=f" {invoice.get('paymentStatus', 'Pending')} ",
            text_color=fg, fg_color=bg,
        )
        if invoice.get("paymentStatus") == "Paid":
            self.paid_button.pack_forget()
        else:
            self.paid_button.pack(side="left", padx=16, pady=15)

        _clear(self.body)
        paper = Card(self.body, corner_radius=8)
        paper.pack(fill="x", padx=2, pady=2)
        paper.grid_columnconfigure(0, weight=1)

        # Letterhead
        letterhead = ctk.CTkFrame(paper, fg_color="transparent")
        letterhead.grid(row=0, column=0, sticky="ew", padx=26, pady=(22, 0))
        letterhead.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(
            letterhead, text="AEGIS HEALTH", font=(theme.FONT_FAMILY, 22, "bold"),
            text_color=theme.PRIMARY, anchor="w",
        ).grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(
            letterhead, text="Multi-Specialty Hospital & Research Centre",
            font=font(10, bold=True), text_color=theme.MUTED, anchor="w",
        ).grid(row=1, column=0, sticky="w", pady=(0, 2))
        ctk.CTkLabel(
            letterhead,
            text="Aegis Health Campus, Sector 21, Navi Mumbai 400705  ·  +91 22 4000 8800  ·  GSTIN 27AEGIS4821F1Z5",
            font=font(8), text_color=theme.FAINT, anchor="e", justify="right",
        ).grid(row=0, column=1, rowspan=2, sticky="e")
        ctk.CTkFrame(paper, height=2, fg_color=theme.PRIMARY).grid(
            row=1, column=0, sticky="ew", padx=26, pady=(14, 16),
        )

        # Meta
        meta = ctk.CTkFrame(paper, fg_color="transparent")
        meta.grid(row=2, column=0, sticky="ew", padx=26)
        meta.grid_columnconfigure(0, weight=1)
        meta.grid_columnconfigure(1, weight=1)

        billed = ctk.CTkFrame(meta, fg_color="transparent")
        billed.grid(row=0, column=0, sticky="nw")
        ctk.CTkLabel(
            billed, text="BILLED TO", font=font(8, bold=True), text_color=theme.FAINT, anchor="w",
        ).pack(anchor="w")
        ctk.CTkLabel(
            billed, text=invoice.get("patientName", ""), font=font(13, bold=True),
            text_color=theme.TEXT, anchor="w",
        ).pack(anchor="w", pady=(3, 1))
        for line in (
            f"MRN: {invoice.get('patientMrn', '—')}",
            f"Phone: {invoice.get('patientPhone') or '—'}",
            f"Admission: {invoice.get('admissionDate') or '—'}",
            f"Discharge: {invoice.get('dischargeDate') or 'Ongoing / OPD'}",
        ):
            ctk.CTkLabel(
                billed, text=line, font=font(9, mono=True),
                text_color=theme.MUTED, anchor="w",
            ).pack(anchor="w")

        details = ctk.CTkFrame(meta, fg_color="transparent")
        details.grid(row=0, column=1, sticky="ne")
        for label, text in (
            ("INVOICE NUMBER", invoice.get("invoiceNumber", "")),
            ("ISSUED AT", invoice.get("issuedAt", "")),
            ("SETTLEMENT", invoice.get("paymentStatus", "")),
            ("METHOD", invoice.get("paymentMethod") or "—"),
        ):
            row = ctk.CTkFrame(details, fg_color="transparent")
            row.pack(fill="x", pady=1)
            ctk.CTkLabel(
                row, text=label, font=font(8, bold=True), text_color=theme.FAINT,
                anchor="w", width=112,
            ).pack(side="left")
            ctk.CTkLabel(
                row, text=str(text), font=font(9, mono=True), text_color=theme.TEXT_SECONDARY,
                anchor="e",
            ).pack(side="right")

        if invoice.get("insuranceProvider"):
            tpa = ctk.CTkLabel(
                paper,
                text=f"Insurance / TPA: {invoice.get('insuranceProvider')}",
                font=font(9, bold=True), text_color=theme.BLUE,
                fg_color=theme.BLUE_BG, corner_radius=5, padx=9, height=25, anchor="w",
            )
            tpa.grid(row=3, column=0, sticky="w", padx=26, pady=(12, 0))

        # Itemized table
        table = ctk.CTkFrame(paper, fg_color="transparent")
        table.grid(row=4, column=0, sticky="ew", padx=26, pady=(18, 0))
        table.grid_columnconfigure(1, weight=1)
        headings = (
            ("#", 26, "w"), ("DESCRIPTION", 0, "w"), ("CATEGORY", 110, "w"),
            ("QTY", 54, "e"), ("UNIT PRICE", 92, "e"), ("AMOUNT", 100, "e"),
        )
        header = ctk.CTkFrame(table, fg_color=theme.CARD_ALT, corner_radius=5)
        header.grid(row=0, column=0, columnspan=6, sticky="ew")
        for column, (label, width, anchor) in enumerate(headings):
            header.grid_columnconfigure(column, weight=1 if column == 1 else 0)
            ctk.CTkLabel(
                header, text=label, font=font(8, bold=True), text_color=theme.FAINT,
                anchor=anchor, width=width,
            ).grid(row=0, column=column, sticky="ew", padx=(10 if column == 0 else 4, 8), pady=7)

        for index, item in enumerate(invoice.get("items") or [], start=1):
            row = ctk.CTkFrame(table, fg_color="transparent")
            row.grid(row=index * 2 - 1, column=0, columnspan=6, sticky="ew")
            for column, weight in ((0, 0), (1, 1), (2, 0), (3, 0), (4, 0), (5, 0)):
                row.grid_columnconfigure(column, weight=weight)
            values = (
                (str(index), 26, "w"),
                (item.get("description", ""), 0, "w"),
                (item.get("category", ""), 110, "w"),
                (f"{safe_float(item.get('quantity', 0), 0):g}", 54, "e"),
                (inr(item.get("unitPrice", 0), 2), 92, "e"),
                (inr(item.get("total", 0), 2), 100, "e"),
            )
            for column, (text, width, anchor) in enumerate(values):
                ctk.CTkLabel(
                    row, text=str(text),
                    font=font(9, mono=column in (3, 4, 5)),
                    text_color=theme.TEXT_SECONDARY if column != 5 else theme.TEXT,
                    anchor=anchor, width=width, justify="left",
                    wraplength=340 if column == 1 else 0,
                ).grid(row=0, column=column, sticky="ew", padx=(10 if column == 0 else 4, 8), pady=6)
            ctk.CTkFrame(table, height=1, fg_color=theme.BORDER).grid(
                row=index * 2, column=0, columnspan=6, sticky="sew",
            )

        # Totals
        totals = ctk.CTkFrame(paper, fg_color="transparent")
        totals.grid(row=5, column=0, sticky="e", padx=26, pady=(14, 0))
        rows = [
            ("Subtotal", inr(invoice.get("subtotal", 0), 2), theme.TEXT_SECONDARY, font(9)),
            ("GST", inr(invoice.get("tax", 0), 2), theme.TEXT_SECONDARY, font(9)),
            ("Discount", f"- {inr(invoice.get('discount', 0), 2)}", theme.EMERALD, font(9)),
        ]
        for index, (label, value, color, label_font) in enumerate(rows):
            ctk.CTkLabel(
                totals, text=label, font=label_font, text_color=theme.MUTED, anchor="w",
            ).grid(row=index, column=0, sticky="w", padx=(0, 70), pady=2)
            ctk.CTkLabel(
                totals, text=value, font=font(9, mono=True), text_color=color, anchor="e",
            ).grid(row=index, column=1, sticky="e", pady=2)
        ctk.CTkFrame(totals, height=1, fg_color=theme.BORDER).grid(
            row=len(rows), column=0, columnspan=2, sticky="ew", pady=5,
        )
        ctk.CTkLabel(
            totals, text="Grand Total", font=font(12, bold=True),
            text_color=theme.TEXT, anchor="w",
        ).grid(row=len(rows) + 1, column=0, sticky="w", padx=(0, 70), pady=2)
        ctk.CTkLabel(
            totals, text=inr(invoice.get("grandTotal", 0), 2),
            font=font(17, bold=True, mono=True), text_color=theme.PRIMARY, anchor="e",
        ).grid(row=len(rows) + 1, column=1, sticky="e", pady=2)

        # Notes / signature
        notes = invoice.get("notes") or ""
        footer_note = ctk.CTkFrame(paper, fg_color="transparent")
        footer_note.grid(row=6, column=0, sticky="ew", padx=26, pady=(20, 24))
        footer_note.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(
            footer_note, text="NOTES", font=font(8, bold=True), text_color=theme.FAINT, anchor="w",
        ).grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(
            footer_note, text=notes or "Thank you for choosing Aegis Health.",
            font=font(9), text_color=theme.TEXT_SECONDARY, anchor="w",
            justify="left", wraplength=590,
        ).grid(row=1, column=0, sticky="w", pady=(2, 12))
        ctk.CTkLabel(
            footer_note,
            text="This is a computer-generated invoice. Please retain it for insurance and tax records.",
            font=font(8), text_color=theme.FAINT, anchor="w",
        ).grid(row=2, column=0, sticky="w")
        signature = ctk.CTkFrame(footer_note, fg_color="transparent")
        signature.grid(row=0, column=1, rowspan=3, sticky="e", padx=(30, 0))
        ctk.CTkLabel(
            signature, text="", font=font(8), height=34,
        ).pack()
        ctk.CTkFrame(signature, height=1, width=170, fg_color=theme.BORDER_STRONG).pack()
        ctk.CTkLabel(
            signature, text="Authorized Signatory · Finance", font=font(8),
            text_color=theme.FAINT,
        ).pack(pady=(4, 0))

    # ------------------------------------------------------------------ actions
    def mark_paid(self) -> None:
        if self.invoice.get("paymentStatus") == "Paid":
            self.app.toast("This invoice is already marked paid.", error=True)
            return
        try:
            self.store.update_invoice_payment(
                self.invoice["id"], "Paid", self.invoice.get("paymentMethod") or "UPI / Bank Transfer",
            )
        except Exception as error:
            self.app.toast(str(error), error=True)
            return
        self.render()

    def print_receipt(self) -> None:
        path = Path(tempfile.gettempdir()) / f"aegis_receipt_{self.invoice.get('invoiceNumber', 'invoice')}.html"
        try:
            path.write_text(self._receipt_html(self.invoice), encoding="utf-8")
        except OSError as error:
            self.app.toast(f"Could not create printable receipt: {error}", error=True)
            return
        try:
            webbrowser.open(path.as_uri())
            self.app.toast("Printable receipt opened in your browser. Use Ctrl+P to print or save as PDF.")
        except Exception as error:
            self.app.toast(f"Could not open browser: {error}", error=True)

    def save_html(self) -> None:
        default_name = f"aegis_receipt_{self.invoice.get('invoiceNumber', 'invoice')}.html"
        path = filedialog.asksaveasfilename(
            parent=self,
            title="Save printable receipt",
            defaultextension=".html",
            initialfile=default_name,
            filetypes=[("HTML files", "*.html"), ("All files", "*.*")],
        )
        if not path:
            return
        try:
            Path(path).write_text(self._receipt_html(self.invoice), encoding="utf-8")
        except OSError as error:
            self.app.toast(f"Could not save receipt: {error}", error=True)
            return
        self.app.toast(f"Receipt saved to {Path(path).name}.")

    @staticmethod
    def _receipt_html(invoice: dict) -> str:
        escape = html.escape
        item_rows = []
        for index, item in enumerate(invoice.get("items") or [], start=1):
            item_rows.append(
                "<tr>"
                f"<td class='num'>{index}</td>"
                f"<td>{escape(str(item.get('description', '')))}</td>"
                f"<td>{escape(str(item.get('category', '')))}</td>"
                f"<td class='num'>{item.get('quantity', 0):g}</td>"
                f"<td class='num'>{escape(inr(item.get('unitPrice', 0), 2))}</td>"
                f"<td class='num strong'>{escape(inr(item.get('total', 0), 2))}</td>"
                "</tr>"
            )
        status = str(invoice.get("paymentStatus", "Pending"))
        status_class = "paid" if status == "Paid" else ("partial" if status == "Partially Paid" else "pending")
        tpa_row = ""
        if invoice.get("insuranceProvider"):
            tpa_row = (
                "<div class='tpa'>Insurance / TPA: "
                f"{escape(str(invoice.get('insuranceProvider')))}</div>"
            )
        notes = escape(str(invoice.get("notes") or "Thank you for choosing Aegis Health."))
        template = Template(_RECEIPT_TEMPLATE)
        return template.safe_substitute(
            invoice_number=escape(str(invoice.get("invoiceNumber", ""))),
            issued_at=escape(str(invoice.get("issuedAt", ""))),
            status=escape(status),
            status_class=status_class,
            patient_name=escape(str(invoice.get("patientName", ""))),
            patient_mrn=escape(str(invoice.get("patientMrn", ""))),
            patient_phone=escape(str(invoice.get("patientPhone") or "—")),
            admission_date=escape(str(invoice.get("admissionDate") or "—")),
            discharge_date=escape(str(invoice.get("dischargeDate") or "Ongoing / OPD")),
            payment_method=escape(str(invoice.get("paymentMethod") or "—")),
            items="\n".join(item_rows),
            subtotal=escape(inr(invoice.get("subtotal", 0), 2)),
            tax=escape(inr(invoice.get("tax", 0), 2)),
            discount=escape(inr(invoice.get("discount", 0), 2)),
            grand_total=escape(inr(invoice.get("grandTotal", 0), 2)),
            notes=notes,
            tpa_row=tpa_row,
        )

    def close(self) -> None:
        try:
            self.grab_release()
        except Exception:
            pass
        self.destroy()


_RECEIPT_TEMPLATE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Aegis Health Receipt · $invoice_number</title>
<style>
  * { box-sizing: border-box; }
  body {
    margin: 0; background: #eef2f7; color: #0f172a;
    font-family: "Segoe UI", Arial, sans-serif; -webkit-print-color-adjust: exact;
  }
  .toolbar {
    max-width: 210mm; margin: 16px auto 0; display: flex; justify-content: flex-end;
  }
  .toolbar button {
    font: 600 12px "Segoe UI", Arial, sans-serif; color: #fff; background: #0f172a;
    border: 0; border-radius: 6px; padding: 9px 16px; cursor: pointer;
  }
  .sheet {
    width: 210mm; min-height: 280mm; margin: 16px auto 30px; background: #fff;
    padding: 16mm 15mm; box-shadow: 0 10px 30px rgba(15, 23, 42, .12);
  }
  .letterhead { display: flex; justify-content: space-between; align-items: flex-start; gap: 20px; }
  .brand { font-size: 25px; font-weight: 800; letter-spacing: 1.5px; color: #0f172a; }
  .tagline { font-size: 10px; font-weight: 700; letter-spacing: 1px; color: #64748b; text-transform: uppercase; }
  .hospital-meta { font-size: 9px; color: #94a3b8; text-align: right; line-height: 1.6; }
  .rule { border-top: 2px solid #0f172a; margin: 14px 0 18px; }
  .meta { display: flex; justify-content: space-between; gap: 30px; }
  .label { font-size: 8px; font-weight: 700; letter-spacing: .8px; color: #94a3b8; text-transform: uppercase; }
  .patient-name { font-size: 15px; font-weight: 700; margin: 4px 0 3px; }
  .small { font-size: 9.5px; color: #64748b; line-height: 1.7; }
  .invoice-meta { min-width: 290px; }
  .invoice-meta .row { display: flex; justify-content: space-between; gap: 20px; font-size: 9.5px; padding: 2px 0; }
  .invoice-meta .key { color: #94a3b8; font-weight: 600; }
  .invoice-meta .val { font-family: Consolas, monospace; color: #334155; }
  .status {
    display: inline-block; border-radius: 20px; padding: 3px 10px; font-size: 9px;
    font-weight: 800; letter-spacing: .5px; text-transform: uppercase;
  }
  .status.paid { background: #ecfdf5; color: #047857; }
  .status.pending { background: #fffbeb; color: #b45309; }
  .status.partial { background: #eff6ff; color: #1d4ed8; }
  .tpa {
    margin-top: 13px; background: #eff6ff; color: #1d4ed8; border-radius: 5px;
    padding: 7px 10px; font-size: 9.5px; font-weight: 700; display: inline-block;
  }
  table { width: 100%; border-collapse: collapse; margin-top: 20px; }
  thead th {
    background: #f8fafc; color: #94a3b8; font-size: 8px; letter-spacing: .6px;
    text-align: left; padding: 8px 7px; border-bottom: 1px solid #e2e8f0; text-transform: uppercase;
  }
  tbody td { font-size: 9.5px; color: #475569; padding: 8px 7px; border-bottom: 1px solid #eef2f7; vertical-align: top; }
  tbody td.num { text-align: right; font-family: Consolas, monospace; white-space: nowrap; }
  tbody td.strong { color: #0f172a; font-weight: 700; }
  .totals { width: 280px; margin: 14px 0 0 auto; }
  .totals .row { display: flex; justify-content: space-between; font-size: 9.5px; color: #64748b; padding: 3px 0; }
  .totals .row .amount { font-family: Consolas, monospace; }
  .totals .discount { color: #047857; }
  .totals .grand {
    border-top: 1px solid #cbd5e1; margin-top: 6px; padding-top: 8px;
    color: #0f172a; font-size: 13px; font-weight: 800;
  }
  .totals .grand .amount { font-size: 16px; }
  .below { display: flex; justify-content: space-between; gap: 40px; margin-top: 32px; }
  .notes { max-width: 115mm; }
  .notes p { font-size: 9.5px; color: #475569; line-height: 1.6; margin: 5px 0 0; }
  .signature { min-width: 55mm; text-align: center; padding-top: 26px; }
  .signature .line { border-top: 1px solid #cbd5e1; padding-top: 5px; font-size: 8.5px; color: #94a3b8; }
  .fineprint {
    border-top: 1px solid #e2e8f0; margin-top: 26px; padding-top: 10px;
    font-size: 8px; color: #94a3b8; text-align: center;
  }
  @media print {
    body { background: #fff; }
    .toolbar { display: none; }
    .sheet { width: auto; min-height: auto; margin: 0; padding: 10mm 12mm; box-shadow: none; }
    @page { size: A4; margin: 8mm; }
  }
</style>
</head>
<body>
  <div class="toolbar"><button onclick="window.print()">Print / Save as PDF</button></div>
  <div class="sheet">
    <div class="letterhead">
      <div>
        <div class="brand">AEGIS HEALTH</div>
        <div class="tagline">Multi-Specialty Hospital &amp; Research Centre</div>
      </div>
      <div class="hospital-meta">
        Aegis Health Campus, Sector 21<br>
        Navi Mumbai 400705, Maharashtra<br>
        +91 22 4000 8800 · billing@aegishealth.in<br>
        GSTIN 27AEGIS4821F1Z5
      </div>
    </div>
    <div class="rule"></div>
    <div class="meta">
      <div>
        <div class="label">Billed To</div>
        <div class="patient-name">$patient_name</div>
        <div class="small">
          MRN: $patient_mrn<br>
          Phone: $patient_phone<br>
          Admission: $admission_date<br>
          Discharge: $discharge_date
        </div>
      </div>
      <div class="invoice-meta">
        <div class="row"><span class="key">INVOICE NUMBER</span><span class="val">$invoice_number</span></div>
        <div class="row"><span class="key">ISSUED AT</span><span class="val">$issued_at</span></div>
        <div class="row"><span class="key">PAYMENT METHOD</span><span class="val">$payment_method</span></div>
        <div class="row" style="margin-top: 5px"><span class="key">STATUS</span><span class="status $status_class">$status</span></div>
      </div>
    </div>
    $tpa_row
    <table>
      <thead>
        <tr>
          <th style="width: 24px">#</th>
          <th>Description</th>
          <th style="width: 92px">Category</th>
          <th style="width: 45px; text-align: right">Qty</th>
          <th style="width: 82px; text-align: right">Unit Price</th>
          <th style="width: 92px; text-align: right">Amount</th>
        </tr>
      </thead>
      <tbody>
        $items
      </tbody>
    </table>
    <div class="totals">
      <div class="row"><span>Subtotal</span><span class="amount">$subtotal</span></div>
      <div class="row"><span>GST</span><span class="amount">$tax</span></div>
      <div class="row discount"><span>Discount</span><span class="amount">- $discount</span></div>
      <div class="row grand"><span>Grand Total</span><span class="amount">$grand_total</span></div>
    </div>
    <div class="below">
      <div class="notes">
        <div class="label">Notes</div>
        <p>$notes</p>
      </div>
      <div class="signature">
        <div class="line">Authorized Signatory · Finance</div>
      </div>
    </div>
    <div class="fineprint">
      This is a computer-generated invoice. Please retain it for insurance and tax records.
    </div>
  </div>
</body>
</html>
"""
