import React, { useState } from 'react';
import { useHospital } from '../context/HospitalContext';
import {
  X,
  HeartPulse,
  Activity,
  AlertTriangle,
  FileText,
  User,
  BedDouble,
  DollarSign,
  Plus,
  Send,
  ArrowRightLeft,
  CheckCircle2,
  Calendar
} from 'lucide-react';

export const PatientDetailModal: React.FC = () => {
  const {
    selectedPatientId,
    setSelectedPatientId,
    patients,
    beds,
    labOrders,
    addVitalSign,
    addClinicalNote,
    dischargePatient,
    transferPatientBed,
    setIsNewInvoiceModalOpen,
    showToast
  } = useHospital();

  const patient = patients.find(p => p.id === selectedPatientId);

  // States for sub-forms
  const [activeTab, setActiveTab] = useState<'chart' | 'vitals' | 'notes' | 'transfer' | 'discharge'>('chart');
  
  // New Vitals state
  const [newHR, setNewHR] = useState(75);
  const [newBP, setNewBP] = useState('120/80');
  const [newSpO2, setNewSpO2] = useState(98);
  const [newTemp, setNewTemp] = useState(98.6);
  const [newRR, setNewRR] = useState(16);
  const [recorder, setRecorder] = useState('Staff Nurse');

  // New Note state
  const [newNote, setNewNote] = useState('');

  // Transfer bed state
  const [targetBedId, setTargetBedId] = useState('');

  // Discharge state
  const [dischargeSummary, setDischargeSummary] = useState('');

  if (!patient) return null;

  const patientLabs = labOrders.filter(l => l.patientMrn === patient.mrn || l.patientName === patient.name);
  const availableBeds = beds.filter(b => b.status === 'Available');

  const handleSaveVitals = (e: React.FormEvent) => {
    e.preventDefault();
    addVitalSign(patient.id, {
      heartRate: Number(newHR),
      bloodPressure: newBP,
      spo2: Number(newSpO2),
      temperature: Number(newTemp),
      respiratoryRate: Number(newRR),
      recordedBy: recorder
    });
    setActiveTab('chart');
  };

  const handleSaveNote = (e: React.FormEvent) => {
    e.preventDefault();
    if (!newNote.trim()) return;
    addClinicalNote(patient.id, newNote.trim());
    setNewNote('');
    setActiveTab('chart');
  };

  const handleTransferBed = (e: React.FormEvent) => {
    e.preventDefault();
    if (!targetBedId) return;
    transferPatientBed(patient.id, targetBedId);
    setActiveTab('chart');
  };

  const handleDischarge = (e: React.FormEvent) => {
    e.preventDefault();
    if (!dischargeSummary.trim()) {
      showToast('Please enter a clinical discharge summary.');
      return;
    }
    dischargePatient(patient.id, dischargeSummary.trim());
    setSelectedPatientId(null);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-3 sm:p-6 bg-slate-900/50 backdrop-blur-xs">
      <div className="bg-white rounded-xl border border-slate-200 shadow-xl w-full max-w-4xl max-h-[92vh] flex flex-col overflow-hidden animate-in fade-in zoom-in-95 duration-150">
        
        {/* Header */}
        <div className="px-4 sm:px-6 py-3 sm:py-4 border-b border-slate-200 flex items-start justify-between bg-slate-50/80">
          <div>
            <div className="flex flex-wrap items-center gap-2">
              <h2 className="text-base sm:text-lg font-bold text-slate-900">
                {patient.name}
              </h2>
              <span className="font-mono text-[11px] sm:text-xs font-semibold text-slate-500 bg-white px-2 py-0.5 rounded border border-slate-200">
                {patient.mrn}
              </span>
              <span className={`text-xs font-semibold ${
                patient.status === 'ICU' ? 'text-rose-700' : 'text-slate-700'
              }`}>
                · {patient.status}
              </span>
            </div>

            <div className="flex flex-wrap items-center gap-1.5 sm:gap-2 mt-1 text-[11px] sm:text-xs text-slate-500">
              <span>{patient.age}y</span>
              <span>·</span>
              <span>{patient.gender}</span>
              <span>·</span>
              <span className="font-mono font-medium text-slate-700">Blood: {patient.bloodGroup}</span>
              <span>·</span>
              <span>Admitted: {patient.admissionDate}</span>
              <span>·</span>
              <span className="font-medium text-slate-800">{patient.bedNumber || 'No Bed'} ({patient.ward || 'OPD'})</span>
            </div>
          </div>

          <button
            onClick={() => setSelectedPatientId(null)}
            className="p-1 text-slate-400 hover:text-slate-600 rounded-md transition-colors shrink-0"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Allergy Warning Bar */}
        {patient.allergies.length > 0 && patient.allergies[0] !== 'No known drug allergies (NKDA)' && patient.allergies[0] !== 'No known allergies' && (
          <div className="bg-rose-50 border-b border-rose-200 px-4 sm:px-6 py-2 flex items-center gap-2 text-xs text-rose-800 font-medium">
            <AlertTriangle className="w-4 h-4 text-rose-600 shrink-0" />
            <span>Documented Allergies: <strong className="font-bold">{patient.allergies.join(', ')}</strong></span>
          </div>
        )}

        {/* Sub-navigation Tabs - swipeable on mobile */}
        <div className="flex items-center gap-1 px-3 sm:px-6 border-b border-slate-200 bg-white text-xs overflow-x-auto scrollbar-none touch-pan-x">
          {[
            { id: 'chart', label: 'Clinical Summary' },
            { id: 'vitals', label: 'Log Vitals' },
            { id: 'notes', label: 'Clinical Notes' },
            { id: 'transfer', label: 'Transfer Bed' },
            { id: 'discharge', label: 'Discharge' }
          ].map(t => (
            <button
              key={t.id}
              onClick={() => setActiveTab(t.id as any)}
              className={`py-2.5 sm:py-3 px-2.5 sm:px-3 font-semibold border-b-2 transition-colors whitespace-nowrap shrink-0 ${
                activeTab === t.id
                  ? 'border-slate-900 text-slate-900'
                  : 'border-transparent text-slate-500 hover:text-slate-800'
              }`}
            >
              {t.label}
            </button>
          ))}
        </div>

        {/* Modal Body */}
        <div className="flex-1 overflow-y-auto p-4 sm:p-6 space-y-5 sm:space-y-6">

          {/* TAB 1: CLINICAL SUMMARY */}
          {activeTab === 'chart' && (
            <div className="space-y-6">
              {/* Primary Vitals Card */}
              <div>
                <div className="flex items-center justify-between mb-2">
                  <h3 className="text-xs font-bold text-slate-900 uppercase tracking-wider">
                    Current Vital Signs
                  </h3>
                  <button
                    onClick={() => setActiveTab('vitals')}
                    className="text-xs font-semibold text-slate-700 hover:text-slate-900"
                  >
                    + Record Reading
                  </button>
                </div>

                {patient.vitals.length > 0 ? (
                  <div className="grid grid-cols-2 sm:grid-cols-5 gap-3">
                    <div className="p-3 bg-slate-50 rounded-lg border border-slate-200">
                      <span className="text-[11px] text-slate-500 block">Heart Rate</span>
                      <div className="flex items-baseline gap-1 mt-1">
                        <span className="text-xl font-bold font-mono text-slate-900 tabular-nums">
                          {patient.vitals[0].heartRate}
                        </span>
                        <span className="text-[10px] text-slate-400">bpm</span>
                      </div>
                    </div>

                    <div className="p-3 bg-slate-50 rounded-lg border border-slate-200">
                      <span className="text-[11px] text-slate-500 block">Blood Pressure</span>
                      <div className="flex items-baseline gap-1 mt-1">
                        <span className="text-xl font-bold font-mono text-slate-900 tabular-nums">
                          {patient.vitals[0].bloodPressure}
                        </span>
                        <span className="text-[10px] text-slate-400">mmHg</span>
                      </div>
                    </div>

                    <div className="p-3 bg-slate-50 rounded-lg border border-slate-200">
                      <span className="text-[11px] text-slate-500 block">Oxygen (SpO2)</span>
                      <div className="flex items-baseline gap-1 mt-1">
                        <span className="text-xl font-bold font-mono text-slate-900 tabular-nums">
                          {patient.vitals[0].spo2}%
                        </span>
                        <span className="text-[10px] text-slate-400">room air</span>
                      </div>
                    </div>

                    <div className="p-3 bg-slate-50 rounded-lg border border-slate-200">
                      <span className="text-[11px] text-slate-500 block">Temperature</span>
                      <div className="flex items-baseline gap-1 mt-1">
                        <span className="text-xl font-bold font-mono text-slate-900 tabular-nums">
                          {patient.vitals[0].temperature}°F
                        </span>
                      </div>
                    </div>

                    <div className="p-3 bg-slate-50 rounded-lg border border-slate-200">
                      <span className="text-[11px] text-slate-500 block">Respiratory Rate</span>
                      <div className="flex items-baseline gap-1 mt-1">
                        <span className="text-xl font-bold font-mono text-slate-900 tabular-nums">
                          {patient.vitals[0].respiratoryRate}
                        </span>
                        <span className="text-[10px] text-slate-400">/min</span>
                      </div>
                    </div>
                  </div>
                ) : (
                  <div className="p-4 bg-slate-50 rounded-lg border border-slate-200 text-xs text-slate-500 text-center">
                    No vitals recorded yet.
                  </div>
                )}
                {patient.vitals.length > 0 && (
                  <p className="text-[11px] text-slate-400 mt-1.5 font-mono">
                    Last recorded at {patient.vitals[0].recordedAt} by {patient.vitals[0].recordedBy}
                  </p>
                )}
              </div>

              {/* Complaints & Diagnoses */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="p-4 bg-white rounded-lg border border-slate-200">
                  <h4 className="text-xs font-bold text-slate-900 mb-1.5">
                    Chief Complaint on Admission
                  </h4>
                  <p className="text-xs text-slate-700 leading-relaxed">
                    {patient.chiefComplaint}
                  </p>
                </div>

                <div className="p-4 bg-white rounded-lg border border-slate-200">
                  <h4 className="text-xs font-bold text-slate-900 mb-1.5">
                    Clinical Diagnoses
                  </h4>
                  <ul className="text-xs text-slate-700 space-y-1">
                    {patient.diagnoses.map((d, i) => (
                      <li key={i} className="flex items-center gap-1.5">
                        <span className="w-1.5 h-1.5 rounded-full bg-slate-700 shrink-0" />
                        <span>{d}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              </div>

              {/* Care Team & Emergency Contact */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
                <div className="p-4 bg-slate-50 rounded-lg border border-slate-200">
                  <span className="font-semibold text-slate-900 block mb-1">Attending Physician</span>
                  <p className="text-slate-800 font-medium">{patient.assignedDoctorName}</p>
                  <p className="text-slate-500 mt-0.5">Department of {patient.department}</p>
                </div>

                <div className="p-4 bg-slate-50 rounded-lg border border-slate-200">
                  <span className="font-semibold text-slate-900 block mb-1">Emergency Contact & Next of Kin</span>
                  <p className="text-slate-800 font-medium">{patient.emergencyContact.name} ({patient.emergencyContact.relation})</p>
                  <p className="text-slate-500 mt-0.5 font-mono">{patient.emergencyContact.phone}</p>
                </div>
              </div>

              {/* Patient Lab Orders & Results */}
              <div>
                <h3 className="text-xs font-bold text-slate-900 uppercase tracking-wider mb-2">
                  Laboratory Investigations ({patientLabs.length})
                </h3>
                {patientLabs.length === 0 ? (
                  <p className="text-xs text-slate-400 bg-slate-50 p-3 rounded-lg border border-slate-200">
                    No laboratory requisitions ordered for this patient.
                  </p>
                ) : (
                  <div className="divide-y divide-slate-100 border border-slate-200 rounded-lg overflow-hidden bg-white text-xs">
                    {patientLabs.map(lab => (
                      <div key={lab.id} className="p-3">
                        <div className="flex items-center justify-between">
                          <span className="font-semibold text-slate-900">{lab.testName}</span>
                          <span className="font-mono text-[11px] text-slate-500">{lab.status}</span>
                        </div>
                        {lab.resultSummary ? (
                          <p className="text-xs text-slate-700 font-mono mt-1 bg-slate-50 p-2 rounded">
                            {lab.resultSummary}
                          </p>
                        ) : (
                          <p className="text-[11px] text-slate-400 mt-0.5">Awaiting lab results</p>
                        )}
                      </div>
                    ))}
                  </div>
                )}
              </div>

              {/* Progress Notes */}
              <div>
                <div className="flex items-center justify-between mb-2">
                  <h3 className="text-xs font-bold text-slate-900 uppercase tracking-wider">
                    Recent Clinical Notes
                  </h3>
                  <button
                    onClick={() => setActiveTab('notes')}
                    className="text-xs font-semibold text-slate-700 hover:text-slate-900"
                  >
                    + Add Progress Note
                  </button>
                </div>
                <div className="space-y-2">
                  {patient.notes.map((note, idx) => (
                    <div key={idx} className="p-3 bg-slate-50 rounded-lg border border-slate-200 text-xs text-slate-700">
                      {note}
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* TAB 2: LOG VITALS FORM */}
          {activeTab === 'vitals' && (
            <form onSubmit={handleSaveVitals} className="space-y-4 max-w-lg">
              <h3 className="text-sm font-bold text-slate-900">
                Log New Clinical Vital Signs
              </h3>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="text-xs font-semibold text-slate-700 block mb-1">
                    Heart Rate (BPM)
                  </label>
                  <input
                    type="number"
                    value={newHR}
                    onChange={(e) => setNewHR(Number(e.target.value))}
                    required
                    className="w-full px-3 py-1.5 text-xs bg-slate-50 border border-slate-200 rounded font-mono"
                  />
                </div>

                <div>
                  <label className="text-xs font-semibold text-slate-700 block mb-1">
                    Blood Pressure (mmHg)
                  </label>
                  <input
                    type="text"
                    value={newBP}
                    onChange={(e) => setNewBP(e.target.value)}
                    placeholder="120/80"
                    required
                    className="w-full px-3 py-1.5 text-xs bg-slate-50 border border-slate-200 rounded font-mono"
                  />
                </div>

                <div>
                  <label className="text-xs font-semibold text-slate-700 block mb-1">
                    SpO2 Oxygen Saturation (%)
                  </label>
                  <input
                    type="number"
                    value={newSpO2}
                    onChange={(e) => setNewSpO2(Number(e.target.value))}
                    min="50"
                    max="100"
                    required
                    className="w-full px-3 py-1.5 text-xs bg-slate-50 border border-slate-200 rounded font-mono"
                  />
                </div>

                <div>
                  <label className="text-xs font-semibold text-slate-700 block mb-1">
                    Body Temperature (°F)
                  </label>
                  <input
                    type="number"
                    step="0.1"
                    value={newTemp}
                    onChange={(e) => setNewTemp(Number(e.target.value))}
                    required
                    className="w-full px-3 py-1.5 text-xs bg-slate-50 border border-slate-200 rounded font-mono"
                  />
                </div>

                <div>
                  <label className="text-xs font-semibold text-slate-700 block mb-1">
                    Respiratory Rate (/min)
                  </label>
                  <input
                    type="number"
                    value={newRR}
                    onChange={(e) => setNewRR(Number(e.target.value))}
                    required
                    className="w-full px-3 py-1.5 text-xs bg-slate-50 border border-slate-200 rounded font-mono"
                  />
                </div>

                <div>
                  <label className="text-xs font-semibold text-slate-700 block mb-1">
                    Recorded By (Nurse/Doctor)
                  </label>
                  <input
                    type="text"
                    value={recorder}
                    onChange={(e) => setRecorder(e.target.value)}
                    required
                    className="w-full px-3 py-1.5 text-xs bg-slate-50 border border-slate-200 rounded"
                  />
                </div>
              </div>

              <div className="flex items-center gap-2 pt-3">
                <button
                  type="submit"
                  className="px-4 py-2 text-xs font-semibold text-white bg-slate-900 rounded-md hover:bg-slate-800 transition-colors"
                >
                  Save Vitals Reading
                </button>
                <button
                  type="button"
                  onClick={() => setActiveTab('chart')}
                  className="px-4 py-2 text-xs font-semibold text-slate-700 bg-slate-100 rounded-md hover:bg-slate-200 transition-colors"
                >
                  Cancel
                </button>
              </div>
            </form>
          )}

          {/* TAB 3: NOTES FORM */}
          {activeTab === 'notes' && (
            <form onSubmit={handleSaveNote} className="space-y-4 max-w-lg">
              <h3 className="text-sm font-bold text-slate-900">
                Add Doctor / Nursing Progress Note
              </h3>
              <div>
                <label className="text-xs font-semibold text-slate-700 block mb-1">
                  Clinical Observation & Orders
                </label>
                <textarea
                  value={newNote}
                  onChange={(e) => setNewNote(e.target.value)}
                  rows={4}
                  placeholder="e.g. Patient stable, afebrile, chest clear to auscultation. Continue current IV regimen..."
                  required
                  className="w-full p-2.5 text-xs bg-slate-50 border border-slate-200 rounded-md focus:bg-white"
                />
              </div>
              <div className="flex items-center gap-2">
                <button
                  type="submit"
                  className="px-4 py-2 text-xs font-semibold text-white bg-slate-900 rounded-md hover:bg-slate-800 transition-colors"
                >
                  Post Progress Note
                </button>
                <button
                  type="button"
                  onClick={() => setActiveTab('chart')}
                  className="px-4 py-2 text-xs font-semibold text-slate-700 bg-slate-100 rounded-md hover:bg-slate-200 transition-colors"
                >
                  Cancel
                </button>
              </div>
            </form>
          )}

          {/* TAB 4: TRANSFER BED */}
          {activeTab === 'transfer' && (
            <form onSubmit={handleTransferBed} className="space-y-4 max-w-lg">
              <h3 className="text-sm font-bold text-slate-900">
                Transfer Patient to Another Ward or Bed
              </h3>
              <p className="text-xs text-slate-500">
                Current Location: <strong>{patient.bedNumber || 'None'} ({patient.ward || 'None'})</strong>
              </p>

              <div>
                <label className="text-xs font-semibold text-slate-700 block mb-1">
                  Select New Available Bed
                </label>
                <select
                  value={targetBedId}
                  onChange={(e) => setTargetBedId(e.target.value)}
                  required
                  className="w-full px-3 py-2 text-xs bg-slate-50 border border-slate-200 rounded"
                >
                  <option value="">-- Choose target bed --</option>
                  {availableBeds.map(b => (
                    <option key={b.id} value={b.id}>
                      {b.code} - {b.ward} (₹{b.dailyRate.toLocaleString('en-IN')}/day) - {b.floor}
                    </option>
                  ))}
                </select>
              </div>

              <div className="flex items-center gap-2 pt-2">
                <button
                  type="submit"
                  disabled={!targetBedId}
                  className="px-4 py-2 text-xs font-semibold text-white bg-slate-900 rounded-md hover:bg-slate-800 transition-colors disabled:opacity-50"
                >
                  Execute Bed Transfer
                </button>
                <button
                  type="button"
                  onClick={() => setActiveTab('chart')}
                  className="px-4 py-2 text-xs font-semibold text-slate-700 bg-slate-100 rounded-md hover:bg-slate-200 transition-colors"
                >
                  Cancel
                </button>
              </div>
            </form>
          )}

          {/* TAB 5: DISCHARGE PATIENT */}
          {activeTab === 'discharge' && (
            <form onSubmit={handleDischarge} className="space-y-4 max-w-lg">
              <h3 className="text-sm font-bold text-slate-900">
                Patient Discharge Clearance
              </h3>
              <p className="text-xs text-slate-600">
                Discharging will mark the patient as <strong>Discharged</strong>, update the inpatient census, and release Bed <strong>{patient.bedNumber}</strong> for disinfection & cleaning.
              </p>

              <div>
                <label className="text-xs font-semibold text-slate-700 block mb-1">
                  Discharge Summary & Home Care Advice
                </label>
                <textarea
                  value={dischargeSummary}
                  onChange={(e) => setDischargeSummary(e.target.value)}
                  rows={4}
                  placeholder="e.g. Clinically recovered. Oral medications advised for 7 days. Follow-up OPD visit scheduled in 10 days..."
                  required
                  className="w-full p-2.5 text-xs bg-slate-50 border border-slate-200 rounded-md focus:bg-white"
                />
              </div>

              <div className="flex items-center gap-2 pt-2">
                <button
                  type="submit"
                  className="px-4 py-2 text-xs font-semibold text-white bg-rose-700 rounded-md hover:bg-rose-800 transition-colors"
                >
                  Confirm Discharge & Release Bed
                </button>
                <button
                  type="button"
                  onClick={() => setActiveTab('chart')}
                  className="px-4 py-2 text-xs font-semibold text-slate-700 bg-slate-100 rounded-md hover:bg-slate-200 transition-colors"
                >
                  Cancel
                </button>
              </div>
            </form>
          )}
        </div>

        {/* Modal Footer */}
        <div className="px-6 py-3 border-t border-slate-200 bg-slate-50 flex items-center justify-between text-xs">
          <div className="flex items-center gap-2">
            <button
              onClick={() => {
                setSelectedPatientId(null);
                setIsNewInvoiceModalOpen(true);
              }}
              className="px-3 py-1.5 font-semibold text-slate-700 bg-white hover:bg-slate-100 border border-slate-200 rounded transition-colors"
            >
              Generate Bill / Invoice
            </button>
          </div>
          <button
            onClick={() => setSelectedPatientId(null)}
            className="px-4 py-1.5 font-semibold text-white bg-slate-900 hover:bg-slate-800 rounded transition-colors"
          >
            Close Chart
          </button>
        </div>
      </div>
    </div>
  );
};
