import React, { useState, useEffect, useRef } from 'react';
import { useHospital } from '../context/HospitalContext';
import {
  Search,
  User,
  BedDouble,
  Stethoscope,
  Plus,
  ArrowRight,
  X
} from 'lucide-react';

export const CommandPaletteModal: React.FC = () => {
  const {
    isSearchOpen,
    setIsSearchOpen,
    patients,
    doctors,
    beds,
    setSelectedPatientId,
    setActiveTab,
    setIsAdmitModalOpen,
    setIsEmergencyModalOpen,
    setIsNewAppointmentModalOpen,
    setIsNewInvoiceModalOpen
  } = useHospital();

  const [query, setQuery] = useState('');
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (isSearchOpen) {
      setTimeout(() => inputRef.current?.focus(), 50);
    } else {
      setQuery('');
    }
  }, [isSearchOpen]);

  if (!isSearchOpen) return null;

  const matchedPatients = query.trim()
    ? patients.filter(
        p =>
          p.name.toLowerCase().includes(query.toLowerCase()) ||
          p.mrn.toLowerCase().includes(query.toLowerCase()) ||
          p.phone.includes(query)
      ).slice(0, 5)
    : [];

  const matchedDoctors = query.trim()
    ? doctors.filter(
        d =>
          d.name.toLowerCase().includes(query.toLowerCase()) ||
          d.specialty.toLowerCase().includes(query.toLowerCase()) ||
          d.department.toLowerCase().includes(query.toLowerCase())
      ).slice(0, 3)
    : [];

  const matchedBeds = query.trim()
    ? beds.filter(
        b =>
          b.code.toLowerCase().includes(query.toLowerCase()) ||
          b.ward.toLowerCase().includes(query.toLowerCase())
      ).slice(0, 3)
    : [];

  const quickActions = [
    { label: 'Admit New Patient', action: () => { setIsSearchOpen(false); setIsAdmitModalOpen(true); } },
    { label: 'Emergency Triage Intake (ER)', action: () => { setIsSearchOpen(false); setIsEmergencyModalOpen(true); } },
    { label: 'Book OPD Appointment', action: () => { setIsSearchOpen(false); setIsNewAppointmentModalOpen(true); } },
    { label: 'Generate Patient Invoice', action: () => { setIsSearchOpen(false); setIsNewInvoiceModalOpen(true); } },
    { label: 'View Bed & Ward Allocation', action: () => { setIsSearchOpen(false); setActiveTab('beds'); } },
    { label: 'View Pharmacy Formulary', action: () => { setIsSearchOpen(false); setActiveTab('pharmacy-labs'); } }
  ].filter(a => !query.trim() || a.label.toLowerCase().includes(query.toLowerCase()));

  return (
    <div className="fixed inset-0 z-50 flex items-start justify-center pt-12 sm:pt-20 p-3 sm:p-4 bg-slate-900/50 backdrop-blur-xs">
      <div className="bg-white rounded-xl border border-slate-200 shadow-2xl w-full max-w-xl overflow-hidden animate-in fade-in zoom-in-95 duration-100">
        
        {/* Search Input Bar */}
        <div className="flex items-center gap-3 px-4 py-3 border-b border-slate-200 bg-slate-50/50">
          <Search className="w-4 h-4 text-slate-400 shrink-0" />
          <input
            ref={inputRef}
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Type patient name, MRN (e.g. HSP-4109), doctor, bed or action..."
            className="w-full bg-transparent text-xs text-slate-900 placeholder:text-slate-400 focus:outline-hidden"
          />
          <kbd className="text-[10px] font-mono text-slate-400 bg-white border border-slate-200 px-1.5 py-0.5 rounded shrink-0">
            ESC
          </kbd>
        </div>

        {/* Results Container */}
        <div className="max-h-80 overflow-y-auto p-2 divide-y divide-slate-100 text-xs">
          
          {/* Matched Patients */}
          {matchedPatients.length > 0 && (
            <div className="py-2">
              <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider px-2 block mb-1">
                Patients Found ({matchedPatients.length})
              </span>
              {matchedPatients.map(p => (
                <div
                  key={p.id}
                  onClick={() => {
                    setSelectedPatientId(p.id);
                    setIsSearchOpen(false);
                  }}
                  className="px-2.5 py-2 hover:bg-slate-50 rounded-md cursor-pointer flex items-center justify-between text-xs"
                >
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="font-semibold text-slate-900">{p.name}</span>
                      <span className="font-mono text-[11px] text-slate-500">{p.mrn}</span>
                      <span className="text-slate-300">·</span>
                      <span className="text-slate-600">{p.ward || 'OPD'}</span>
                    </div>
                    <span className="text-[11px] text-slate-400 block mt-0.5">
                      {p.diagnoses[0] || p.chiefComplaint}
                    </span>
                  </div>
                  <span className="text-[11px] font-medium text-blue-700">Open Chart →</span>
                </div>
              ))}
            </div>
          )}

          {/* Matched Doctors */}
          {matchedDoctors.length > 0 && (
            <div className="py-2">
              <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider px-2 block mb-1">
                Medical Staff
              </span>
              {matchedDoctors.map(d => (
                <div
                  key={d.id}
                  onClick={() => {
                    setActiveTab('doctors');
                    setIsSearchOpen(false);
                  }}
                  className="px-2.5 py-2 hover:bg-slate-50 rounded-md cursor-pointer flex items-center justify-between text-xs"
                >
                  <div>
                    <span className="font-semibold text-slate-900 block">{d.name}</span>
                    <span className="text-[11px] text-slate-500 block">{d.specialty} · {d.department}</span>
                  </div>
                  <span className="text-[11px] font-medium text-slate-600">View Roster →</span>
                </div>
              ))}
            </div>
          )}

          {/* Matched Beds */}
          {matchedBeds.length > 0 && (
            <div className="py-2">
              <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider px-2 block mb-1">
                Ward Beds
              </span>
              {matchedBeds.map(b => (
                <div
                  key={b.id}
                  onClick={() => {
                    setActiveTab('beds');
                    setIsSearchOpen(false);
                  }}
                  className="px-2.5 py-2 hover:bg-slate-50 rounded-md cursor-pointer flex items-center justify-between text-xs"
                >
                  <div>
                    <span className="font-mono font-bold text-slate-900">{b.code}</span>
                    <span className="text-[11px] text-slate-500 ml-2">{b.ward} · {b.status}</span>
                  </div>
                  <span className="text-[11px] font-medium text-slate-600">View Bed →</span>
                </div>
              ))}
            </div>
          )}

          {/* Quick Actions */}
          <div className="py-2">
            <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider px-2 block mb-1">
              Quick Clinical Workflows
            </span>
            {quickActions.map((action, idx) => (
              <div
                key={idx}
                onClick={action.action}
                className="px-2.5 py-2 hover:bg-slate-50 rounded-md cursor-pointer flex items-center justify-between text-xs text-slate-700"
              >
                <span>{action.label}</span>
                <span className="text-slate-400">↵</span>
              </div>
            ))}
          </div>

        </div>

        {/* Footer */}
        <div className="px-4 py-2 bg-slate-50 border-t border-slate-100 flex items-center justify-between text-[11px] text-slate-400">
          <span>Search patients, MRN, beds, doctors, and actions</span>
          <span>Press ESC to close</span>
        </div>
      </div>
    </div>
  );
};
