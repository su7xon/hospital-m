import React, { useState } from 'react';
import { useHospital } from '../context/HospitalContext';
import { TriageLevel } from '../types/hms';
import { X, AlertCircle } from 'lucide-react';

export const EmergencyModal: React.FC = () => {
  const {
    isEmergencyModalOpen,
    setIsEmergencyModalOpen,
    addEmergencyCase,
    doctors,
    showToast
  } = useHospital();

  const [patientName, setPatientName] = useState('');
  const [age, setAge] = useState(38);
  const [gender, setGender] = useState<'Male' | 'Female' | 'Other'>('Male');
  const [triageLevel, setTriageLevel] = useState<TriageLevel>('P2 - Emergency');
  const [chiefComplaint, setChiefComplaint] = useState('');
  const [vitalsBrief, setVitalsBrief] = useState('BP: 130/85 | HR: 88 | SpO2: 97%');
  const [assignedDoctor, setAssignedDoctor] = useState('Dr. Meera Nambiar');
  const [notes, setNotes] = useState('');

  if (!isEmergencyModalOpen) return null;

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!patientName.trim()) {
      showToast('Please enter patient name or triage tag (e.g. Unidentified Male).');
      return;
    }

    addEmergencyCase({
      patientName: patientName.trim(),
      age: Number(age),
      gender,
      triageLevel,
      chiefComplaint: chiefComplaint.trim() || 'Acute trauma / medical emergency',
      vitalsBrief: vitalsBrief.trim(),
      assignedDoctor,
      status: 'Waiting',
      notes: notes.trim() || 'Triage intake logged at ER counter.'
    });

    setIsEmergencyModalOpen(false);
    setPatientName('');
    setChiefComplaint('');
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-3 sm:p-6 bg-slate-900/50 backdrop-blur-xs">
      <div className="bg-white rounded-xl border border-slate-200 shadow-xl w-full max-w-lg p-4 sm:p-5 space-y-4 max-h-[92vh] overflow-y-auto">
        {/* Header */}
        <div className="flex items-start justify-between border-b border-slate-100 pb-3">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded bg-rose-50 border border-rose-200 flex items-center justify-center text-rose-700">
              <AlertCircle className="w-4 h-4" />
            </div>
            <div>
              <h2 className="text-sm font-bold text-slate-900">
                Emergency Department Triage Intake
              </h2>
              <span className="text-[11px] text-slate-500">
                Manchester Triage System (Priority Levels 1 through 5)
              </span>
            </div>
          </div>
          <button
            onClick={() => setIsEmergencyModalOpen(false)}
            className="text-slate-400 hover:text-slate-600"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-3 text-xs">
          <div>
            <label className="font-semibold text-slate-700 block mb-1">
              Patient Name / Identification *
            </label>
            <input
              type="text"
              placeholder="e.g. Sunil Verma (or Unknown Trauma Male #2)"
              value={patientName}
              onChange={(e) => setPatientName(e.target.value)}
              required
              className="w-full px-3 py-1.5 bg-slate-50 border border-slate-200 rounded focus:bg-white"
            />
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="font-semibold text-slate-700 block mb-1">Age</label>
              <input
                type="number"
                value={age}
                onChange={(e) => setAge(Number(e.target.value))}
                required
                className="w-full px-3 py-1.5 bg-slate-50 border border-slate-200 rounded font-mono"
              />
            </div>

            <div>
              <label className="font-semibold text-slate-700 block mb-1">Gender</label>
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
          </div>

          <div>
            <label className="font-semibold text-slate-700 block mb-1">
              Triage Priority Category *
            </label>
            <select
              value={triageLevel}
              onChange={(e) => setTriageLevel(e.target.value as any)}
              className="w-full px-3 py-1.5 bg-slate-50 border border-slate-200 rounded font-semibold text-slate-900"
            >
              <option value="P1 - Resuscitation">P1 - Resuscitation (Immediate life threat)</option>
              <option value="P2 - Emergency">P2 - Emergency (Within 10 minutes)</option>
              <option value="P3 - Urgent">P3 - Urgent (Within 60 minutes)</option>
              <option value="P4 - Semi-Urgent">P4 - Semi-Urgent (Within 120 minutes)</option>
              <option value="P5 - Non-Urgent">P5 - Non-Urgent (Standard OPD)</option>
            </select>
          </div>

          <div>
            <label className="font-semibold text-slate-700 block mb-1">
              Emergency Chief Complaint & Symptoms *
            </label>
            <textarea
              rows={2}
              placeholder="e.g. Acute severe shortness of breath, bilateral wheezing..."
              value={chiefComplaint}
              onChange={(e) => setChiefComplaint(e.target.value)}
              required
              className="w-full p-2 bg-slate-50 border border-slate-200 rounded focus:bg-white"
            />
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <div>
              <label className="font-semibold text-slate-700 block mb-1">
                Triage Vitals Summary
              </label>
              <input
                type="text"
                value={vitalsBrief}
                onChange={(e) => setVitalsBrief(e.target.value)}
                placeholder="BP: 120/80 | HR: 80 | SpO2: 98%"
                className="w-full px-3 py-1.5 bg-slate-50 border border-slate-200 rounded font-mono"
              />
            </div>

            <div>
              <label className="font-semibold text-slate-700 block mb-1">
                Assigned ER Physician
              </label>
              <select
                value={assignedDoctor}
                onChange={(e) => setAssignedDoctor(e.target.value)}
                className="w-full px-3 py-1.5 bg-slate-50 border border-slate-200 rounded"
              >
                {doctors.map(d => (
                  <option key={d.id} value={d.name}>
                    {d.name} ({d.department})
                  </option>
                ))}
              </select>
            </div>
          </div>

          <div>
            <label className="font-semibold text-slate-700 block mb-1">
              Immediate Clinical Orders / Interventions
            </label>
            <input
              type="text"
              placeholder="e.g. High flow oxygen, 2 wide bore IV lines, ECG stat"
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              className="w-full px-3 py-1.5 bg-slate-50 border border-slate-200 rounded"
            />
          </div>

          <div className="flex items-center justify-end gap-2 pt-3 border-t border-slate-100">
            <button
              type="button"
              onClick={() => setIsEmergencyModalOpen(false)}
              className="px-3 py-1.5 font-semibold text-slate-700 bg-slate-100 hover:bg-slate-200 rounded"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="px-4 py-1.5 font-semibold text-white bg-rose-700 hover:bg-rose-800 rounded"
            >
              Log ER Admission
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
