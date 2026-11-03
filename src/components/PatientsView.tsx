import React, { useState } from 'react';
import { useHospital } from '../context/HospitalContext';
import { Patient, PatientStatus } from '../types/hms';
import {
  Search,
  Plus,
  Filter,
  Download,
  Activity,
  HeartPulse,
  Eye,
  UserPlus
} from 'lucide-react';

export const PatientsView: React.FC = () => {
  const {
    patients,
    setSelectedPatientId,
    setIsAdmitModalOpen,
    showToast
  } = useHospital();

  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState<'All' | PatientStatus>('All');
  const [wardFilter, setWardFilter] = useState<string>('All');

  // Filtered patients
  const filteredPatients = patients.filter(patient => {
    const matchesSearch =
      patient.name.toLowerCase().includes(search.toLowerCase()) ||
      patient.mrn.toLowerCase().includes(search.toLowerCase()) ||
      patient.phone.includes(search) ||
      patient.diagnoses.some(d => d.toLowerCase().includes(search.toLowerCase())) ||
      patient.chiefComplaint.toLowerCase().includes(search.toLowerCase());

    const matchesStatus = statusFilter === 'All' || patient.status === statusFilter;
    const matchesWard = wardFilter === 'All' || patient.ward === wardFilter;

    return matchesSearch && matchesStatus && matchesWard;
  });

  const exportPatientsData = () => {
    const dataStr = 'data:text/json;charset=utf-8,' + encodeURIComponent(JSON.stringify(patients, null, 2));
    const downloadAnchor = document.createElement('a');
    downloadAnchor.setAttribute('href', dataStr);
    downloadAnchor.setAttribute('download', `aegis_patients_registry_${new Date().toISOString().substring(0, 10)}.json`);
    document.body.appendChild(downloadAnchor);
    downloadAnchor.click();
    downloadAnchor.remove();
    showToast('Exported patient registry records to JSON.');
  };

  return (
    <div className="space-y-5">
      {/* View Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 pb-2 border-b border-slate-200">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-xl font-bold text-slate-900 tracking-tight">
              Patient Clinical Directory
            </h1>
            <span className="text-xs font-mono text-slate-500 tabular-nums">
              ({patients.length} total records)
            </span>
          </div>
          <p className="text-xs text-slate-500 mt-0.5">
            Electronic Health Records (EHR), active ward census, vitals history, and intake charts.
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-2 w-full sm:w-auto">
          <button
            onClick={exportPatientsData}
            className="flex-1 sm:flex-initial flex items-center justify-center gap-1.5 px-3 py-1.5 text-xs font-semibold text-slate-700 bg-white hover:bg-slate-50 border border-slate-200 rounded-md transition-colors shadow-2xs"
          >
            <Download className="w-3.5 h-3.5 text-slate-500 shrink-0" />
            <span className="whitespace-nowrap">Export</span>
          </button>
          <button
            onClick={() => setIsAdmitModalOpen(true)}
            className="flex-1 sm:flex-initial flex items-center justify-center gap-1.5 px-3 py-1.5 text-xs font-semibold text-white bg-slate-900 hover:bg-slate-800 rounded-md transition-colors shadow-xs whitespace-nowrap"
          >
            <Plus className="w-3.5 h-3.5 shrink-0" />
            <span>Admit Patient</span>
          </button>
        </div>
      </div>

      {/* Filter and Search Bar */}
      <div className="bg-white p-3.5 rounded-lg border border-slate-200 shadow-2xs space-y-3">
        <div className="flex flex-col md:flex-row items-stretch md:items-center justify-between gap-3">
          {/* Live Search */}
          <div className="relative flex-1 max-w-md">
            <Search className="w-4 h-4 absolute left-3 top-2.5 text-slate-400" />
            <input
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search by patient name, MRN (e.g. HSP-4109), phone, diagnosis..."
              className="w-full pl-9 pr-3 py-1.5 text-xs bg-slate-50 border border-slate-200 rounded-md focus:bg-white focus:outline-hidden focus:border-slate-400 transition-colors"
            />
            {search && (
              <button
                onClick={() => setSearch('')}
                className="absolute right-2.5 top-2 text-xs text-slate-400 hover:text-slate-600"
              >
                Clear
              </button>
            )}
          </div>

          {/* Ward filter selector */}
          <div className="flex items-center gap-2 text-xs">
            <span className="text-slate-500 shrink-0">Ward:</span>
            <select
              value={wardFilter}
              onChange={(e) => setWardFilter(e.target.value)}
              className="w-full sm:w-auto bg-slate-50 border border-slate-200 rounded px-2.5 py-1.5 text-xs text-slate-700 focus:outline-hidden"
            >
              <option value="All">All Locations</option>
              <option value="ICU">ICU (Intensive Care)</option>
              <option value="General Ward A">General Ward A</option>
              <option value="General Ward B">General Ward B</option>
              <option value="Private Suite">Private Suite</option>
              <option value="Emergency Care">Emergency Care</option>
            </select>
          </div>
        </div>

        {/* Status segmented filters (Functional Buttons - horizontally swipeable on mobile) */}
        <div className="flex items-center gap-1.5 pt-2 border-t border-slate-100 overflow-x-auto scrollbar-none pb-0.5 touch-pan-x">
          {(['All', 'Admitted', 'ICU', 'Emergency', 'Outpatient', 'Discharged'] as const).map(st => {
            const isActive = statusFilter === st;
            const count = st === 'All'
              ? patients.length
              : patients.filter(p => p.status === st).length;

            return (
              <button
                key={st}
                onClick={() => setStatusFilter(st)}
                className={`px-2.5 py-1 text-xs font-medium rounded transition-colors whitespace-nowrap shrink-0 flex items-center gap-1.5 ${
                  isActive
                    ? 'bg-slate-900 text-white shadow-2xs'
                    : 'text-slate-600 hover:bg-slate-100'
                }`}
              >
                <span>{st}</span>
                <span className={`text-[10px] font-mono tabular-nums ${isActive ? 'text-slate-300' : 'text-slate-400'}`}>
                  {count}
                </span>
              </button>
            );
          })}
        </div>
      </div>

      {/* Patient Table */}
      <div className="bg-white rounded-lg border border-slate-200 shadow-2xs overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs border-collapse">
            <thead>
              <tr className="bg-slate-50/80 border-b border-slate-200 text-slate-600 font-semibold">
                <th className="py-2.5 px-4 font-medium">MRN / Intake Date</th>
                <th className="py-2.5 px-4 font-medium">Patient Details</th>
                <th className="py-2.5 px-4 font-medium">Ward & Bed</th>
                <th className="py-2.5 px-4 font-medium">Chief Complaint / Diagnosis</th>
                <th className="py-2.5 px-4 font-medium">Attending Doctor</th>
                <th className="py-2.5 px-4 font-medium">Latest Vitals</th>
                <th className="py-2.5 px-4 font-medium">Status</th>
                <th className="py-2.5 px-4 font-medium text-right">Chart</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {filteredPatients.length === 0 ? (
                <tr>
                  <td colSpan={8} className="py-12 text-center text-slate-400">
                    <p className="text-sm font-medium">No matching patient records found.</p>
                    <p className="text-xs text-slate-400 mt-1">Try adjusting search terms or status filters.</p>
                  </td>
                </tr>
              ) : (
                filteredPatients.map(patient => {
                  const latestVital = patient.vitals[0];
                  return (
                    <tr
                      key={patient.id}
                      onClick={() => setSelectedPatientId(patient.id)}
                      className="hover:bg-slate-50/70 transition-colors cursor-pointer group"
                    >
                      {/* MRN & Date */}
                      <td className="py-3 px-4 whitespace-nowrap">
                        <span className="font-mono font-semibold text-slate-900 block">
                          {patient.mrn}
                        </span>
                        <span className="text-[11px] text-slate-400 block font-mono">
                          {patient.admissionDate.substring(0, 10)}
                        </span>
                      </td>

                      {/* Patient Name, Age, Blood Group */}
                      <td className="py-3 px-4">
                        <span className="font-semibold text-slate-900 group-hover:text-blue-700 transition-colors block">
                          {patient.name}
                        </span>
                        <div className="flex items-center gap-1.5 text-[11px] text-slate-500 mt-0.5">
                          <span>{patient.age}y / {patient.gender.charAt(0)}</span>
                          <span className="text-slate-300" aria-hidden="true">·</span>
                          <span className="font-mono text-slate-600 font-medium">{patient.bloodGroup}</span>
                          <span className="text-slate-300" aria-hidden="true">·</span>
                          <span>{patient.phone}</span>
                        </div>
                      </td>

                      {/* Ward & Bed */}
                      <td className="py-3 px-4 whitespace-nowrap">
                        {patient.bedNumber ? (
                          <div>
                            <span className="font-semibold text-slate-800 block">
                              {patient.bedNumber}
                            </span>
                            <span className="text-[11px] text-slate-500 block">
                              {patient.ward}
                            </span>
                          </div>
                        ) : (
                          <span className="text-slate-400 italic">OPD / Not Assigned</span>
                        )}
                      </td>

                      {/* Complaint / Diagnosis */}
                      <td className="py-3 px-4 max-w-xs">
                        <p className="font-medium text-slate-800 truncate" title={patient.diagnoses[0] || patient.chiefComplaint}>
                          {patient.diagnoses[0] || patient.chiefComplaint}
                        </p>
                        {patient.allergies.length > 0 && patient.allergies[0] !== 'No known drug allergies (NKDA)' && patient.allergies[0] !== 'No known allergies' && (
                          <span className="text-[10px] text-rose-600 block mt-0.5 truncate">
                            Allergy: {patient.allergies.join(', ')}
                          </span>
                        )}
                      </td>

                      {/* Attending Doctor */}
                      <td className="py-3 px-4 whitespace-nowrap">
                        <span className="font-medium text-slate-800 block">
                          {patient.assignedDoctorName}
                        </span>
                        <span className="text-[11px] text-slate-400 block">
                          {patient.department}
                        </span>
                      </td>

                      {/* Vitals */}
                      <td className="py-3 px-4 whitespace-nowrap font-mono tabular-nums">
                        {latestVital ? (
                          <div>
                            <span className="text-slate-700 block font-medium">
                              HR {latestVital.heartRate} · BP {latestVital.bloodPressure}
                            </span>
                            <span className="text-[11px] text-slate-400 block">
                              SpO2 {latestVital.spo2}% · {latestVital.temperature}°F
                            </span>
                          </div>
                        ) : (
                          <span className="text-slate-400 text-[11px]">Pending intake</span>
                        )}
                      </td>

                      {/* Status (Unboxed metadata with typographic text) */}
                      <td className="py-3 px-4 whitespace-nowrap">
                        <span className={`text-xs font-semibold ${
                          patient.status === 'ICU'
                            ? 'text-rose-700'
                            : patient.status === 'Emergency'
                            ? 'text-amber-700'
                            : patient.status === 'Admitted'
                            ? 'text-slate-900'
                            : 'text-slate-500'
                        }`}>
                          {patient.status}
                        </span>
                      </td>

                      {/* Action */}
                      <td className="py-3 px-4 whitespace-nowrap text-right">
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            setSelectedPatientId(patient.id);
                          }}
                          className="px-2.5 py-1 text-xs font-medium text-slate-700 hover:text-slate-900 hover:bg-slate-100 rounded transition-colors"
                        >
                          View Chart →
                        </button>
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
