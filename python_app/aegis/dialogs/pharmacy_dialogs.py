"""Pharmacy dispensation, formulary intake and diagnostics dialogs."""

from __future__ import annotations

from datetime import date, timedelta
from typing import Any

import customtkinter as ctk

from .. import theme
from ..utils import inr, safe_float, safe_int
from ..widgets import (
    BaseDialog,
    Card,
    font,
    field,
    section_label,
    tinted_button,
    two_column_form,
    value,
)

CATEGORIES = [
    "Antibiotics",
    "Cardiovascular",
    "Analgesics",
    "Respiratory",
    "IV Fluids",
    "Emergency",
    "Vitamins",
]
DOSAGE_FORMS = ["Tablet", "Capsule", "Injection", "IV Infusion", "Syrup", "Ointment"]
UNITS = ["Tablets", "Capsules", "Vials", "Bottles", "Ampoules", "Tubes", "Sachets"]
LAB_DEPARTMENTS = ["Biochemistry", "Hematology", "Radiology", "Microbiology", "Pathology"]
LAB_PRIORITIES = ["Routine", "STAT Urgent"]


class DispenseMedicineDialog(BaseDialog):
    def __init__(self, app: Any, medicine: dict) -> None:
        self.medicine = medicine
        super().__init__(
            app,
            "Dispense Medication",
            "Bedside formulary dispensation and automatic stock reconciliation.",
            width=590,
            height=600,
        )

        stock = int(medicine.get("stock", 0))
        unit = medicine.get("unit", "units")

        info = Card(self.body, corner_radius=10)
        info.pack(fill="x", padx=2, pady=(2, 12))
        info.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(
            info,
            text=medicine.get("name", ""),
            font=font(15, bold=True),
            text_color=theme.TEXT,
            anchor="w",
        ).grid(row=0, column=0, sticky="w", padx=15, pady=(13, 1))
        ctk.CTkLabel(
            info,
            text=f"{medicine.get('genericName', '')}  ·  {medicine.get('code', '')}",
            font=font(10),
            text_color=theme.MUTED,
            anchor="w",
        ).grid(row=1, column=0, sticky="w", padx=15)

        chips = ctk.CTkFrame(info, fg_color="transparent")
        chips.grid(row=2, column=0, sticky="w", padx=15, pady=(10, 14))
        for text, fg, bg in (
            (f"Stock {stock} {unit}", theme.EMERALD if stock > int(medicine.get("minStock", 0)) else theme.AMBER,
             theme.EMERALD_BG if stock > int(medicine.get("minStock", 0)) else theme.AMBER_BG),
            (f"Unit price {inr(medicine.get('unitPrice', 0), 2)}", theme.TEXT_SECONDARY, theme.CARD_ALT),
            (medicine.get("category", ""), theme.BLUE, theme.BLUE_BG),
            (f"Batch {medicine.get('batchNumber', '—')}", theme.TEXT_SECONDARY, theme.CARD_ALT),
        ):
            ctk.CTkLabel(
                chips,
                text=text,
                font=font(9, bold=True),
                text_color=fg,
                fg_color=bg,
                corner_radius=5,
                padx=8,
                height=23,
            ).pack(side="left", padx=(0, 6))

        form = ctk.CTkFrame(self.body, fg_color="transparent")
        form.pack(fill="x", padx=2)
        two_column_form(form, 2)
        row = 0

        section_label(form, "Dispensation details", row); row += 1
        self.quantity = field(
            form, f"Quantity to dispense ({unit}) *", row, column=0, default=1, mono=True,
        )
        self.quantity.bind("<KeyRelease>", lambda _e: self._update_preview())
        self.recipient = field(
            form, "Patient / ward allocation", row, column=1,
            placeholder="e.g. ICU-02 · Rohan Deshmukh",
        )
        self.recipient.bind("<KeyRelease>", lambda _e: None)
        row += 1

        quick = ctk.CTkFrame(form, fg_color="transparent")
        quick.grid(row=row, column=0, columnspan=2, sticky="w", padx=7, pady=(0, 8))
        ctk.CTkLabel(
            quick, text="Quick quantity", font=font(9, bold=True), text_color=theme.FAINT,
        ).pack(side="left", padx=(0, 7))
        for amount in (1, 2, 5, 10, 20):
            tinted_button(
                quick, str(amount), lambda qty=amount: self._set_quantity(qty),
                color=theme.TEXT_SECONDARY, bg=theme.CARD_ALT, border=theme.BORDER_STRONG,
                height=24, width=38, font=font(9, bold=True),
            ).pack(side="left", padx=(0, 4))
        row += 1

        self.preview_card = ctk.CTkFrame(
            form, fg_color=theme.CARD_ALT, corner_radius=8,
            border_width=1, border_color=theme.BORDER,
        )
        self.preview_card.grid(row=row, column=0, columnspan=2, sticky="ew", padx=7, pady=(4, 4))
        self.preview_label = ctk.CTkLabel(
            self.preview_card, text="", font=font(10, mono=True),
            text_color=theme.TEXT_SECONDARY, anchor="w", justify="left",
        )
        self.preview_label.pack(fill="x", padx=12, pady=12)

        self._update_preview()
        self.add_footer("Confirm Dispensation", self.submit)

    def _set_quantity(self, amount: int) -> None:
        self.quantity.delete(0, "end")
        self.quantity.insert(0, str(amount))
        self._update_preview()

    def _update_preview(self) -> None:
        quantity = safe_int(value(self.quantity), 0)
        stock = int(self.medicine.get("stock", 0))
        unit = self.medicine.get("unit", "units")
        unit_price = float(self.medicine.get("unitPrice", 0))
        if quantity <= 0:
            text = "Enter a quantity to preview the stock balance."
            color = theme.MUTED
        elif quantity > stock:
            text = f"Cannot dispense {quantity} {unit} — only {stock} {unit} available."
            color = theme.ROSE
        else:
            text = (
                f"{quantity} {unit} × {inr(unit_price, 2)} = {inr(quantity * unit_price, 2)}\n"
                f"Remaining stock after dispensation: {stock - quantity} {unit}"
            )
            color = theme.EMERALD if stock - quantity > int(self.medicine.get("minStock", 0)) else theme.AMBER
        self.preview_label.configure(text=text, text_color=color)

    def submit(self) -> None:
        quantity = safe_int(value(self.quantity), 0)
        stock = int(self.medicine.get("stock", 0))
        if quantity <= 0:
            self.app.toast("Quantity must be greater than zero.", error=True)
            return
        if quantity > stock:
            self.app.toast(
                f"Insufficient stock. Available: {stock} {self.medicine.get('unit', 'units')}.",
                error=True,
            )
            return
        if self.run_action(
            self.store.dispense_medicine,
            self.medicine["id"],
            quantity,
            value(self.recipient),
        ):
            self.close()


class AddMedicineDialog(BaseDialog):
    def __init__(self, app: Any) -> None:
        super().__init__(
            app,
            "Add New Medicine to Formulary",
            "Register a new pharmacy SKU, reorder threshold and batch information.",
            width=760,
            height=760,
        )

        form = ctk.CTkFrame(self.body, fg_color="transparent")
        form.pack(fill="x", padx=2, pady=2)
        two_column_form(form, 2)
        row = 0

        section_label(form, "1. Drug identification", row); row += 1
        self.name = field(
            form, "Brand name & strength *", row, colspan=2,
            placeholder="e.g. Augmentin 625 Duo",
        ); row += 1
        self.generic = field(
            form, "Generic / chemical name *", row, colspan=2,
            placeholder="e.g. Amoxicillin + Clavulanic Acid",
        ); row += 1

        section_label(form, "2. Classification & form", row); row += 1
        self.category = field(form, "Therapeutic category", row, column=0,
                              kind="option", values=CATEGORIES, default="Antibiotics")
        self.dosage = field(form, "Dosage form", row, column=1,
                            kind="option", values=DOSAGE_FORMS, default="Tablet"); row += 1

        section_label(form, "3. Stock, pricing & reorder levels", row); row += 1
        self.stock = field(form, "Initial stock quantity *", row, column=0, default=100, mono=True)
        self.unit = field(form, "Unit of measure", row, column=1, kind="option",
                          values=UNITS, default="Tablets"); row += 1
        self.min_stock = field(form, "Minimum reorder level", row, column=0, default=25, mono=True)
        self.price = field(form, "Unit price (₹) *", row, column=1, default="0.00", mono=True); row += 1

        section_label(form, "4. Batch & expiry tracking", row); row += 1
        self.batch = field(form, "Batch number", row, column=0, default="BATCH-2026A", mono=True)
        self.expiry = field(
            form, "Expiry date (YYYY-MM-DD)", row, column=1,
            default=(date.today() + timedelta(days=730)).isoformat(), mono=True,
        ); row += 1

        self.add_footer("Add to Inventory", self.submit)

    def submit(self) -> None:
        name = value(self.name)
        generic = value(self.generic)
        if not name:
            self.app.toast("Medicine brand name is required.", error=True)
            return
        if not generic:
            self.app.toast("Generic / chemical name is required.", error=True)
            return

        stock = safe_int(value(self.stock), -1)
        minimum = safe_int(value(self.min_stock), -1)
        price = safe_float(value(self.price), -1)
        if stock < 0:
            self.app.toast("Initial stock must be zero or greater.", error=True)
            return
        if minimum < 0:
            self.app.toast("Minimum reorder level must be zero or greater.", error=True)
            return
        if price < 0:
            self.app.toast("Unit price must be zero or greater.", error=True)
            return
        if minimum > stock:
            self.app.toast("Minimum reorder level cannot exceed the initial stock.", error=True)
            return

        data = {
            "name": name,
            "genericName": generic,
            "category": self.category.get(),
            "dosageForm": self.dosage.get(),
            "stock": stock,
            "unit": self.unit.get(),
            "minStock": minimum,
            "unitPrice": price,
            "batchNumber": value(self.batch) or "BATCH-2026A",
            "expiryDate": value(self.expiry) or (date.today() + timedelta(days=730)).isoformat(),
        }
        if self.run_action(self.store.add_medicine, data):
            self.close()


class LabOrderDialog(BaseDialog):
    def __init__(self, app: Any) -> None:
        super().__init__(
            app,
            "Create Diagnostic Requisition",
            "Raise a laboratory or imaging investigation for a registered patient.",
            width=700,
            height=690,
        )
        self._patient_labels = [
            f"{patient.get('name')} · {patient.get('mrn')} · {patient.get('ward') or patient.get('status', 'OPD')}"
            for patient in self.store.patients
        ]
        self._patient_by_label = dict(zip(self._patient_labels, self.store.patients))
        self._doctor_labels = [
            f"{doctor.get('name')} · {doctor.get('department')}"
            for doctor in self.store.doctors
        ]
        self._doctor_by_label = dict(zip(self._doctor_labels, self.store.doctors))

        form = ctk.CTkFrame(self.body, fg_color="transparent")
        form.pack(fill="x", padx=2, pady=2)
        two_column_form(form, 2)
        row = 0

        section_label(form, "1. Patient & ordering clinician", row); row += 1
        self.patient = field(
            form, "Select patient *", row, colspan=2, kind="option",
            values=self._patient_labels or ["No patients registered"],
            default=self._patient_labels[0] if self._patient_labels else "",
        )
        self.patient.configure(command=self._patient_changed); row += 1
        self.doctor = field(
            form, "Ordering physician *", row, colspan=2, kind="option",
            values=self._doctor_labels or ["No doctors configured"],
            default=self._doctor_labels[0] if self._doctor_labels else "",
        ); row += 1

        section_label(form, "2. Investigation details", row); row += 1
        self.test = field(
            form, "Test / investigation name *", row, colspan=2,
            placeholder="e.g. Arterial Blood Gas (ABG), Serum Electrolytes, CT Head",
        ); row += 1
        self.department = field(
            form, "Laboratory / department", row, column=0, kind="option",
            values=LAB_DEPARTMENTS, default="Biochemistry",
        )
        self.priority = field(
            form, "Clinical priority", row, column=1, kind="option",
            values=LAB_PRIORITIES, default="Routine",
        ); row += 1
        self.indication = field(
            form, "Clinical indication / specimen notes", row, colspan=2, kind="text",
            height=74, placeholder="e.g. Rule out acute coronary syndrome; fasting sample required.",
        ); row += 1

        self._patient_changed(self.patient.get())
        self.add_footer("Issue Requisition", self.submit)

    def _patient_changed(self, label: str) -> None:
        patient = self._patient_by_label.get(label)
        if not patient:
            return
        doctor_id = patient.get("assignedDoctorId")
        for doctor_label, doctor in self._doctor_by_label.items():
            if doctor.get("id") == doctor_id:
                self.doctor.set(doctor_label)
                break

    def submit(self) -> None:
        patient = self._patient_by_label.get(self.patient.get())
        if not patient:
            self.app.toast("Please select a registered patient.", error=True)
            return
        test = value(self.test)
        if not test:
            self.app.toast("Test or investigation name is required.", error=True)
            return
        doctor = self._doctor_by_label.get(self.doctor.get())
        priority = self.priority.get()
        data = {
            "patientName": patient.get("name"),
            "patientMrn": patient.get("mrn"),
            "patientId": patient.get("id"),
            "testName": test,
            "department": self.department.get(),
            "orderedBy": doctor.get("name") if doctor else self.doctor.get().split(" · ")[0],
            "status": "Pending",
            "priority": priority,
            "notes": value(self.indication),
        }
        if self.run_action(self.store.create_lab_order, data):
            self.close()


class LabResultDialog(BaseDialog):
    TEMPLATES = [
        ("Within normal limits", "All measured parameters are within the established reference range. No acute abnormality detected."),
        ("Abnormal · correlate", "Abnormal values detected. Please correlate clinically and consider repeat sampling / additional imaging."),
        ("Critical value", "CRITICAL VALUE — immediate clinician notification advised. Repeat sample recommended for confirmation."),
    ]

    def __init__(self, app: Any, order: dict) -> None:
        self.order = order
        super().__init__(
            app,
            "Log Diagnostic Findings",
            "Finalize and digitally sign the laboratory result for the patient chart.",
            width=700,
            height=700,
        )

        info = Card(self.body, corner_radius=10)
        info.pack(fill="x", padx=2, pady=(2, 12))
        info.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(
            info,
            text=f"{order.get('testName', '')}",
            font=font(15, bold=True),
            text_color=theme.TEXT,
            anchor="w",
        ).grid(row=0, column=0, sticky="w", padx=15, pady=(13, 1))
        ctk.CTkLabel(
            info,
            text=(
                f"{order.get('orderNumber')}  ·  {order.get('patientName')} "
                f"({order.get('patientMrn')})  ·  {order.get('department')}"
            ),
            font=font(10, mono=True),
            text_color=theme.MUTED,
            anchor="w",
        ).grid(row=1, column=0, sticky="w", padx=15)
        ctk.CTkLabel(
            info,
            text=(
                f"Ordered by {order.get('orderedBy')} on {order.get('orderedDate')}  ·  "
                f"Priority: {order.get('priority', 'Routine')}"
            ),
            font=font(9),
            text_color=theme.FAINT,
            anchor="w",
        ).grid(row=2, column=0, sticky="w", padx=15, pady=(2, 13))

        form = ctk.CTkFrame(self.body, fg_color="transparent")
        form.pack(fill="x", padx=2)
        two_column_form(form, 2)

        section_label(form, "Findings / reference values *", 0)
        self.result = field(
            form, "Diagnostic findings *", 1, colspan=2, kind="text", height=190,
            mono=True,
            placeholder=(
                "e.g. Hemoglobin: 13.2 g/dL (Normal: 12.0-16.0)\n"
                "WBC: 7,800/uL\nPlatelets: 240,000/uL"
            ),
        )
        if order.get("resultSummary"):
            self.result.delete("1.0", "end")
            self.result.insert("1.0", order["resultSummary"])

        quick = ctk.CTkFrame(form, fg_color="transparent")
        quick.grid(row=2, column=0, columnspan=2, sticky="w", padx=7, pady=(2, 8))
        ctk.CTkLabel(
            quick, text="Quick templates", font=font(9, bold=True), text_color=theme.FAINT,
        ).pack(side="left", padx=(0, 7))
        for label, body in self.TEMPLATES:
            tinted_button(
                quick, label, lambda text=body: self._apply_template(text),
                color=theme.TEXT_SECONDARY, bg=theme.CARD_ALT, border=theme.BORDER_STRONG,
                height=25, font=font(9, bold=True),
            ).pack(side="left", padx=(0, 4))

        ctk.CTkLabel(
            form,
            text=(
                "Finalizing this result marks the requisition completed and publishes the "
                "findings to the patient's clinical chart."
            ),
            font=font(9),
            text_color=theme.MUTED,
            anchor="w",
            justify="left",
        ).grid(row=3, column=0, columnspan=2, sticky="w", padx=7, pady=(2, 2))

        self.add_footer("Finalize & Sign Result", self.submit, submit_color=theme.EMERALD)

    def _apply_template(self, text: str) -> None:
        self.result.delete("1.0", "end")
        self.result.insert("1.0", text)

    def submit(self) -> None:
        findings = value(self.result)
        if not findings:
            self.app.toast("Please enter the diagnostic findings.", error=True)
            return
        if self.run_action(self.store.update_lab_result, self.order["id"], findings):
            self.close()
