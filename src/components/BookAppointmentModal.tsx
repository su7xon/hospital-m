import React, { useState } from 'react';
import { useHospital } from '../context/HospitalContext';
import { Appointment } from '../types/hms';
import { X, Calendar, Clock, User, Stethoscope } from 'lucide-react';

export const BookAppointmentModal: React.FC = () => {
  const {
    isNewAppointmentModalOpen,
    setIsNewAppointmentModalOpen,
    bookAppointment,
    doctors,
    patients,
    showToast
  } = useHospital();

  const [patientName, setPatientName] = useState('');
  const [patientPhone, setPatientPhone] = useState('+91 ');
  const [patientMrn, setPatientMrn] = useState('');
  const [doctorId, setDoctorId] = useState(doctors[0]?.id || '');
  const [date, setDate] = useState('2026-10-20');
  const [timeSlot, setTimeSlot] = useState('11:00 AM');
  const [consultType, setConsultType] = useState<Appointment['type']>('OPD');
  const [reason, setReason] = useState('');

  if (!isNewAppointmentModalOpen) return null;

  const selectedDoctor = doctors.find(d => d.id === doctorId);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!patientName.trim()) {
      showToast('Please enter patient name.');
      return;
    }

    bookAppointment({
      patientName: patientName.trim(),
      patientPhone: patientPhone.trim(),
      patientMrn: patientMrn.trim() || undefined,
      doctorId,
      doctorName: selectedDoctor ? selectedDoctor.name : 'Attending Specialist',
      department: selectedDoctor ? selectedDoctor.department : 'General OPD',
      date,
      timeSlot,
      status: 'Scheduled',
      reason: reason.trim() || 'General specialist consultation',
      type: consultType
    });

    setIsNewAppointmentModalOpen(false);
    setPatientName('');
    setReason('');
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-3 sm:p-6 bg-slate-900/50 backdrop-blur-xs">
      <div className="bg-white rounded-xl border border-slate-200 shadow-xl w-full max-w-lg p-4 sm:p-5 space-y-4 max-h-[92vh] overflow-y-auto">
        {/* Header */}
        <div className="flex items-start justify-between border-b border-slate-100 pb-3">
          <div>
            <h2 className="text-sm font-bold text-slate-900">
              Book Outpatient Consultation (OPD)
            </h2>
            <span className="text-[11px] text-slate-500">
              Schedule specialist appointment slot and patient registration
            </span>
          </div>
          <button
            onClick={() => setIsNewAppointmentModalOpen(false)}
            className="text-slate-400 hover:text-slate-600"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-3 text-xs">
          <div>
            <label className="font-semibold text-slate-700 block mb-1">
              Patient Full Name *
            </label>
            <input
              type="text"
              placeholder="e.g. Ramesh Patel"
              value={patientName}
              onChange={(e) => setPatientName(e.target.value)}
              required
              className="w-full px-3 py-1.5 bg-slate-50 border border-slate-200 rounded focus:bg-white"
            />
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="font-semibold text-slate-700 block mb-1">
                Contact Phone *
              </label>
              <input
                type="text"
                value={patientPhone}
                onChange={(e) => setPatientPhone(e.target.value)}
                required
                className="w-full px-3 py-1.5 bg-slate-50 border border-slate-200 rounded font-mono"
              />
            </div>

            <div>
              <label className="font-semibold text-slate-700 block mb-1">
                Existing Hospital MRN (Optional)
              </label>
              <input
                type="text"
                placeholder="e.g. HSP-4109"
                value={patientMrn}
                onChange={(e) => setPatientMrn(e.target.value)}
                className="w-full px-3 py-1.5 bg-slate-50 border border-slate-200 rounded font-mono"
              />
            </div>
          </div>

          <div>
            <label className="font-semibold text-slate-700 block mb-1">
              Select Specialist Doctor *
            </label>
            <select
              value={doctorId}
              onChange={(e) => setDoctorId(e.target.value)}
              required
              className="w-full px-3 py-1.5 bg-slate-50 border border-slate-200 rounded"
            >
              {doctors.map(d => (
                <option key={d.id} value={d.id}>
                  {d.name} ({d.department} · {d.room})
                </option>
              ))}
            </select>
          </div>

          <div className="grid grid-cols-3 gap-3">
            <div>
              <label className="font-semibold text-slate-700 block mb-1">Date</label>
              <input
                type="date"
                value={date}
                onChange={(e) => setDate(e.target.value)}
                required
                className="w-full px-2.5 py-1.5 bg-slate-50 border border-slate-200 rounded font-mono text-[11px]"
              />
            </div>

            <div>
              <label className="font-semibold text-slate-700 block mb-1">Time Slot</label>
              <select
                value={timeSlot}
                onChange={(e) => setTimeSlot(e.target.value)}
                className="w-full px-2.5 py-1.5 bg-slate-50 border border-slate-200 rounded font-mono"
              >
                <option value="09:00 AM">09:00 AM</option>
                <option value="09:30 AM">09:30 AM</option>
                <option value="10:00 AM">10:00 AM</option>
                <option value="10:30 AM">10:30 AM</option>
                <option value="11:00 AM">11:00 AM</option>
                <option value="11:30 AM">11:30 AM</option>
                <option value="12:00 PM">12:00 PM</option>
                <option value="02:30 PM">02:30 PM</option>
                <option value="03:00 PM">03:00 PM</option>
                <option value="03:30 PM">03:30 PM</option>
                <option value="04:00 PM">04:00 PM</option>
              </select>
            </div>

            <div>
              <label className="font-semibold text-slate-700 block mb-1">Type</label>
              <select
                value={consultType}
                onChange={(e) => setConsultType(e.target.value as any)}
                className="w-full px-2.5 py-1.5 bg-slate-50 border border-slate-200 rounded"
              >
                <option value="OPD">OPD Consultation</option>
                <option value="Follow-up">Follow-up Visit</option>
                <option value="Review">Report Review</option>
              </select>
            </div>
          </div>

          <div>
            <label className="font-semibold text-slate-700 block mb-1">
              Chief Symptom / Clinical Indication
            </label>
            <input
              type="text"
              placeholder="e.g. Chronic back pain, review MRI spine reports"
              value={reason}
              onChange={(e) => setReason(e.target.value)}
              className="w-full px-3 py-1.5 bg-slate-50 border border-slate-200 rounded"
            />
          </div>

          <div className="flex items-center justify-end gap-2 pt-3 border-t border-slate-100">
            <button
              type="button"
              onClick={() => setIsNewAppointmentModalOpen(false)}
              className="px-3 py-1.5 font-semibold text-slate-700 bg-slate-100 hover:bg-slate-200 rounded"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="px-4 py-1.5 font-semibold text-white bg-slate-900 hover:bg-slate-800 rounded"
            >
              Confirm Appointment
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
