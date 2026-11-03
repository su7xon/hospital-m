import React, { useState } from 'react';
import { useHospital } from '../context/HospitalContext';
import { Doctor } from '../types/hms';
import {
  Stethoscope,
  Phone,
  Mail,
  MapPin,
  Clock,
  UserCheck,
  Calendar,
  Search
} from 'lucide-react';

export const DoctorsView: React.FC = () => {
  const {
    doctors,
    toggleDoctorDuty,
    setIsNewAppointmentModalOpen,
    setActiveTab
  } = useHospital();

  const [search, setSearch] = useState('');
  const [deptFilter, setDeptFilter] = useState('All');

  const filteredDoctors = doctors.filter(doc => {
    const matchesDept = deptFilter === 'All' || doc.department === deptFilter;
    const matchesSearch =
      doc.name.toLowerCase().includes(search.toLowerCase()) ||
      doc.specialty.toLowerCase().includes(search.toLowerCase()) ||
      doc.department.toLowerCase().includes(search.toLowerCase());
    return matchesDept && matchesSearch;
  });

  const onDutyCount = doctors.filter(d => d.onDuty).length;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 pb-2 border-b border-slate-200">
        <div>
          <h1 className="text-xl font-bold text-slate-900 tracking-tight">
            Medical Staff & Consultant Roster
          </h1>
          <p className="text-xs text-slate-500 mt-0.5">
            Specialist clinicians, on-duty emergency shifts, and inpatient allocations.
          </p>
        </div>

        <div className="flex items-center gap-2 text-xs">
          <span className="text-slate-500">Currently On Duty:</span>
          <strong className="font-mono text-emerald-700 bg-emerald-50 border border-emerald-200 px-2.5 py-1 rounded">
            {onDutyCount} of {doctors.length} Doctors
          </strong>
        </div>
      </div>

      {/* Filter and Search */}
      <div className="bg-white p-3.5 rounded-lg border border-slate-200 shadow-2xs flex flex-col md:flex-row items-stretch md:items-center justify-between gap-3">
        <div className="relative flex-1 max-w-md">
          <Search className="w-4 h-4 absolute left-3 top-2.5 text-slate-400" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search by physician name, specialty, department..."
            className="w-full pl-9 pr-3 py-1.5 text-xs bg-slate-50 border border-slate-200 rounded-md focus:bg-white focus:outline-hidden"
          />
        </div>

        <div className="flex items-center gap-2 text-xs">
          <span className="text-slate-500">Department:</span>
          <select
            value={deptFilter}
            onChange={(e) => setDeptFilter(e.target.value)}
            className="bg-slate-50 border border-slate-200 rounded px-2.5 py-1.5 text-xs text-slate-700 focus:outline-hidden"
          >
            <option value="All">All Departments</option>
            <option value="Cardiology">Cardiology</option>
            <option value="Neurology">Neurology</option>
            <option value="Internal Medicine">Internal Medicine</option>
            <option value="Orthopedics">Orthopedics</option>
            <option value="Pediatrics">Pediatrics</option>
            <option value="Emergency Medicine">Emergency Medicine</option>
          </select>
        </div>
      </div>

      {/* Doctors Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {filteredDoctors.map(doctor => (
          <div
            key={doctor.id}
            className="bg-white rounded-lg border border-slate-200 shadow-2xs p-5 flex flex-col justify-between hover:border-slate-300 transition-colors"
          >
            <div>
              {/* Doctor Header */}
              <div className="flex items-start justify-between gap-2">
                <div>
                  <h3 className="font-bold text-sm text-slate-900">
                    {doctor.name}
                  </h3>
                  <span className="text-[11px] text-slate-500 font-medium block">
                    {doctor.qualification}
                  </span>
                  <span className="text-xs font-semibold text-slate-800 block mt-1">
                    {doctor.specialty}
                  </span>
                </div>

                {/* Duty Toggle Button */}
                <button
                  onClick={() => toggleDoctorDuty(doctor.id)}
                  className={`px-2.5 py-1 text-[11px] font-semibold rounded border transition-colors shrink-0 ${
                    doctor.onDuty
                      ? 'bg-emerald-50 border-emerald-200 text-emerald-800 hover:bg-emerald-100'
                      : 'bg-slate-100 border-slate-200 text-slate-600 hover:bg-slate-200'
                  }`}
                >
                  {doctor.onDuty ? '● On Floor' : '○ Off Duty'}
                </button>
              </div>

              {/* Department & Location */}
              <div className="mt-4 space-y-1.5 text-xs text-slate-600 border-t border-slate-100 pt-3">
                <div className="flex items-center gap-2">
                  <span className="text-slate-400">Department:</span>
                  <span className="font-semibold text-slate-800">{doctor.department}</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-slate-400">Clinic Cabin:</span>
                  <span>{doctor.room}</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-slate-400">Shift Timings:</span>
                  <span className="font-mono">{doctor.scheduleHours}</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-slate-400">Active Inpatients:</span>
                  <span className="font-mono font-semibold text-slate-800">{doctor.activePatients} under care</span>
                </div>
              </div>

              {/* Contact info */}
              <div className="mt-3 pt-3 border-t border-slate-100 text-[11px] text-slate-500 font-mono space-y-0.5">
                <div>Phone: {doctor.phone}</div>
                <div>Email: {doctor.email}</div>
              </div>
            </div>

            {/* Quick Action */}
            <div className="mt-4 pt-3 border-t border-slate-100 flex items-center justify-between text-xs">
              <button
                onClick={() => {
                  setActiveTab('appointments');
                }}
                className="w-full py-1.5 font-semibold text-slate-800 bg-slate-100 hover:bg-slate-200 rounded text-center transition-colors"
              >
                View Doctor Schedule
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
