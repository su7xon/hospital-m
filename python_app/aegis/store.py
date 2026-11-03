"""Domain logic for Aegis Health.

The store owns the in-memory hospital state, persists every mutation to
SQLite, and emits lightweight UI notifications through callbacks.
"""

from __future__ import annotations

import re
import uuid
from typing import Any, Callable

from .database import Database
from .utils import now_str


class StoreError(Exception):
    """Raised when a clinical/business rule prevents an action."""


class HospitalStore:
    def __init__(self, database: Database | None = None) -> None:
        self.db = database or Database()
        self.on_change: Callable[[], None] | None = None
        self.on_toast: Callable[[str], None] | None = None
        self._load()

    # ------------------------------------------------------------------ state
    def _load(self) -> None:
        data = self.db.load_all()
        self.patients: list[dict] = data["patients"]
        self.doctors: list[dict] = data["doctors"]
        self.beds: list[dict] = data["beds"]
        self.appointments: list[dict] = data["appointments"]
        self.emergency_cases: list[dict] = data["emergency_cases"]
        self.medicines: list[dict] = data["medicines"]
        self.lab_orders: list[dict] = data["lab_orders"]
        self.invoices: list[dict] = data["invoices"]

    def _collection(self, kind: str) -> list[dict]:
        return getattr(self, kind)

    def _persist(self, kinds: list[str]) -> None:
        for kind in kinds:
            self.db.replace_kind(kind, self._collection(kind))

    def _commit(self, kinds: list[str], message: str | None = None) -> None:
        self._persist(kinds)
        if self.on_change:
            self.on_change()
        if message and self.on_toast:
            self.on_toast(message)

    @staticmethod
    def _new_id(prefix: str) -> str:
        return f"{prefix}-{uuid.uuid4().hex[:10]}"

    @staticmethod
    def _next_number(records: list[dict], field: str, prefix: str, fallback: int) -> int:
        numbers: list[int] = []
        pattern = re.compile(rf"{re.escape(prefix)}(\d+)")
        for record in records:
            match = pattern.search(str(record.get(field, "")))
            if match:
                numbers.append(int(match.group(1)))
        return (max(numbers) + 1) if numbers else fallback

    # --------------------------------------------------------------- lookups
    def patient(self, patient_id: str) -> dict | None:
        return next((p for p in self.patients if p.get("id") == patient_id), None)

    def doctor(self, doctor_id: str) -> dict | None:
        return next((d for d in self.doctors if d.get("id") == doctor_id), None)

    def bed(self, bed_id: str) -> dict | None:
        return next((b for b in self.beds if b.get("id") == bed_id), None)

    def bed_by_code(self, code: str) -> dict | None:
        return next((b for b in self.beds if b.get("code") == code), None)

    # --------------------------------------------------------------- patients
    def admit_patient(self, data: dict, vitals: dict | None = None) -> dict:
        name = str(data.get("name", "")).strip()
        if not name:
            raise StoreError("Patient name is required.")
        if not str(data.get("assignedDoctorId", "")).strip():
            raise StoreError("Please assign an attending physician.")

        bed_code = data.get("bedNumber") or None
        bed = self.bed_by_code(bed_code) if bed_code else None
        if bed_code and not bed:
            raise StoreError(f"Bed {bed_code} was not found.")
        if bed and bed.get("status") != "Available":
            raise StoreError(f"Bed {bed_code} is not available right now.")

        doctor = self.doctor(data.get("assignedDoctorId", ""))
        if not doctor:
            raise StoreError("Selected doctor was not found.")

        mrn = f"HSP-{self._next_number(self.patients, 'mrn', 'HSP-', 4140)}"
        patient_id = self._new_id("pat")
        stamp = now_str()

        vital = {
            "id": self._new_id("v"),
            "recordedAt": stamp,
            "heartRate": int((vitals or {}).get("heartRate", 76)),
            "bloodPressure": (vitals or {}).get("bloodPressure", "120/80"),
            "spo2": int((vitals or {}).get("spo2", 98)),
            "temperature": float((vitals or {}).get("temperature", 98.6)),
            "respiratoryRate": int((vitals or {}).get("respiratoryRate", 16)),
            "recordedBy": (vitals or {}).get("recordedBy", "Intake Triage Nurse"),
        }

        patient = {
            **data,
            "name": name,
            "id": patient_id,
            "mrn": mrn,
            "admissionDate": data.get("admissionDate") or stamp,
            "status": "ICU" if bed and bed.get("ward") == "ICU" else data.get("status", "Admitted"),
            "ward": bed.get("ward") if bed else data.get("ward", "General Ward A"),
            "bedNumber": bed.get("code") if bed else None,
            "assignedDoctorId": doctor["id"],
            "assignedDoctorName": doctor.get("name", "Attending Physician"),
            "department": doctor.get("department", "Internal Medicine"),
            "vitals": [vital],
        }
        patient.setdefault("notes", [])
        patient.setdefault("allergies", ["No known drug allergies (NKDA)"])
        patient.setdefault("diagnoses", ["Pending clinical evaluation"])
        if not patient["notes"]:
            patient["notes"] = [f"Admitted on {stamp} by Clinical Intake Desk."]

        self.patients.insert(0, patient)

        if bed:
            bed.update({
                "status": "Occupied",
                "patientId": patient_id,
                "patientName": name,
                "patientMrn": mrn,
                "admittedSince": stamp[:10],
            })
        doctor["activePatients"] = int(doctor.get("activePatients", 0)) + 1

        self._commit(
            ["patients", "beds", "doctors"],
            f"Admitted {name} ({mrn}) successfully.",
        )
        return patient

    def discharge_patient(self, patient_id: str, summary: str) -> None:
        patient = self.patient(patient_id)
        if not patient:
            raise StoreError("Patient record not found.")
        if patient.get("status") == "Discharged":
            raise StoreError("This patient is already discharged.")
        if not summary.strip():
            raise StoreError("Please enter a discharge summary.")

        stamp = now_str()
        patient["status"] = "Discharged"
        patient["dischargeDate"] = stamp
        patient.setdefault("notes", []).insert(0, f"Discharge Summary: {summary.strip()} (Recorded on {stamp})")

        bed = self.bed_by_code(patient.get("bedNumber") or "")
        if bed:
            bed.update({
                "status": "Cleaning",
                "patientId": None,
                "patientName": None,
                "patientMrn": None,
                "admittedSince": None,
            })

        doctor = self.doctor(patient.get("assignedDoctorId", ""))
        if doctor:
            doctor["activePatients"] = max(0, int(doctor.get("activePatients", 0)) - 1)

        self._commit(
            ["patients", "beds", "doctors"],
            f"{patient['name']} discharged. Bed {patient.get('bedNumber') or ''} marked for cleaning.",
        )

    def add_vital(self, patient_id: str, vital: dict) -> None:
        patient = self.patient(patient_id)
        if not patient:
            raise StoreError("Patient record not found.")
        record = {
            "id": self._new_id("v"),
            "recordedAt": now_str(),
            "heartRate": int(vital.get("heartRate", 0)),
            "bloodPressure": str(vital.get("bloodPressure", "")).strip(),
            "spo2": int(vital.get("spo2", 0)),
            "temperature": float(vital.get("temperature", 0)),
            "respiratoryRate": int(vital.get("respiratoryRate", 0)),
            "recordedBy": str(vital.get("recordedBy", "Staff Nurse")).strip() or "Staff Nurse",
        }
        patient.setdefault("vitals", []).insert(0, record)
        self._commit(
            ["patients"],
            f"Vitals logged for {patient['name']} (HR {record['heartRate']} bpm · BP {record['bloodPressure']}).",
        )

    def add_note(self, patient_id: str, note: str) -> None:
        patient = self.patient(patient_id)
        if not patient:
            raise StoreError("Patient record not found.")
        if not note.strip():
            raise StoreError("Clinical note cannot be empty.")
        patient.setdefault("notes", []).insert(0, f"{now_str()} - {note.strip()}")
        self._commit(["patients"], "Clinical progress note saved.")

    def transfer_bed(self, patient_id: str, bed_id: str) -> None:
        patient = self.patient(patient_id)
        bed = self.bed(bed_id)
        if not patient or not bed:
            raise StoreError("Patient or target bed was not found.")
        if bed.get("status") != "Available":
            raise StoreError(f"Bed {bed.get('code')} is not available for transfer.")

        old_bed = self.bed_by_code(patient.get("bedNumber") or "")
        if old_bed:
            old_bed.update({
                "status": "Cleaning",
                "patientId": None,
                "patientName": None,
                "patientMrn": None,
                "admittedSince": None,
            })

        bed.update({
            "status": "Occupied",
            "patientId": patient["id"],
            "patientName": patient["name"],
            "patientMrn": patient["mrn"],
            "admittedSince": patient.get("admissionDate", now_str())[:10],
        })

        patient["ward"] = bed.get("ward")
        patient["bedNumber"] = bed.get("code")
        patient.setdefault("notes", []).insert(
            0,
            f"Transferred from {old_bed.get('code') if old_bed else 'None'} to "
            f"{bed.get('code')} ({bed.get('ward')}) on {now_str()}",
        )

        self._commit(
            ["patients", "beds"],
            f"Transferred {patient['name']} to {bed.get('code')} ({bed.get('ward')}).",
        )

    # ------------------------------------------------------------------- beds
    def update_bed_status(self, bed_id: str, status: str) -> None:
        bed = self.bed(bed_id)
        if not bed:
            raise StoreError("Bed not found.")
        if status == "Occupied":
            raise StoreError("Assign patients through the admission workflow.")
        bed.update({
            "status": status,
            "patientId": None,
            "patientName": None,
            "patientMrn": None,
            "admittedSince": None,
        })
        self._commit(["beds"], f"Bed {bed.get('code')} marked {status}.")

    # ----------------------------------------------------------- appointments
    def book_appointment(self, data: dict) -> dict:
        name = str(data.get("patientName", "")).strip()
        if not name:
            raise StoreError("Patient name is required.")
        doctor = self.doctor(data.get("doctorId", ""))
        if not doctor:
            raise StoreError("Please select a specialist.")

        number = f"APT-{self._next_number(self.appointments, 'appointmentNumber', 'APT-', 901)}"
        appointment = {
            **data,
            "id": self._new_id("apt"),
            "appointmentNumber": number,
            "patientName": name,
            "doctorId": doctor["id"],
            "doctorName": doctor.get("name", "Attending Specialist"),
            "department": doctor.get("department", "General OPD"),
            "status": "Scheduled",
        }
        self.appointments.insert(0, appointment)
        self._commit(
            ["appointments"],
            f"Appointment booked ({number}) with {appointment['doctorName']}.",
        )
        return appointment

    def update_appointment_status(self, appointment_id: str, status: str) -> None:
        appointment = next((a for a in self.appointments if a.get("id") == appointment_id), None)
        if not appointment:
            raise StoreError("Appointment not found.")
        appointment["status"] = status
        self._commit(["appointments"], f"Appointment status updated to \"{status}\".")

    # -------------------------------------------------------------- emergency
    def add_emergency_case(self, data: dict) -> dict:
        name = str(data.get("patientName", "")).strip()
        if not name:
            raise StoreError("Patient name or triage tag is required.")
        case = {
            **data,
            "id": self._new_id("er"),
            "patientName": name,
            "arrivalTime": __import__("datetime").datetime.now().strftime("%I:%M %p"),
            "status": data.get("status", "Waiting"),
        }
        self.emergency_cases.insert(0, case)
        self._commit(["emergency_cases"], f"Emergency triage case logged for {name}.")
        return case

    def update_emergency_status(self, er_id: str, status: str) -> None:
        case = next((c for c in self.emergency_cases if c.get("id") == er_id), None)
        if not case:
            raise StoreError("Emergency case not found.")
        case["status"] = status
        self._commit(["emergency_cases"], f"Triage status updated to \"{status}\".")

    def admit_emergency_case(self, er_id: str) -> None:
        case = next((c for c in self.emergency_cases if c.get("id") == er_id), None)
        if not case:
            raise StoreError("Emergency case not found.")
        if case.get("status") in ("Admitted", "Discharged"):
            raise StoreError("This emergency case is already closed.")

        bed = next((b for b in self.beds if b.get("status") == "Available"), None)
        if not bed:
            raise StoreError("No available bed. Please free a bed or admit via the intake form.")
        doctor = next((d for d in self.doctors if d.get("onDuty")), None) or (self.doctors[0] if self.doctors else None)
        if not doctor:
            raise StoreError("No physician is configured for admission.")

        patient = self.admit_patient({
            "name": case.get("patientName", "Emergency Patient"),
            "age": int(case.get("age", 0)),
            "gender": case.get("gender", "Other"),
            "bloodGroup": "O+",
            "phone": "+91 99999 00000",
            "address": "Emergency Admissions Intake",
            "emergencyContact": {
                "name": "Attendant on record",
                "relation": "Primary Contact",
                "phone": "+91 99999 00000",
            },
            "status": "ICU" if bed.get("ward") == "ICU" else "Admitted",
            "ward": bed.get("ward"),
            "bedNumber": bed.get("code"),
            "assignedDoctorId": doctor["id"],
            "assignedDoctorName": doctor.get("name"),
            "department": doctor.get("department"),
            "chiefComplaint": case.get("chiefComplaint", "Emergency admission"),
            "allergies": ["Pending confirmation"],
            "diagnoses": [f"Admitted via Emergency: {case.get('chiefComplaint', '')}"],
            "notes": [case.get("notes", ""), f"Emergency Vitals: {case.get('vitalsBrief', '')}"],
        })
        case["status"] = "Admitted"
        self._commit(
            ["emergency_cases"],
            f"ER patient {patient['name']} admitted to {patient.get('bedNumber')}.",
        )

    # --------------------------------------------------------------- pharmacy
    def dispense_medicine(self, medicine_id: str, quantity: int, recipient: str = "") -> None:
        medicine = next((m for m in self.medicines if m.get("id") == medicine_id), None)
        if not medicine:
            raise StoreError("Medicine not found.")
        if quantity <= 0:
            raise StoreError("Quantity must be greater than zero.")
        available = int(medicine.get("stock", 0))
        if quantity > available:
            raise StoreError(f"Insufficient stock for {medicine.get('name')}. Available: {available}")

        recipient = recipient.strip() or "Counter dispensation"
        medicine["stock"] = available - quantity
        medicine.setdefault("dispenseLog", []).insert(0, {
            "id": self._new_id("disp"),
            "quantity": quantity,
            "recipient": recipient,
            "dispensedAt": now_str(),
        })
        self._commit(
            ["medicines"],
            f"Dispensed {quantity} {medicine.get('unit')} of {medicine.get('name')} "
            f"to {recipient}. Remaining: {medicine['stock']}.",
        )

    def add_medicine(self, data: dict) -> dict:
        name = str(data.get("name", "")).strip()
        if not name:
            raise StoreError("Medicine name is required.")
        code = f"MED-{self._next_number(self.medicines, 'code', 'MED-', 101)}"
        medicine = {**data, "id": self._new_id("med"), "code": code, "name": name}
        self.medicines.insert(0, medicine)
        self._commit(["medicines"], f"Added {name} ({code}) to pharmacy inventory.")
        return medicine

    # ------------------------------------------------------------------- labs
    def create_lab_order(self, data: dict) -> dict:
        if not data.get("patientName"):
            raise StoreError("Please select a patient.")
        if not str(data.get("testName", "")).strip():
            raise StoreError("Test or investigation name is required.")
        number = f"LAB-{self._next_number(self.lab_orders, 'orderNumber', 'LAB-', 2401)}"
        order = {
            **data,
            "id": self._new_id("lab"),
            "orderNumber": number,
            "orderedDate": now_str(),
            "status": "Pending",
        }
        self.lab_orders.insert(0, order)
        self._commit(
            ["lab_orders"],
            f"Lab requisition {number} created for {order.get('patientName')}.",
        )
        return order

    def update_lab_result(self, order_id: str, result: str) -> None:
        order = next((o for o in self.lab_orders if o.get("id") == order_id), None)
        if not order:
            raise StoreError("Lab order not found.")
        if not result.strip():
            raise StoreError("Please enter diagnostic findings.")
        order["status"] = "Completed"
        order["resultSummary"] = result.strip()
        order["completedAt"] = now_str()
        self._commit(["lab_orders"], "Lab result uploaded and finalized.")

    # ---------------------------------------------------------------- billing
    def create_invoice(
        self,
        patient_id: str,
        items: list[dict],
        tax: float,
        discount: float,
        payment_status: str,
        payment_method: str | None = None,
        insurance_provider: str | None = None,
        notes: str = "",
    ) -> dict:
        patient = self.patient(patient_id)
        if not patient:
            raise StoreError("Please select a patient.")
        if not items:
            raise StoreError("Please add at least one line item to the bill.")

        clean_items = []
        for index, item in enumerate(items):
            quantity = float(item.get("quantity", 1))
            unit_price = float(item.get("unitPrice", 0))
            clean_items.append({
                **item,
                "id": item.get("id") or f"ii-{index}-{uuid.uuid4().hex[:5]}",
                "quantity": quantity,
                "unitPrice": unit_price,
                "total": quantity * unit_price,
            })

        subtotal = sum(item["total"] for item in clean_items)
        grand_total = subtotal + float(tax) - float(discount)
        number = f"INV-2026-{self._next_number(self.invoices, 'invoiceNumber', 'INV-2026-', 81):03d}"

        invoice = {
            "id": self._new_id("inv"),
            "invoiceNumber": number,
            "patientId": patient["id"],
            "patientName": patient.get("name", "Walk-in Patient"),
            "patientMrn": patient.get("mrn", "OPD-WALKIN"),
            "patientPhone": patient.get("phone", ""),
            "admissionDate": patient.get("admissionDate", "")[:10],
            "dischargeDate": patient.get("dischargeDate"),
            "items": clean_items,
            "subtotal": subtotal,
            "tax": float(tax),
            "discount": float(discount),
            "grandTotal": grand_total,
            "paymentStatus": payment_status,
            "paymentMethod": payment_method if payment_status == "Paid" else payment_method,
            "insuranceProvider": insurance_provider,
            "issuedAt": now_str(),
            "notes": notes,
        }
        self.invoices.insert(0, invoice)
        self._commit(
            ["invoices"],
            f"Invoice {number} generated ({self._money(grand_total)}).",
        )
        return invoice

    @staticmethod
    def _money(amount: float) -> str:
        from .utils import inr
        return inr(amount, 2)

    def update_invoice_payment(self, invoice_id: str, status: str, method: str | None = None) -> None:
        invoice = next((i for i in self.invoices if i.get("id") == invoice_id), None)
        if not invoice:
            raise StoreError("Invoice not found.")
        invoice["paymentStatus"] = status
        if method:
            invoice["paymentMethod"] = method
        self._commit(["invoices"], f"Invoice payment marked as \"{status}\".")

    # ----------------------------------------------------------------- doctors
    def toggle_doctor_duty(self, doctor_id: str) -> None:
        doctor = self.doctor(doctor_id)
        if not doctor:
            raise StoreError("Doctor not found.")
        doctor["onDuty"] = not bool(doctor.get("onDuty"))
        state = "On Duty" if doctor["onDuty"] else "Off Duty"
        self._commit(["doctors"], f"{doctor.get('name')} marked {state}.")

    # ------------------------------------------------------------------ reset
    def reset_data(self) -> None:
        self.db.reset()
        self._load()
        if self.on_change:
            self.on_change()
        if self.on_toast:
            self.on_toast("Hospital records reset to the initial verified clinical dataset.")
