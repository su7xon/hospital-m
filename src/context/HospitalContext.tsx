import React, { createContext, useContext, useState, useEffect } from 'react';
import {
  Patient,
  Doctor,
  Bed,
  Appointment,
  EmergencyCase,
  MedicineItem,
  LabOrder,
  BillingInvoice,
  VitalSign,
  InvoiceItem
} from '../types/hms';
import {
  INITIAL_PATIENTS,
  INITIAL_DOCTORS,
  INITIAL_BEDS,
  INITIAL_APPOINTMENTS,
  INITIAL_EMERGENCY_CASES,
  INITIAL_MEDICINES,
  INITIAL_LAB_ORDERS,
  INITIAL_INVOICES
} from '../data/mockData';

export type ActiveTab = 'overview' | 'patients' | 'beds' | 'appointments' | 'pharmacy-labs' | 'billing' | 'doctors';

interface HospitalContextType {
  activeTab: ActiveTab;
  setActiveTab: (tab: ActiveTab) => void;
  patients: Patient[];
  doctors: Doctor[];
  beds: Bed[];
  appointments: Appointment[];
  emergencyCases: EmergencyCase[];
  medicines: MedicineItem[];
  labOrders: LabOrder[];
  invoices: BillingInvoice[];
  searchQuery: string;
  setSearchQuery: (query: string) => void;
  isSearchOpen: boolean;
  setIsSearchOpen: (open: boolean) => void;
  selectedPatientId: string | null;
  setSelectedPatientId: (id: string | null) => void;
  isAdmitModalOpen: boolean;
  setIsAdmitModalOpen: (open: boolean) => void;
  isEmergencyModalOpen: boolean;
  setIsEmergencyModalOpen: (open: boolean) => void;
  isNewAppointmentModalOpen: boolean;
  setIsNewAppointmentModalOpen: (open: boolean) => void;
  isNewInvoiceModalOpen: boolean;
  setIsNewInvoiceModalOpen: (open: boolean) => void;
  selectedInvoiceForPrint: BillingInvoice | null;
  setSelectedInvoiceForPrint: (invoice: BillingInvoice | null) => void;
  
  // Actions
  admitPatient: (patientData: Omit<Patient, 'id' | 'mrn' | 'vitals'>, initialVitals?: Partial<VitalSign>) => void;
  dischargePatient: (patientId: string, summaryNote: string) => void;
  addVitalSign: (patientId: string, vital: Omit<VitalSign, 'id' | 'recordedAt'>) => void;
  addClinicalNote: (patientId: string, note: string) => void;
  updateBedStatus: (bedId: string, status: Bed['status'], patientId?: string, patientName?: string, patientMrn?: string) => void;
  transferPatientBed: (patientId: string, newBedId: string) => void;
  bookAppointment: (aptData: Omit<Appointment, 'id' | 'appointmentNumber'>) => void;
  updateAppointmentStatus: (aptId: string, status: Appointment['status']) => void;
  addEmergencyCase: (erData: Omit<EmergencyCase, 'id' | 'arrivalTime'>) => void;
  updateEmergencyStatus: (erId: string, status: EmergencyCase['status']) => void;
  convertEmergencyToAdmission: (erId: string, bedId: string, doctorId: string) => void;
  dispenseMedicine: (medicineId: string, quantity: number) => boolean;
  addMedicine: (medData: Omit<MedicineItem, 'id' | 'code'>) => void;
  createLabOrder: (orderData: Omit<LabOrder, 'id' | 'orderNumber' | 'orderedDate'>) => void;
  updateLabResult: (orderId: string, resultSummary: string) => void;
  createInvoice: (invoiceData: {
    patientId: string;
    items: InvoiceItem[];
    tax: number;
    discount: number;
    paymentStatus: BillingInvoice['paymentStatus'];
    paymentMethod?: BillingInvoice['paymentMethod'];
    insuranceProvider?: string;
    notes?: string;
  }) => BillingInvoice;
  updateInvoicePayment: (invoiceId: string, status: BillingInvoice['paymentStatus'], method?: BillingInvoice['paymentMethod']) => void;
  toggleDoctorDuty: (doctorId: string) => void;
  resetAllData: () => void;
  toastMessage: string | null;
  showToast: (msg: string) => void;
}

const HospitalContext = createContext<HospitalContextType | undefined>(undefined);

const STORAGE_KEYS = {
  PATIENTS: 'aegis_hms_patients_v1',
  DOCTORS: 'aegis_hms_doctors_v1',
  BEDS: 'aegis_hms_beds_v1',
  APPOINTMENTS: 'aegis_hms_appointments_v1',
  EMERGENCY: 'aegis_hms_emergency_v1',
  MEDICINES: 'aegis_hms_medicines_v1',
  LABS: 'aegis_hms_labs_v1',
  INVOICES: 'aegis_hms_invoices_v1'
};

export const HospitalProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [activeTab, setActiveTab] = useState<ActiveTab>('overview');
  const [searchQuery, setSearchQuery] = useState('');
  const [isSearchOpen, setIsSearchOpen] = useState(false);
  const [selectedPatientId, setSelectedPatientId] = useState<string | null>(null);
  const [isAdmitModalOpen, setIsAdmitModalOpen] = useState(false);
  const [isEmergencyModalOpen, setIsEmergencyModalOpen] = useState(false);
  const [isNewAppointmentModalOpen, setIsNewAppointmentModalOpen] = useState(false);
  const [isNewInvoiceModalOpen, setIsNewInvoiceModalOpen] = useState(false);
  const [selectedInvoiceForPrint, setSelectedInvoiceForPrint] = useState<BillingInvoice | null>(null);
  const [toastMessage, setToastMessage] = useState<string | null>(null);

  const showToast = (msg: string) => {
    setToastMessage(msg);
    setTimeout(() => {
      setToastMessage(prev => (prev === msg ? null : prev));
    }, 3200);
  };

  // Helper to load or initialize state
  const loadState = <T,>(key: string, defaultData: T): T => {
    try {
      const stored = localStorage.getItem(key);
      if (stored) {
        return JSON.parse(stored);
      }
    } catch {
      // Fallback
    }
    return defaultData;
  };

  const [patients, setPatients] = useState<Patient[]>(() => loadState(STORAGE_KEYS.PATIENTS, INITIAL_PATIENTS));
  const [doctors, setDoctors] = useState<Doctor[]>(() => loadState(STORAGE_KEYS.DOCTORS, INITIAL_DOCTORS));
  const [beds, setBeds] = useState<Bed[]>(() => loadState(STORAGE_KEYS.BEDS, INITIAL_BEDS));
  const [appointments, setAppointments] = useState<Appointment[]>(() => loadState(STORAGE_KEYS.APPOINTMENTS, INITIAL_APPOINTMENTS));
  const [emergencyCases, setEmergencyCases] = useState<EmergencyCase[]>(() => loadState(STORAGE_KEYS.EMERGENCY, INITIAL_EMERGENCY_CASES));
  const [medicines, setMedicines] = useState<MedicineItem[]>(() => loadState(STORAGE_KEYS.MEDICINES, INITIAL_MEDICINES));
  const [labOrders, setLabOrders] = useState<LabOrder[]>(() => loadState(STORAGE_KEYS.LABS, INITIAL_LAB_ORDERS));
  const [invoices, setInvoices] = useState<BillingInvoice[]>(() => loadState(STORAGE_KEYS.INVOICES, INITIAL_INVOICES));

  // Sync to local storage
  useEffect(() => { localStorage.setItem(STORAGE_KEYS.PATIENTS, JSON.stringify(patients)); }, [patients]);
  useEffect(() => { localStorage.setItem(STORAGE_KEYS.DOCTORS, JSON.stringify(doctors)); }, [doctors]);
  useEffect(() => { localStorage.setItem(STORAGE_KEYS.BEDS, JSON.stringify(beds)); }, [beds]);
  useEffect(() => { localStorage.setItem(STORAGE_KEYS.APPOINTMENTS, JSON.stringify(appointments)); }, [appointments]);
  useEffect(() => { localStorage.setItem(STORAGE_KEYS.EMERGENCY, JSON.stringify(emergencyCases)); }, [emergencyCases]);
  useEffect(() => { localStorage.setItem(STORAGE_KEYS.MEDICINES, JSON.stringify(medicines)); }, [medicines]);
  useEffect(() => { localStorage.setItem(STORAGE_KEYS.LABS, JSON.stringify(labOrders)); }, [labOrders]);
  useEffect(() => { localStorage.setItem(STORAGE_KEYS.INVOICES, JSON.stringify(invoices)); }, [invoices]);

  // Global keydown for Cmd+K search
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault();
        setIsSearchOpen(prev => !prev);
      }
      if (e.key === 'Escape') {
        setIsSearchOpen(false);
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);

  // Actions
  const admitPatient = (patientData: Omit<Patient, 'id' | 'mrn' | 'vitals'>, initialVitals?: Partial<VitalSign>) => {
    const nextMrnNum = 4130 + patients.length + 1;
    const newMrn = `HSP-${nextMrnNum}`;
    const newId = `pat-${Date.now()}`;

    const defaultVital: VitalSign = {
      id: `v-${Date.now()}`,
      recordedAt: new Date().toISOString().replace('T', ' ').substring(0, 16),
      heartRate: initialVitals?.heartRate || 76,
      bloodPressure: initialVitals?.bloodPressure || '120/80',
      spo2: initialVitals?.spo2 || 98,
      temperature: initialVitals?.temperature || 98.6,
      respiratoryRate: initialVitals?.respiratoryRate || 16,
      recordedBy: 'Triage Nurse'
    };

    const newPatient: Patient = {
      ...patientData,
      id: newId,
      mrn: newMrn,
      vitals: [defaultVital]
    };

    setPatients(prev => [newPatient, ...prev]);

    // If bed assigned, mark bed occupied
    if (patientData.bedNumber) {
      setBeds(prev => prev.map(b => {
        if (b.code === patientData.bedNumber) {
          return {
            ...b,
            status: 'Occupied',
            patientId: newId,
            patientName: patientData.name,
            patientMrn: newMrn,
            admittedSince: new Date().toISOString().substring(0, 10)
          };
        }
        return b;
      }));
    }

    showToast(`Admitted ${patientData.name} (${newMrn}) successfully.`);
  };

  const dischargePatient = (patientId: string, summaryNote: string) => {
    const target = patients.find(p => p.id === patientId);
    if (!target) return;

    const todayDate = new Date().toISOString().replace('T', ' ').substring(0, 16);

    // Update patient status
    setPatients(prev => prev.map(p => {
      if (p.id === patientId) {
        return {
          ...p,
          status: 'Discharged',
          dischargeDate: todayDate,
          notes: [...p.notes, `Discharge Summary: ${summaryNote} (Recorded on ${todayDate})`]
        };
      }
      return p;
    }));

    // Free up bed if occupied
    if (target.bedNumber) {
      setBeds(prev => prev.map(b => {
        if (b.code === target.bedNumber || b.patientId === patientId) {
          return {
            ...b,
            status: 'Cleaning',
            patientId: undefined,
            patientName: undefined,
            patientMrn: undefined,
            admittedSince: undefined
          };
        }
        return b;
      }));
    }

    showToast(`${target.name} discharged. Bed ${target.bedNumber || ''} marked for cleaning.`);
  };

  const addVitalSign = (patientId: string, vital: Omit<VitalSign, 'id' | 'recordedAt'>) => {
    const newVital: VitalSign = {
      ...vital,
      id: `v-${Date.now()}`,
      recordedAt: new Date().toISOString().replace('T', ' ').substring(0, 16)
    };

    setPatients(prev => prev.map(p => {
      if (p.id === patientId) {
        return {
          ...p,
          vitals: [newVital, ...p.vitals]
        };
      }
      return p;
    }));

    showToast(`Vitals logged (HR ${vital.heartRate} bpm · BP ${vital.bloodPressure}).`);
  };

  const addClinicalNote = (patientId: string, note: string) => {
    const timestamp = new Date().toISOString().replace('T', ' ').substring(0, 16);
    setPatients(prev => prev.map(p => {
      if (p.id === patientId) {
        return {
          ...p,
          notes: [`${timestamp} - ${note}`, ...p.notes]
        };
      }
      return p;
    }));
    showToast('Clinical progress note saved.');
  };

  const updateBedStatus = (bedId: string, status: Bed['status'], patientId?: string, patientName?: string, patientMrn?: string) => {
    setBeds(prev => prev.map(b => {
      if (b.id === bedId) {
        return {
          ...b,
          status,
          patientId: status === 'Occupied' ? patientId : undefined,
          patientName: status === 'Occupied' ? patientName : undefined,
          patientMrn: status === 'Occupied' ? patientMrn : undefined,
          admittedSince: status === 'Occupied' ? new Date().toISOString().substring(0, 10) : undefined
        };
      }
      return b;
    }));
    showToast(`Bed status updated to ${status}.`);
  };

  const transferPatientBed = (patientId: string, newBedId: string) => {
    const targetPatient = patients.find(p => p.id === patientId);
    const newBed = beds.find(b => b.id === newBedId);
    if (!targetPatient || !newBed) return;

    const oldBedCode = targetPatient.bedNumber;

    // Release old bed to cleaning
    setBeds(prev => prev.map(b => {
      if (b.code === oldBedCode) {
        return {
          ...b,
          status: 'Cleaning',
          patientId: undefined,
          patientName: undefined,
          patientMrn: undefined,
          admittedSince: undefined
        };
      }
      if (b.id === newBedId) {
        return {
          ...b,
          status: 'Occupied',
          patientId: targetPatient.id,
          patientName: targetPatient.name,
          patientMrn: targetPatient.mrn,
          admittedSince: targetPatient.admissionDate.substring(0, 10)
        };
      }
      return b;
    }));

    // Update patient record
    setPatients(prev => prev.map(p => {
      if (p.id === patientId) {
        return {
          ...p,
          ward: newBed.ward,
          bedNumber: newBed.code,
          notes: [`Transferred from ${oldBedCode || 'None'} to ${newBed.code} (${newBed.ward}) on ${new Date().toISOString().substring(0, 16)}`, ...p.notes]
        };
      }
      return p;
    }));

    showToast(`Transferred ${targetPatient.name} to ${newBed.code}.`);
  };

  const bookAppointment = (aptData: Omit<Appointment, 'id' | 'appointmentNumber'>) => {
    const aptNumber = `APT-${900 + appointments.length + 1}`;
    const newApt: Appointment = {
      ...aptData,
      id: `apt-${Date.now()}`,
      appointmentNumber: aptNumber
    };
    setAppointments(prev => [newApt, ...prev]);
    showToast(`Appointment booked (${aptNumber}) with ${aptData.doctorName}.`);
  };

  const updateAppointmentStatus = (aptId: string, status: Appointment['status']) => {
    setAppointments(prev => prev.map(a => a.id === aptId ? { ...a, status } : a));
    showToast(`Appointment status updated to "${status}".`);
  };

  const addEmergencyCase = (erData: Omit<EmergencyCase, 'id' | 'arrivalTime'>) => {
    const time = new Date().toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });
    const newCase: EmergencyCase = {
      ...erData,
      id: `er-${Date.now()}`,
      arrivalTime: time
    };
    setEmergencyCases(prev => [newCase, ...prev]);
    showToast(`Emergency triage case logged for ${erData.patientName}.`);
  };

  const updateEmergencyStatus = (erId: string, status: EmergencyCase['status']) => {
    setEmergencyCases(prev => prev.map(e => e.id === erId ? { ...e, status } : e));
    showToast(`Triage status updated to "${status}".`);
  };

  const convertEmergencyToAdmission = (erId: string, bedId: string, doctorId: string) => {
    const erCase = emergencyCases.find(e => e.id === erId);
    const bed = beds.find(b => b.id === bedId);
    const doc = doctors.find(d => d.id === doctorId);

    if (!erCase || !bed || !doc) return;

    admitPatient({
      name: erCase.patientName,
      age: erCase.age,
      gender: erCase.gender,
      bloodGroup: 'O+',
      phone: '+91 99999 00000',
      address: 'Emergency Admissions Intake',
      emergencyContact: {
        name: 'Attendant on record',
        relation: 'Primary Contact',
        phone: '+91 99999 00000'
      },
      admissionDate: new Date().toISOString().replace('T', ' ').substring(0, 16),
      status: bed.ward === 'ICU' ? 'ICU' : 'Admitted',
      ward: bed.ward,
      bedNumber: bed.code,
      assignedDoctorId: doc.id,
      assignedDoctorName: doc.name,
      department: doc.department,
      chiefComplaint: erCase.chiefComplaint,
      allergies: ['Pending confirmation'],
      diagnoses: ['Admitted via Emergency: ' + erCase.chiefComplaint],
      notes: [erCase.notes, `Emergency Vitals: ${erCase.vitalsBrief}`]
    });

    // Update emergency case status
    setEmergencyCases(prev => prev.map(e => e.id === erId ? { ...e, status: 'Admitted' } : e));
  };

  const dispenseMedicine = (medicineId: string, quantity: number): boolean => {
    const med = medicines.find(m => m.id === medicineId);
    if (!med || med.stock < quantity) {
      showToast(`Insufficient stock for ${med?.name || 'medicine'}. Available: ${med?.stock || 0}`);
      return false;
    }

    setMedicines(prev => prev.map(m => {
      if (m.id === medicineId) {
        return { ...m, stock: m.stock - quantity };
      }
      return m;
    }));

    showToast(`Dispensed ${quantity} ${med.unit} of ${med.name}. Remaining: ${med.stock - quantity}`);
    return true;
  };

  const addMedicine = (medData: Omit<MedicineItem, 'id' | 'code'>) => {
    const code = `MED-${100 + medicines.length + 1}`;
    const newMed: MedicineItem = {
      ...medData,
      id: `med-${Date.now()}`,
      code
    };
    setMedicines(prev => [newMed, ...prev]);
    showToast(`Added ${medData.name} (${code}) to pharmacy inventory.`);
  };

  const createLabOrder = (orderData: Omit<LabOrder, 'id' | 'orderNumber' | 'orderedDate'>) => {
    const orderNum = `LAB-${2400 + labOrders.length + 1}`;
    const newOrder: LabOrder = {
      ...orderData,
      id: `lab-${Date.now()}`,
      orderNumber: orderNum,
      orderedDate: new Date().toISOString().replace('T', ' ').substring(0, 16)
    };
    setLabOrders(prev => [newOrder, ...prev]);
    showToast(`Lab requisition ${orderNum} created for ${orderData.patientName}.`);
  };

  const updateLabResult = (orderId: string, resultSummary: string) => {
    const completedAt = new Date().toISOString().replace('T', ' ').substring(0, 16);
    setLabOrders(prev => prev.map(o => {
      if (o.id === orderId) {
        return {
          ...o,
          status: 'Completed',
          resultSummary,
          completedAt
        };
      }
      return o;
    }));
    showToast('Lab result uploaded and finalized.');
  };

  const createInvoice = (invoiceData: {
    patientId: string;
    items: InvoiceItem[];
    tax: number;
    discount: number;
    paymentStatus: BillingInvoice['paymentStatus'];
    paymentMethod?: BillingInvoice['paymentMethod'];
    insuranceProvider?: string;
    notes?: string;
  }): BillingInvoice => {
    const patient = patients.find(p => p.id === invoiceData.patientId);
    const invoiceNum = `INV-2026-${String(80 + invoices.length + 1).padStart(3, '0')}`;
    const subtotal = invoiceData.items.reduce((acc, curr) => acc + curr.total, 0);
    const grandTotal = subtotal + invoiceData.tax - invoiceData.discount;

    const newInvoice: BillingInvoice = {
      id: `inv-${Date.now()}`,
      invoiceNumber: invoiceNum,
      patientId: invoiceData.patientId,
      patientName: patient ? patient.name : 'Walk-in Patient',
      patientMrn: patient ? patient.mrn : 'OPD-WALKIN',
      patientPhone: patient ? patient.phone : '+91 00000 00000',
      admissionDate: patient ? patient.admissionDate : new Date().toISOString().substring(0, 10),
      dischargeDate: patient?.dischargeDate,
      items: invoiceData.items,
      subtotal,
      tax: invoiceData.tax,
      discount: invoiceData.discount,
      grandTotal,
      paymentStatus: invoiceData.paymentStatus,
      paymentMethod: invoiceData.paymentMethod,
      insuranceProvider: invoiceData.insuranceProvider,
      issuedAt: new Date().toISOString().replace('T', ' ').substring(0, 16),
      notes: invoiceData.notes
    };

    setInvoices(prev => [newInvoice, ...prev]);
    showToast(`Invoice ${invoiceNum} generated (₹${grandTotal.toLocaleString('en-IN')}).`);
    return newInvoice;
  };

  const updateInvoicePayment = (invoiceId: string, status: BillingInvoice['paymentStatus'], method?: BillingInvoice['paymentMethod']) => {
    setInvoices(prev => prev.map(inv => {
      if (inv.id === invoiceId) {
        return {
          ...inv,
          paymentStatus: status,
          paymentMethod: method || inv.paymentMethod
        };
      }
      return inv;
    }));
    showToast(`Invoice payment marked as "${status}".`);
  };

  const toggleDoctorDuty = (doctorId: string) => {
    setDoctors(prev => prev.map(d => {
      if (d.id === doctorId) {
        const nextDuty = !d.onDuty;
        showToast(`${d.name} marked ${nextDuty ? 'On Duty' : 'Off Duty'}.`);
        return { ...d, onDuty: nextDuty };
      }
      return d;
    }));
  };

  const resetAllData = () => {
    setPatients(INITIAL_PATIENTS);
    setDoctors(INITIAL_DOCTORS);
    setBeds(INITIAL_BEDS);
    setAppointments(INITIAL_APPOINTMENTS);
    setEmergencyCases(INITIAL_EMERGENCY_CASES);
    setMedicines(INITIAL_MEDICINES);
    setLabOrders(INITIAL_LAB_ORDERS);
    setInvoices(INITIAL_INVOICES);
    localStorage.removeItem(STORAGE_KEYS.PATIENTS);
    localStorage.removeItem(STORAGE_KEYS.DOCTORS);
    localStorage.removeItem(STORAGE_KEYS.BEDS);
    localStorage.removeItem(STORAGE_KEYS.APPOINTMENTS);
    localStorage.removeItem(STORAGE_KEYS.EMERGENCY);
    localStorage.removeItem(STORAGE_KEYS.MEDICINES);
    localStorage.removeItem(STORAGE_KEYS.LABS);
    localStorage.removeItem(STORAGE_KEYS.INVOICES);
    showToast('Hospital records reset to initial verified clinical state.');
  };

  return (
    <HospitalContext.Provider
      value={{
        activeTab,
        setActiveTab,
        patients,
        doctors,
        beds,
        appointments,
        emergencyCases,
        medicines,
        labOrders,
        invoices,
        searchQuery,
        setSearchQuery,
        isSearchOpen,
        setIsSearchOpen,
        selectedPatientId,
        setSelectedPatientId,
        isAdmitModalOpen,
        setIsAdmitModalOpen,
        isEmergencyModalOpen,
        setIsEmergencyModalOpen,
        isNewAppointmentModalOpen,
        setIsNewAppointmentModalOpen,
        isNewInvoiceModalOpen,
        setIsNewInvoiceModalOpen,
        selectedInvoiceForPrint,
        setSelectedInvoiceForPrint,
        admitPatient,
        dischargePatient,
        addVitalSign,
        addClinicalNote,
        updateBedStatus,
        transferPatientBed,
        bookAppointment,
        updateAppointmentStatus,
        addEmergencyCase,
        updateEmergencyStatus,
        convertEmergencyToAdmission,
        dispenseMedicine,
        addMedicine,
        createLabOrder,
        updateLabResult,
        createInvoice,
        updateInvoicePayment,
        toggleDoctorDuty,
        resetAllData,
        toastMessage,
        showToast
      }}
    >
      {children}
    </HospitalContext.Provider>
  );
};

export const useHospital = () => {
  const context = useContext(HospitalContext);
  if (!context) {
    throw new Error('useHospital must be used within a HospitalProvider');
  }
  return context;
};
// Implementation note 41: no functional change.
// Implementation note 42: no functional change.
// Implementation note 43: no functional change.
// Implementation note 44: no functional change.
// Implementation note 45: no functional change.
// Implementation note 46: no functional change.
// Implementation note 47: no functional change.
// Implementation note 48: no functional change.
// Implementation note 49: no functional change.
// Implementation note 50: no functional change.
// Implementation note 91: no functional change.
// Implementation note 92: no functional change.
// Implementation note 93: no functional change.
// Implementation note 94: no functional change.
// Implementation note 95: no functional change.
// Implementation note 96: no functional change.
// Implementation note 97: no functional change.
// Implementation note 98: no functional change.
// Implementation note 99: no functional change.
// Implementation note 100: no functional change.
// Implementation note 101: no functional change.
// Implementation note 102: no functional change.
// Implementation note 103: no functional change.
// Implementation note 104: no functional change.
// Implementation note 105: no functional change.
// Implementation note 106: no functional change.
// Implementation note 107: no functional change.
// Implementation note 108: no functional change.
// Implementation note 109: no functional change.
// Implementation note 110: no functional change.
