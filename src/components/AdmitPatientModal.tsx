import React, { useState } from 'react';
import { useHospital } from '../context/HospitalContext';
import { Patient } from '../types/hms';
import { X, UserPlus, HeartPulse, BedDouble, Stethoscope } from 'lucide-react';

export const AdmitPatientModal: React.FC = () => {
  const {
    isAdmitModalOpen,
    setIsAdmitModalOpen,
    admitPatient,
    doctors,
    beds,
    showToast
  } = useHospital();

  const [name, setName] = useState('');
  const [age, setAge] = useState(45);
  const [gender, setGender] = useState<'Male' | 'Female' | 'Other'>('Male');
  const [bloodGroup, setBloodGroup] = useState<Patient['bloodGroup']>('B+');
  const [phone, setPhone] = useState('+91 ');
  const [address, setAddress] = useState('');
  const [kinName, setKinName] = useState('');
  const [kinRelation, setKinRelation] = useState('Spouse');
  const [kinPhone, setKinPhone] = useState('');

  const [doctorId, setDoctorId] = useState(doctors[0]?.id || '');
  const [bedCode, setBedCode] = useState('');
  const [chiefComplaint, setChiefComplaint] = useState('');
  const [allergiesInput, setAllergiesInput] = useState('No known drug allergies (NKDA)');
  const [diagnosisInput, setDiagnosisInput] = useState('');

  // Initial vitals
  const [initialHR, setInitialHR] = useState(76);
  const [initialBP, setInitialBP] = useState('120/80');
  const [initialSpO2, setInitialSpO2] = useState(98);
  const [initialTemp, setInitialTemp] = useState(98.6);
  const [initialRR, setInitialRR] = useState(16);

  if (!isAdmitModalOpen) return null;

  const availableBeds = beds.filter(b => b.status === 'Available');
  const selectedDoctor = doctors.find(d => d.id === doctorId);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim()) {
      showToast('Please enter patient name.');
      return;
    }

    const assignedBed = beds.find(b => b.code === bedCode);

    const now = new Date().toISOString().replace('T', ' ').substring(0, 16);

    const allergies = allergiesInput
      .split(',')
      .map(a => a.trim())
      .filter(Boolean);

    const diagnoses = diagnosisInput.trim()
      ? [diagnosisInput.trim()]
      : ['Pending clinical evaluation'];

    admitPatient(
      {
        name: name.trim(),
        age: Number(age),
        gender,
        bloodGroup,
        phone: phone.trim(),
        address: address.trim() || 'Not specified',
        emergencyContact: {
          name: kinName.trim() || 'Next of kin',
          relation: kinRelation,
          phone: kinPhone.trim() || phone.trim()
        },
        admissionDate: now,
        status: assignedBed?.ward === 'ICU' ? 'ICU' : 'Admitted',
        ward: assignedBed?.ward || 'General Ward A',
        bedNumber: assignedBed?.code || undefined,
        assignedDoctorId: doctorId,
        assignedDoctorName: selectedDoctor?.name || 'Dr. On Duty',
        department: selectedDoctor?.department || 'Internal Medicine',
        chiefComplaint: chiefComplaint.trim() || 'General admission intake',
        allergies: allergies.length > 0 ? allergies : ['No known drug allergies (NKDA)'],
        diagnoses,
        notes: [`Admitted on ${now} by Clinical Intake Desk.`]
      },
      {
        heartRate: Number(initialHR),
        bloodPressure: initialBP,
        spo2: Number(initialSpO2),
        temperature: Number(initialTemp),
        respiratoryRate: Number(initialRR),
        recordedBy: 'Intake Triage Nurse'
      }
    );

    setIsAdmitModalOpen(false);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-3 sm:p-6 bg-slate-900/50 backdrop-blur-xs">
      <div className="bg-white rounded-xl border border-slate-200 shadow-xl w-full max-w-3xl max-h-[92vh] flex flex-col overflow-hidden animate-in fade-in zoom-in-95 duration-150">
        
        {/* Modal Header */}
        <div className="px-6 py-4 border-b border-slate-200 bg-slate-50/80 flex items-center justify-between">
          <div>
            <h2 className="text-base font-bold text-slate-900">
              Inpatient Admission Intake Form
            </h2>
            <p className="text-xs text-slate-500 mt-0.5">
              Electronic registration, ward bed allocation, and baseline triage vitals.
            </p>
          </div>
          <button
            onClick={() => setIsAdmitModalOpen(false)}
            className="p-1 text-slate-400 hover:text-slate-600 rounded transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Modal Body */}
        <form onSubmit={handleSubmit} className="flex-1 overflow-y-auto p-6 space-y-6 text-xs">
          
          {/* Section 1: Demographics */}
          <div>
            <h3 className="text-xs font-bold text-slate-900 uppercase tracking-wider mb-3">
              1. Patient Demographics & Identification
            </h3>
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
              <div className="sm:col-span-2">
                <label className="font-semibold text-slate-700 block mb-1">Full Legal Name *</label>
                <input
                  type="text"
                  placeholder="e.g. Rahul Sharma"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  required
                  className="w-full px-3 py-1.5 bg-slate-50 border border-slate-200 rounded focus:bg-white"
                />
              </div>

              <div>
                <label className="font-semibold text-slate-700 block mb-1">Age *</label>
                <input
                  type="number"
                  min="0"
                  max="125"
                  value={age}
                  onChange={(e) => setAge(Number(e.target.value))}
                  required
                  className="w-full px-3 py-1.5 bg-slate-50 border border-slate-200 rounded font-mono"
                />
              </div>

              <div>
                <label className="font-semibold text-slate-700 block mb-1">Biological Gender</label>
                <select
                  value={gender}
                  onChange={(e) => setGender(e.target.value as any)}
                  className="w-full px-3 py-1.5 bg-slate-50 border border-slate-200 rounded"
                >
                  <option value="Male">Male</option>
                  <option value="Female">Female</option>
                  <option value="Other">Other</option>
                </select>
              </div>

              <div>
                <label className="font-semibold text-slate-700 block mb-1">Blood Group</label>
                <select
                  value={bloodGroup}
                  onChange={(e) => setBloodGroup(e.target.value as any)}
                  className="w-full px-3 py-1.5 bg-slate-50 border border-slate-200 rounded font-mono"
                >
                  <option value="A+">A+</option>
                  <option value="A-">A-</option>
                  <option value="B+">B+</option>
                  <option value="B-">B-</option>
                  <option value="AB+">AB+</option>
                  <option value="AB-">AB-</option>
                  <option value="O+">O+</option>
                  <option value="O-">O-</option>
                </select>
              </div>

              <div>
                <label className="font-semibold text-slate-700 block mb-1">Contact Phone *</label>
                <input
                  type="text"
                  value={phone}
                  onChange={(e) => setPhone(e.target.value)}
                  required
                  className="w-full px-3 py-1.5 bg-slate-50 border border-slate-200 rounded font-mono"
                />
              </div>

              <div className="sm:col-span-3">
                <label className="font-semibold text-slate-700 block mb-1">Residential Address</label>
                <input
                  type="text"
                  placeholder="Street, locality, city"
                  value={address}
                  onChange={(e) => setAddress(e.target.value)}
                  className="w-full px-3 py-1.5 bg-slate-50 border border-slate-200 rounded"
                />
              </div>
            </div>
          </div>

          {/* Section 2: Emergency Contact */}
          <div className="border-t border-slate-100 pt-4">
            <h3 className="text-xs font-bold text-slate-900 uppercase tracking-wider mb-3">
              2. Emergency Contact / Guardian
            </h3>
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
              <div>
                <label className="font-semibold text-slate-700 block mb-1">Contact Name</label>
                <input
                  type="text"
                  placeholder="e.g. Sunita Sharma"
                  value={kinName}
                  onChange={(e) => setKinName(e.target.value)}
                  className="w-full px-3 py-1.5 bg-slate-50 border border-slate-200 rounded"
                />
              </div>

              <div>
                <label className="font-semibold text-slate-700 block mb-1">Relationship</label>
                <input
                  type="text"
                  placeholder="e.g. Spouse / Parent / Sibling"
                  value={kinRelation}
                  onChange={(e) => setKinRelation(e.target.value)}
                  className="w-full px-3 py-1.5 bg-slate-50 border border-slate-200 rounded"
                />
              </div>

              <div>
                <label className="font-semibold text-slate-700 block mb-1">Emergency Phone</label>
                <input
                  type="text"
                  placeholder="+91..."
                  value={kinPhone}
                  onChange={(e) => setKinPhone(e.target.value)}
                  className="w-full px-3 py-1.5 bg-slate-50 border border-slate-200 rounded font-mono"
                />
              </div>
            </div>
          </div>

          {/* Section 3: Clinical Intake & Bed Allocation */}
          <div className="border-t border-slate-100 pt-4">
            <h3 className="text-xs font-bold text-slate-900 uppercase tracking-wider mb-3">
              3. Clinical Assignment & Ward Allocation
            </h3>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <div>
                <label className="font-semibold text-slate-700 block mb-1">Attending Physician *</label>
                <select
                  value={doctorId}
                  onChange={(e) => setDoctorId(e.target.value)}
                  required
                  className="w-full px-3 py-1.5 bg-slate-50 border border-slate-200 rounded"
                >
                  {doctors.map(d => (
                    <option key={d.id} value={d.id}>
                      {d.name} ({d.department}) {d.onDuty ? '· On Duty' : ''}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="font-semibold text-slate-700 block mb-1">Allocate Inpatient Bed</label>
                <select
                  value={bedCode}
                  onChange={(e) => setBedCode(e.target.value)}
                  className="w-full px-3 py-1.5 bg-slate-50 border border-slate-200 rounded font-medium"
                >
                  <option value="">-- No Bed (OPD / Day Care) --</option>
                  {availableBeds.map(b => (
                    <option key={b.id} value={b.code}>
                      {b.code} - {b.ward} (₹{b.dailyRate.toLocaleString('en-IN')}/day)
                    </option>
                  ))}
                </select>
                {availableBeds.length === 0 && (
                  <span className="text-[11px] text-amber-700 block mt-1">
                    Notice: All ward beds currently full. Patient can be admitted to day care or emergency observation.
                  </span>
                )}
              </div>

              <div className="sm:col-span-2">
                <label className="font-semibold text-slate-700 block mb-1">Chief Presenting Complaint *</label>
                <textarea
                  rows={2}
                  placeholder="e.g. Acute onset retrosternal chest pain with diaphoresis for 2 hours..."
                  value={chiefComplaint}
                  onChange={(e) => setChiefComplaint(e.target.value)}
                  required
                  className="w-full p-2 bg-slate-50 border border-slate-200 rounded"
                />
              </div>

              <div>
                <label className="font-semibold text-slate-700 block mb-1">Provisional Clinical Diagnosis</label>
                <input
                  type="text"
                  placeholder="e.g. Acute Coronary Syndrome"
                  value={diagnosisInput}
                  onChange={(e) => setDiagnosisInput(e.target.value)}
                  className="w-full px-3 py-1.5 bg-slate-50 border border-slate-200 rounded"
                />
              </div>

              <div>
                <label className="font-semibold text-slate-700 block mb-1">Known Drug Allergies</label>
                <input
                  type="text"
                  placeholder="e.g. Penicillin, Sulfa drugs (or NKDA)"
                  value={allergiesInput}
                  onChange={(e) => setAllergiesInput(e.target.value)}
                  className="w-full px-3 py-1.5 bg-slate-50 border border-slate-200 rounded"
                />
              </div>
            </div>
          </div>

          {/* Section 4: Baseline Intake Vitals */}
          <div className="border-t border-slate-100 pt-4">
            <h3 className="text-xs font-bold text-slate-900 uppercase tracking-wider mb-3">
              4. Baseline Intake Vitals
            </h3>
            <div className="grid grid-cols-2 sm:grid-cols-5 gap-3">
              <div>
                <label className="font-semibold text-slate-700 block mb-1">Heart Rate (bpm)</label>
                <input
                  type="number"
                  value={initialHR}
                  onChange={(e) => setInitialHR(Number(e.target.value))}
                  required
                  className="w-full px-2.5 py-1.5 bg-slate-50 border border-slate-200 rounded font-mono"
                />
              </div>

              <div>
                <label className="font-semibold text-slate-700 block mb-1">Blood Pressure</label>
                <input
                  type="text"
                  value={initialBP}
                  onChange={(e) => setInitialBP(e.target.value)}
                  required
                  className="w-full px-2.5 py-1.5 bg-slate-50 border border-slate-200 rounded font-mono"
                />
              </div>

              <div>
                <label className="font-semibold text-slate-700 block mb-1">SpO2 (%)</label>
                <input
                  type="number"
                  value={initialSpO2}
                  onChange={(e) => setInitialSpO2(Number(e.target.value))}
                  required
                  className="w-full px-2.5 py-1.5 bg-slate-50 border border-slate-200 rounded font-mono"
                />
              </div>

              <div>
                <label className="font-semibold text-slate-700 block mb-1">Temp (°F)</label>
                <input
                  type="number"
                  step="0.1"
                  value={initialTemp}
                  onChange={(e) => setInitialTemp(Number(e.target.value))}
                  required
                  className="w-full px-2.5 py-1.5 bg-slate-50 border border-slate-200 rounded font-mono"
                />
              </div>

              <div>
                <label className="font-semibold text-slate-700 block mb-1">Resp. Rate (/min)</label>
                <input
                  type="number"
                  value={initialRR}
                  onChange={(e) => setInitialRR(Number(e.target.value))}
                  required
                  className="w-full px-2.5 py-1.5 bg-slate-50 border border-slate-200 rounded font-mono"
                />
              </div>
            </div>
          </div>

          {/* Modal Actions */}
          <div className="flex items-center justify-end gap-3 pt-4 border-t border-slate-200">
            <button
              type="button"
              onClick={() => setIsAdmitModalOpen(false)}
              className="px-4 py-2 font-semibold text-slate-700 bg-slate-100 hover:bg-slate-200 rounded-md transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="px-5 py-2 font-semibold text-white bg-slate-900 hover:bg-slate-800 rounded-md transition-colors shadow-xs"
            >
              Confirm Admission
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
