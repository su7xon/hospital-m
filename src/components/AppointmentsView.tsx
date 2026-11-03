import React, { useState } from 'react';
import { useHospital } from '../context/HospitalContext';
import { Appointment, AppointmentStatus } from '../types/hms';
import {
  Calendar,
  Clock,
  Plus,
  User,
  Stethoscope,
  Filter,
  CheckCircle2,
  Phone
} from 'lucide-react';

export const AppointmentsView: React.FC = () => {
  const {
    appointments,
    doctors,
    updateAppointmentStatus,
    setIsNewAppointmentModalOpen,
    setSelectedPatientId,
    patients
  } = useHospital();

  const [selectedDoctorId, setSelectedDoctorId] = useState<string>('All');
  const [selectedStatus, setSelectedStatus] = useState<string>('All');
  const [search, setSearch] = useState('');

  // Filtered appointments
  const filteredAppointments = appointments.filter(apt => {
    const matchesDoctor = selectedDoctorId === 'All' || apt.doctorId === selectedDoctorId;
    const matchesStatus = selectedStatus === 'All' || apt.status === selectedStatus;
    const matchesSearch =
      apt.patientName.toLowerCase().includes(search.toLowerCase()) ||
      apt.appointmentNumber.toLowerCase().includes(search.toLowerCase()) ||
      apt.doctorName.toLowerCase().includes(search.toLowerCase()) ||
      apt.patientPhone.includes(search);

    return matchesDoctor && matchesStatus && matchesSearch;
  });

  const scheduledCount = appointments.filter(a => a.status === 'Scheduled').length;
  const checkedInCount = appointments.filter(a => a.status === 'Checked-in').length;
  const inConsultCount = appointments.filter(a => a.status === 'In Consultation').length;
  const completedCount = appointments.filter(a => a.status === 'Completed').length;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 pb-2 border-b border-slate-200">
        <div>
          <h1 className="text-xl font-bold text-slate-900 tracking-tight">
            Outpatient Department (OPD) Scheduling
          </h1>
          <p className="text-xs text-slate-500 mt-0.5">
            Specialist clinic bookings, patient queue management, and consultation status.
          </p>
        </div>

        <button
          onClick={() => setIsNewAppointmentModalOpen(true)}
          className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold text-white bg-slate-900 hover:bg-slate-800 rounded-md transition-colors self-start sm:self-auto shadow-xs"
        >
          <Plus className="w-3.5 h-3.5" />
          <span>Book New Appointment</span>
        </button>
      </div>

      {/* KPI Stats */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        <div className="bg-white p-3.5 rounded-lg border border-slate-200 shadow-2xs">
          <span className="text-xs font-medium text-slate-500 block">Waiting / Scheduled</span>
          <span className="text-xl font-bold font-mono text-slate-900 tabular-nums block mt-1">
            {scheduledCount}
          </span>
          <span className="text-[11px] text-slate-400 mt-1 block">Pending arrival</span>
        </div>

        <div className="bg-white p-3.5 rounded-lg border border-slate-200 shadow-2xs">
          <span className="text-xs font-medium text-slate-500 block">Checked-in At Clinic</span>
          <span className="text-xl font-bold font-mono text-blue-700 tabular-nums block mt-1">
            {checkedInCount}
          </span>
          <span className="text-[11px] text-blue-600 mt-1 block">In waiting room</span>
        </div>

        <div className="bg-white p-3.5 rounded-lg border border-slate-200 shadow-2xs">
          <span className="text-xs font-medium text-slate-500 block">In Consultation</span>
          <span className="text-xl font-bold font-mono text-amber-700 tabular-nums block mt-1">
            {inConsultCount}
          </span>
          <span className="text-[11px] text-amber-600 mt-1 block">Active with doctor</span>
        </div>

        <div className="bg-white p-3.5 rounded-lg border border-slate-200 shadow-2xs">
          <span className="text-xs font-medium text-slate-500 block">Completed Today</span>
          <span className="text-xl font-bold font-mono text-emerald-700 tabular-nums block mt-1">
            {completedCount}
          </span>
          <span className="text-[11px] text-emerald-600 mt-1 block">Discharged with prescription</span>
        </div>
      </div>

      {/* Search & Filters */}
      <div className="bg-white p-3.5 rounded-lg border border-slate-200 shadow-2xs space-y-3">
        <div className="flex flex-col md:flex-row items-stretch md:items-center justify-between gap-3">
          {/* Search */}
          <div className="relative flex-1 max-w-md">
            <input
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search by patient name, phone, appointment #..."
              className="w-full px-3 py-1.5 text-xs bg-slate-50 border border-slate-200 rounded-md focus:bg-white focus:outline-hidden"
            />
          </div>

          {/* Doctor filter dropdown */}
          <div className="flex items-center gap-2 text-xs">
            <span className="text-slate-500">Doctor:</span>
            <select
              value={selectedDoctorId}
              onChange={(e) => setSelectedDoctorId(e.target.value)}
              className="bg-slate-50 border border-slate-200 rounded px-2.5 py-1.5 text-xs text-slate-700 focus:outline-hidden"
            >
              <option value="All">All Specialists ({doctors.length})</option>
              {doctors.map(d => (
                <option key={d.id} value={d.id}>
                  {d.name} ({d.department})
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* Status segmented filters - swipeable on mobile */}
        <div className="flex items-center gap-1 pt-2 border-t border-slate-100 text-xs overflow-x-auto scrollbar-none pb-0.5 touch-pan-x">
          <span className="text-slate-500 mr-2 shrink-0">Status:</span>
          {['All', 'Scheduled', 'Checked-in', 'In Consultation', 'Completed', 'Cancelled'].map(st => {
            const isActive = selectedStatus === st;
            return (
              <button
                key={st}
                onClick={() => setSelectedStatus(st)}
                className={`px-2.5 py-1 text-xs font-medium rounded transition-colors whitespace-nowrap shrink-0 ${
                  isActive
                    ? 'bg-slate-900 text-white shadow-2xs'
                    : 'text-slate-600 hover:bg-slate-100'
                }`}
              >
                {st}
              </button>
            );
          })}
        </div>
      </div>

      {/* Appointments Table */}
      <div className="bg-white rounded-lg border border-slate-200 shadow-2xs overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs border-collapse">
            <thead>
              <tr className="bg-slate-50/80 border-b border-slate-200 text-slate-600 font-semibold">
                <th className="py-2.5 px-4 font-medium">Slot & Appt #</th>
                <th className="py-2.5 px-4 font-medium">Patient Details</th>
                <th className="py-2.5 px-4 font-medium">Attending Specialist</th>
                <th className="py-2.5 px-4 font-medium">Clinical Reason / Type</th>
                <th className="py-2.5 px-4 font-medium">Queue Status</th>
                <th className="py-2.5 px-4 font-medium text-right">Quick Transition</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {filteredAppointments.length === 0 ? (
                <tr>
                  <td colSpan={6} className="py-10 text-center text-slate-400 text-xs">
                    No appointments matching the selected criteria.
                  </td>
                </tr>
              ) : (
                filteredAppointments.map(apt => {
                  const linkedPatient = patients.find(p => p.mrn === apt.patientMrn || p.name === apt.patientName);

                  return (
                    <tr key={apt.id} className="hover:bg-slate-50/60 transition-colors">
                      {/* Slot & Code */}
                      <td className="py-3 px-4 whitespace-nowrap">
                        <span className="font-mono font-bold text-slate-900 block">
                          {apt.timeSlot}
                        </span>
                        <span className="text-[11px] font-mono text-slate-400 block">
                          {apt.appointmentNumber} · {apt.date}
                        </span>
                      </td>

                      {/* Patient */}
                      <td className="py-3 px-4">
                        <div className="flex items-center gap-1.5">
                          <span
                            onClick={() => {
                              if (linkedPatient) setSelectedPatientId(linkedPatient.id);
                            }}
                            className={`font-semibold text-slate-900 ${
                              linkedPatient ? 'hover:text-blue-700 cursor-pointer underline-offset-2 hover:underline' : ''
                            }`}
                          >
                            {apt.patientName}
                          </span>
                          {apt.patientMrn && (
                            <span className="font-mono text-[10px] text-slate-400">
                              ({apt.patientMrn})
                            </span>
                          )}
                        </div>
                        <span className="text-[11px] text-slate-500 block font-mono mt-0.5">
                          {apt.patientPhone}
                        </span>
                      </td>

                      {/* Doctor */}
                      <td className="py-3 px-4 whitespace-nowrap">
                        <span className="font-semibold text-slate-800 block">
                          {apt.doctorName}
                        </span>
                        <span className="text-[11px] text-slate-500 block">
                          {apt.department}
                        </span>
                      </td>

                      {/* Reason & Type */}
                      <td className="py-3 px-4 max-w-xs">
                        <p className="text-slate-800 font-medium truncate" title={apt.reason}>
                          {apt.reason}
                        </p>
                        <span className="text-[11px] text-slate-400 block mt-0.5">
                          {apt.type} consultation
                        </span>
                      </td>

                      {/* Status Selector */}
                      <td className="py-3 px-4 whitespace-nowrap">
                        <select
                          value={apt.status}
                          onChange={(e) => updateAppointmentStatus(apt.id, e.target.value as any)}
                          className="bg-slate-50 border border-slate-200 rounded px-2 py-1 text-xs font-medium text-slate-800 focus:outline-hidden"
                        >
                          <option value="Scheduled">Scheduled</option>
                          <option value="Checked-in">Checked-in</option>
                          <option value="In Consultation">In Consultation</option>
                          <option value="Completed">Completed</option>
                          <option value="Cancelled">Cancelled</option>
                        </select>
                      </td>

                      {/* Quick Action */}
                      <td className="py-3 px-4 whitespace-nowrap text-right">
                        {apt.status === 'Scheduled' && (
                          <button
                            onClick={() => updateAppointmentStatus(apt.id, 'Checked-in')}
                            className="px-2.5 py-1 text-xs font-semibold text-blue-700 bg-blue-50 hover:bg-blue-100 rounded transition-colors"
                          >
                            Check-in
                          </button>
                        )}
                        {apt.status === 'Checked-in' && (
                          <button
                            onClick={() => updateAppointmentStatus(apt.id, 'In Consultation')}
                            className="px-2.5 py-1 text-xs font-semibold text-amber-700 bg-amber-50 hover:bg-amber-100 rounded transition-colors"
                          >
                            Call Patient
                          </button>
                        )}
                        {apt.status === 'In Consultation' && (
                          <button
                            onClick={() => updateAppointmentStatus(apt.id, 'Completed')}
                            className="px-2.5 py-1 text-xs font-semibold text-emerald-700 bg-emerald-50 hover:bg-emerald-100 rounded transition-colors"
                          >
                            Complete
                          </button>
                        )}
                        {apt.status === 'Completed' && (
                          <span className="text-[11px] text-emerald-700 font-medium">
                            ✓ Done
                          </span>
                        )}
                        {apt.status === 'Cancelled' && (
                          <span className="text-[11px] text-slate-400">
                            Cancelled
                          </span>
                        )}
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
