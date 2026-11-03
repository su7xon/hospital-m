export type PatientStatus = 'Admitted' | 'Discharged' | 'Outpatient' | 'Emergency' | 'ICU';

export interface VitalSign {
  id: string;
  recordedAt: string;
  heartRate: number; // bpm
  bloodPressure: string; // e.g. 120/80
  spo2: number; // percentage %
  temperature: number; // °F or °C
  respiratoryRate: number; // breaths/min
  recordedBy: string;
}

export interface Patient {
  id: string;
  mrn: string; // Medical Record Number e.g. HSP-4091
  name: string;
  age: number;
  gender: 'Male' | 'Female' | 'Other';
  bloodGroup: 'A+' | 'A-' | 'B+' | 'B-' | 'AB+' | 'AB-' | 'O+' | 'O-';
  phone: string;
  email?: string;
  address: string;
  emergencyContact: {
    name: string;
    relation: string;
    phone: string;
  };
  admissionDate: string;
  dischargeDate?: string;
  status: PatientStatus;
  ward?: string;
  bedNumber?: string;
  assignedDoctorId: string;
  assignedDoctorName: string;
  department: string;
  chiefComplaint: string;
  allergies: string[];
  diagnoses: string[];
  notes: string[];
  vitals: VitalSign[];
}

export interface Doctor {
  id: string;
  name: string;
  qualification: string;
  specialty: string;
  department: string;
  room: string;
  phone: string;
  email: string;
  onDuty: boolean;
  activePatients: number;
  scheduleHours: string;
}

export type BedStatus = 'Available' | 'Occupied' | 'Cleaning' | 'Maintenance';
export type WardType = 'ICU' | 'General Ward A' | 'General Ward B' | 'Private Suite' | 'Emergency Care';

export interface Bed {
  id: string;
  code: string; // e.g. ICU-01, GWA-12
  ward: WardType;
  floor: string;
  dailyRate: number;
  status: BedStatus;
  patientId?: string;
  patientName?: string;
  patientMrn?: string;
  admittedSince?: string;
}

export type AppointmentStatus = 'Scheduled' | 'Checked-in' | 'In Consultation' | 'Completed' | 'Cancelled';

export interface Appointment {
  id: string;
  appointmentNumber: string;
  patientName: string;
  patientPhone: string;
  patientMrn?: string;
  doctorId: string;
  doctorName: string;
  department: string;
  date: string;
  timeSlot: string;
  status: AppointmentStatus;
  reason: string;
  type: 'OPD' | 'Follow-up' | 'Review';
}

export type TriageLevel = 'P1 - Resuscitation' | 'P2 - Emergency' | 'P3 - Urgent' | 'P4 - Semi-Urgent' | 'P5 - Non-Urgent';

export interface EmergencyCase {
  id: string;
  patientName: string;
  age: number;
  gender: 'Male' | 'Female' | 'Other';
  triageLevel: TriageLevel;
  chiefComplaint: string;
  arrivalTime: string;
  assignedDoctor: string;
  vitalsBrief: string;
  status: 'Waiting' | 'In Treatment' | 'Admitted' | 'Discharged';
  notes: string;
}

export interface MedicineItem {
  id: string;
  code: string;
  name: string;
  genericName: string;
  category: 'Antibiotics' | 'Analgesics' | 'Cardiovascular' | 'Respiratory' | 'IV Fluids' | 'Emergency' | 'Vitamins';
  dosageForm: 'Tablet' | 'Capsule' | 'Syrup' | 'Injection' | 'IV Infusion' | 'Ointment';
  stock: number;
  unit: string;
  minStock: number;
  unitPrice: number;
  batchNumber: string;
  expiryDate: string;
}

export interface LabOrder {
  id: string;
  orderNumber: string;
  patientName: string;
  patientMrn: string;
  testName: string;
  department: 'Biochemistry' | 'Hematology' | 'Radiology' | 'Microbiology' | 'Pathology';
  orderedBy: string;
  orderedDate: string;
  status: 'Pending' | 'In Progress' | 'Completed';
  priority: 'Routine' | 'STAT Urgent';
  resultSummary?: string;
  completedAt?: string;
}

export interface InvoiceItem {
  id: string;
  description: string;
  category: 'Room / Bed' | 'Consultation' | 'Medication' | 'Lab Test' | 'Nursing' | 'Procedure';
  quantity: number;
  unitPrice: number;
  total: number;
}

export interface BillingInvoice {
  id: string;
  invoiceNumber: string;
  patientId: string;
  patientName: string;
  patientMrn: string;
  patientPhone: string;
  admissionDate: string;
  dischargeDate?: string;
  items: InvoiceItem[];
  subtotal: number;
  tax: number;
  discount: number;
  grandTotal: number;
  paymentStatus: 'Paid' | 'Pending' | 'Partially Paid';
  paymentMethod?: 'Card' | 'Cash' | 'Insurance / TPA' | 'UPI / Bank Transfer';
  insuranceProvider?: string;
  issuedAt: string;
  notes?: string;
}
