"""Admission, OPD appointment and emergency triage dialogs."""

from __future__ import annotations

from datetime import datetime
from typing import Any

import customtkinter as ctk

from .. import theme
from ..utils import now_str, safe_float, safe_int
from ..widgets import (
    BaseDialog,
    field,
    font,
    section_label,
    two_column_form,
    value,
)

GENDERS = ["Male", "Female", "Other"]
BLOOD_GROUPS = ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]
TRIAGE_LEVELS = [
    "P1 - Resuscitation",
    "P2 - Emergency",
    "P3 - Urgent",
    "P4 - Semi-Urgent",
    "P5 - Non-Urgent",
]
TIME_SLOTS = [
    "09:00 AM", "09:30 AM", "10:00 AM", "10:30 AM", "11:00 AM", "11:30 AM",
    "12:00 PM", "02:30 PM", "03:00 PM", "03:30 PM", "04:00 PM",
]
CONSULT_TYPES = ["OPD", "Follow-up", "Review"]


class AdmitPatientDialog(BaseDialog):
    def __init__(self, app: Any) -> None:
        super().__init__(
            app,
            "Inpatient Admission Intake",
            "Electronic registration, ward bed allocation and baseline triage vitals.",
            width=820,
            height=780,
        )
        self._doctor_labels = [
            f"{doctor.get('name')} · {doctor.get('department')}"
            + (" · On Duty" if doctor.get("onDuty") else "")
            for doctor in self.store.doctors
        ]
        self._doctor_by_label = dict(zip(self._doctor_labels, self.store.doctors))
        available_beds = [b for b in self.store.beds if b.get("status") == "Available"]
        self._bed_labels = [
            f"{bed.get('code')} · {bed.get('ward')} · \u20b9{int(bed.get('dailyRate', 0)):,}/day"
            for bed in available_beds
        ]
        self._bed_by_label = dict(zip(self._bed_labels, available_beds))

        form = ctk.CTkFrame(self.body, fg_color="transparent")
        form.pack(fill="x", padx=2, pady=2)
        two_column_form(form, 2)
        row = 0

        section_label(form, "1. Patient demographics & identification", row); row += 1
        self.name = field(form, "Full legal name *", row, placeholder="e.g. Rahul Sharma"); row += 1
        self.age = field(form, "Age *", row, column=0, default=45)
        self.gender = field(form, "Biological gender", row, column=1, kind="option", values=GENDERS); row += 1
        self.blood = field(form, "Blood group", row, column=0, kind="option", values=BLOOD_GROUPS, default="B+")
        self.phone = field(form, "Contact phone *", row, column=1, default="+91 ", mono=True); row += 1
        self.address = field(form, "Residential address", row, placeholder="Street, locality, city"); row += 1

        section_label(form, "2. Emergency contact / guardian", row); row += 1
        self.kin_name = field(form, "Contact name", row, column=0, placeholder="Next of kin"); 
        self.kin_relation = field(form, "Relationship", row, column=1, placeholder="Spouse / Parent"); row += 1
        self.kin_phone = field(form, "Emergency phone", row, placeholder="+91...", mono=True); row += 1

        section_label(form, "3. Clinical assignment & ward allocation", row); row += 1
        self.doctor = field(
            form, "Attending physician *", row,
            kind="option", values=self._doctor_labels or ["No doctors configured"],
            default=self._doctor_labels[0] if self._doctor_labels else "",
            colspan=2,
        ); row += 1
        bed_options = (["No bed · OPD / day care"] + self._bed_labels) if self._bed_labels else ["No beds available"]
        self.bed = field(
            form, "Allocate inpatient bed", row, kind="option",
            values=bed_options, default=bed_options[0], colspan=2,
        ); row += 1
        self.complaint = field(
            form, "Chief presenting complaint *", row, colspan=2, kind="text",
            height=68, placeholder="e.g. Acute chest pain with diaphoresis for 2 hours",
        ); row += 1
        self.diagnosis = field(form, "Provisional diagnosis", row, column=0,
                               placeholder="e.g. Acute coronary syndrome")
        self.allergies = field(form, "Known drug allergies", row, column=1,
                               default="No known drug allergies (NKDA)"); row += 1

        section_label(form, "4. Baseline intake vitals", row); row += 1
        self.hr = field(form, "Heart rate (bpm)", row, column=0, default=76)
        self.bp = field(form, "Blood pressure", row, column=1, default="120/80", mono=True); row += 1
        self.spo2 = field(form, "SpO2 (%)", row, column=0, default=98)
        self.temp = field(form, "Temperature (°F)", row, column=1, default="98.6"); row += 1
        self.rr = field(form, "Respiratory rate (/min)", row, column=0, default=16)
        self.recorder = field(form, "Recorded by", row, column=1, default="Intake Triage Nurse"); row += 1

        self.add_footer("Confirm Admission", self.submit)

    def submit(self) -> None:
        name = value(self.name)
        if not name:
            self.app.toast("Please enter the patient's full name.", error=True)
            return
        if not value(self.phone):
            self.app.toast("Please enter a contact phone number.", error=True)
            return
        if not value(self.complaint):
            self.app.toast("Please enter the chief presenting complaint.", error=True)
            return
        if not self._doctor_by_label:
            self.app.toast("No doctors are configured. Cannot admit patient.", error=True)
            return

        doctor = self._doctor_by_label.get(self.doctor.get())
        if not doctor:
            self.app.toast("Please select an attending physician.", error=True)
            return
        bed_label = self.bed.get()
        bed = self._bed_by_label.get(bed_label)

        allergies = [part.strip() for part in value(self.allergies).split(",") if part.strip()]
        diagnosis = value(self.diagnosis)
        stamp = now_str()

        data = {
            "name": name,
            "age": safe_int(value(self.age), 0),
            "gender": self.gender.get(),
            "bloodGroup": self.blood.get(),
            "phone": value(self.phone),
            "address": value(self.address) or "Not specified",
            "emergencyContact": {
                "name": value(self.kin_name) or "Next of kin",
                "relation": value(self.kin_relation) or "Primary contact",
                "phone": value(self.kin_phone) or value(self.phone),
            },
            "admissionDate": stamp,
            "status": "ICU" if bed and bed.get("ward") == "ICU" else "Admitted",
            "ward": bed.get("ward") if bed else "General Ward A",
            "bedNumber": bed.get("code") if bed else None,
            "assignedDoctorId": doctor["id"],
            "assignedDoctorName": doctor.get("name"),
            "department": doctor.get("department"),
            "chiefComplaint": value(self.complaint),
            "allergies": allergies or ["No known drug allergies (NKDA)"],
            "diagnoses": [diagnosis] if diagnosis else ["Pending clinical evaluation"],
            "notes": [f"Admitted on {stamp} by Clinical Intake Desk."],
        }
        vitals = {
            "heartRate": safe_int(value(self.hr), 76),
            "bloodPressure": value(self.bp) or "120/80",
            "spo2": safe_int(value(self.spo2), 98),
            "temperature": safe_float(value(self.temp), 98.6),
            "respiratoryRate": safe_int(value(self.rr), 16),
            "recordedBy": value(self.recorder) or "Intake Triage Nurse",
        }
        if self.run_action(self.store.admit_patient, data, vitals):
            self.close()


class BookAppointmentDialog(BaseDialog):
    def __init__(self, app: Any) -> None:
        super().__init__(
            app,
            "Book Outpatient Consultation",
            "Schedule a specialist appointment slot and register the patient.",
            width=690,
            height=670,
        )
        self._doctor_labels = [
            f"{doctor.get('name')} · {doctor.get('department')} · {doctor.get('room')}"
            for doctor in self.store.doctors
        ]
        self._doctor_by_label = dict(zip(self._doctor_labels, self.store.doctors))

        form = ctk.CTkFrame(self.body, fg_color="transparent")
        form.pack(fill="x", padx=2, pady=2)
        two_column_form(form, 2)
        row = 0
        self.patient_name = field(form, "Patient full name *", row, colspan=2,
                                  placeholder="e.g. Ramesh Patel"); row += 1
        self.phone = field(form, "Contact phone *", row, column=0, default="+91 ", mono=True)
        self.mrn = field(form, "Existing hospital MRN (optional)", row, column=1,
                         placeholder="e.g. HSP-4109", mono=True); row += 1
        self.doctor = field(
            form, "Select specialist *", row, colspan=2, kind="option",
            values=self._doctor_labels or ["No specialists configured"],
            default=self._doctor_labels[0] if self._doctor_labels else "",
        ); row += 1
        self.date = field(form, "Date", row, column=0, default=datetime.now().strftime("%Y-%m-%d"), mono=True)
        self.time_slot = field(form, "Time slot", row, column=1, kind="option", values=TIME_SLOTS,
                               default="11:00 AM"); row += 1
        self.consult_type = field(form, "Consultation type", row, column=0, kind="option",
                                  values=CONSULT_TYPES); row += 1
        self.reason = field(form, "Chief symptom / clinical indication", row, colspan=2,
                            placeholder="e.g. Chronic back pain, review MRI spine reports")
        self.add_footer("Confirm Appointment", self.submit)

    def submit(self) -> None:
        name = value(self.patient_name)
        if not name:
            self.app.toast("Please enter the patient's name.", error=True)
            return
        if not value(self.phone):
            self.app.toast("Please enter a contact phone number.", error=True)
            return
        doctor = self._doctor_by_label.get(self.doctor.get())
        if not doctor:
            self.app.toast("Please select a specialist.", error=True)
            return
        data = {
            "patientName": name,
            "patientPhone": value(self.phone),
            "patientMrn": value(self.mrn) or None,
            "doctorId": doctor["id"],
            "doctorName": doctor.get("name"),
            "department": doctor.get("department"),
            "date": value(self.date) or datetime.now().strftime("%Y-%m-%d"),
            "timeSlot": self.time_slot.get(),
            "status": "Scheduled",
            "reason": value(self.reason) or "General specialist consultation",
            "type": self.consult_type.get(),
        }
        if self.run_action(self.store.book_appointment, data):
            self.close()


class EmergencyTriageDialog(BaseDialog):
    def __init__(self, app: Any) -> None:
        super().__init__(
            app,
            "Emergency Department Triage Intake",
            "Manchester Triage System · priority levels P1 through P5.",
            width=700,
            height=720,
        )
        self._doctor_names = [
            f"{doctor.get('name')} · {doctor.get('department')}"
            for doctor in self.store.doctors
        ]
        form = ctk.CTkFrame(self.body, fg_color="transparent")
        form.pack(fill="x", padx=2, pady=2)
        two_column_form(form, 2)
        row = 0
        self.patient_name = field(form, "Patient name / triage tag *", row, colspan=2,
                                  placeholder="e.g. Unknown Trauma Male #2"); row += 1
        self.age = field(form, "Age", row, column=0, default=38)
        self.gender = field(form, "Gender", row, column=1, kind="option", values=GENDERS); row += 1
        self.triage = field(form, "Triage priority category *", row, colspan=2, kind="option",
                            values=TRIAGE_LEVELS, default="P2 - Emergency"); row += 1
        self.complaint = field(form, "Emergency chief complaint & symptoms *", row, colspan=2,
                               kind="text", height=64,
                               placeholder="e.g. Acute severe shortness of breath, bilateral wheezing"); row += 1
        self.vitals = field(form, "Triage vitals summary", row, column=0,
                            default="BP: 130/85 | HR: 88 | SpO2: 97%")
        self.doctor = field(form, "Assigned ER physician", row, column=1, kind="option",
                            values=self._doctor_names or ["On-duty physician"],
                            default=self._doctor_names[0] if self._doctor_names else ""); row += 1
        self.notes = field(form, "Immediate clinical orders / interventions", row, colspan=2,
                           placeholder="e.g. High flow oxygen, 2 wide bore IV lines, ECG stat")
        self.add_footer("Log ER Admission", self.submit, submit_color=theme.ROSE)

    def submit(self) -> None:
        name = value(self.patient_name)
        if not name:
            self.app.toast("Please enter the patient name or triage tag.", error=True)
            return
        if not value(self.complaint):
            self.app.toast("Please enter the emergency chief complaint.", error=True)
            return
        data = {
            "patientName": name,
            "age": safe_int(value(self.age), 0),
            "gender": self.gender.get(),
            "triageLevel": self.triage.get(),
            "chiefComplaint": value(self.complaint),
            "vitalsBrief": value(self.vitals),
            "assignedDoctor": self.doctor.get().split(" · ")[0] if self._doctor_names else self.doctor.get(),
            "status": "Waiting",
            "notes": value(self.notes) or "Triage intake logged at ER counter.",
        }
        if self.run_action(self.store.add_emergency_case, data):
            self.close()
