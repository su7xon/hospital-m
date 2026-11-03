import React, { useState } from 'react';
import { useHospital } from '../context/HospitalContext';
import { Bed, WardType, BedStatus } from '../types/hms';
import {
  BedDouble,
  CheckCircle2,
  Sparkles,
  Wrench,
  User,
  Plus,
  RefreshCw,
  ArrowRightLeft
} from 'lucide-react';

export const BedAllocationView: React.FC = () => {
  const {
    beds,
    patients,
    updateBedStatus,
    setSelectedPatientId,
    setIsAdmitModalOpen,
    showToast
  } = useHospital();

  const [selectedWard, setSelectedWard] = useState<string>('All');
  const [selectedStatus, setSelectedStatus] = useState<string>('All');

  // Filter beds
  const filteredBeds = beds.filter(bed => {
    const matchesWard = selectedWard === 'All' || bed.ward === selectedWard;
    const matchesStatus = selectedStatus === 'All' || bed.status === selectedStatus;
    return matchesWard && matchesStatus;
  });

  const totalBeds = beds.length;
  const occupiedBeds = beds.filter(b => b.status === 'Occupied').length;
  const availableBeds = beds.filter(b => b.status === 'Available').length;
  const cleaningBeds = beds.filter(b => b.status === 'Cleaning').length;
  const maintenanceBeds = beds.filter(b => b.status === 'Maintenance').length;

  const wardsList: { name: string; ward: string }[] = [
    { name: 'All Wards', ward: 'All' },
    { name: 'ICU (Intensive Care)', ward: 'ICU' },
    { name: 'General Ward A (Male)', ward: 'General Ward A' },
    { name: 'General Ward B (Female)', ward: 'General Ward B' },
    { name: 'Private Suites', ward: 'Private Suite' },
    { name: 'Emergency Care', ward: 'Emergency Care' }
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 pb-2 border-b border-slate-200">
        <div>
          <h1 className="text-xl font-bold text-slate-900 tracking-tight">
            Bed & Ward Allocation Management
          </h1>
          <p className="text-xs text-slate-500 mt-0.5">
            Live inpatient bed inventory, floor sanitization cycle, and occupancy status.
          </p>
        </div>

        <button
          onClick={() => setIsAdmitModalOpen(true)}
          className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold text-white bg-slate-900 hover:bg-slate-800 rounded-md transition-colors self-start sm:self-auto shadow-xs"
        >
          <Plus className="w-3.5 h-3.5" />
          <span>Admit Patient to Bed</span>
        </button>
      </div>

      {/* Stats row */}
      <div className="grid grid-cols-2 sm:grid-cols-5 gap-3">
        <div className="bg-white p-3.5 rounded-lg border border-slate-200 shadow-2xs">
          <span className="text-xs font-medium text-slate-500 block">Total Hospital Beds</span>
          <span className="text-xl font-bold font-mono text-slate-900 tabular-nums block mt-1">
            {totalBeds}
          </span>
          <span className="text-[11px] text-slate-400 mt-1 block">Operational capacity</span>
        </div>

        <div className="bg-white p-3.5 rounded-lg border border-slate-200 shadow-2xs">
          <span className="text-xs font-medium text-slate-500 block">Occupied Beds</span>
          <span className="text-xl font-bold font-mono text-slate-900 tabular-nums block mt-1">
            {occupiedBeds}
          </span>
          <span className="text-[11px] text-slate-500 mt-1 block">
            {Math.round((occupiedBeds / totalBeds) * 100)}% occupancy rate
          </span>
        </div>

        <div className="bg-white p-3.5 rounded-lg border border-slate-200 shadow-2xs">
          <span className="text-xs font-medium text-slate-500 block">Available (Ready)</span>
          <span className="text-xl font-bold font-mono text-emerald-700 tabular-nums block mt-1">
            {availableBeds}
          </span>
          <span className="text-[11px] text-emerald-600 mt-1 block">Immediate intake ready</span>
        </div>

        <div className="bg-white p-3.5 rounded-lg border border-slate-200 shadow-2xs">
          <span className="text-xs font-medium text-slate-500 block">Disinfection / Cleaning</span>
          <span className="text-xl font-bold font-mono text-amber-700 tabular-nums block mt-1">
            {cleaningBeds}
          </span>
          <span className="text-[11px] text-amber-600 mt-1 block">Sanitization in progress</span>
        </div>

        <div className="bg-white p-3.5 rounded-lg border border-slate-200 shadow-2xs">
          <span className="text-xs font-medium text-slate-500 block">Maintenance</span>
          <span className="text-xl font-bold font-mono text-slate-600 tabular-nums block mt-1">
            {maintenanceBeds}
          </span>
          <span className="text-[11px] text-slate-400 mt-1 block">Biomedical repair</span>
        </div>
      </div>

      {/* Ward & Status Segmented Filters */}
      <div className="bg-white p-3 rounded-lg border border-slate-200 shadow-2xs space-y-2.5">
        {/* Ward tabs - horizontally swipeable on mobile */}
        <div className="flex items-center gap-1.5 overflow-x-auto scrollbar-none pb-0.5 touch-pan-x">
          {wardsList.map(w => {
            const isActive = selectedWard === w.ward;
            const count = w.ward === 'All'
              ? beds.length
              : beds.filter(b => b.ward === w.ward).length;

            return (
              <button
                key={w.ward}
                onClick={() => setSelectedWard(w.ward)}
                className={`px-3 py-1.5 text-xs font-medium rounded-md transition-colors whitespace-nowrap shrink-0 flex items-center gap-1.5 ${
                  isActive
                    ? 'bg-slate-900 text-white shadow-2xs'
                    : 'text-slate-600 hover:bg-slate-100'
                }`}
              >
                <span>{w.name}</span>
                <span className={`text-[10px] font-mono tabular-nums ${isActive ? 'text-slate-300' : 'text-slate-400'}`}>
                  {count}
                </span>
              </button>
            );
          })}
        </div>

        {/* Status filter bar - horizontally swipeable on mobile */}
        <div className="flex items-center gap-1 pt-2 border-t border-slate-100 text-xs text-slate-500 overflow-x-auto scrollbar-none pb-0.5 touch-pan-x">
          <span className="mr-2 shrink-0">Status:</span>
          {['All', 'Available', 'Occupied', 'Cleaning', 'Maintenance'].map(st => {
            const isActive = selectedStatus === st;
            return (
              <button
                key={st}
                onClick={() => setSelectedStatus(st)}
                className={`px-2.5 py-1 text-xs font-medium rounded transition-colors whitespace-nowrap shrink-0 ${
                  isActive
                    ? 'bg-slate-200 text-slate-900 font-semibold'
                    : 'text-slate-600 hover:bg-slate-100'
                }`}
              >
                {st}
              </button>
            );
          })}
        </div>
      </div>

      {/* Bed Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
        {filteredBeds.map(bed => {
          const isOccupied = bed.status === 'Occupied';
          const isCleaning = bed.status === 'Cleaning';
          const isMaintenance = bed.status === 'Maintenance';
          const isAvailable = bed.status === 'Available';

          return (
            <div
              key={bed.id}
              className={`rounded-lg border p-4 bg-white shadow-2xs flex flex-col justify-between transition-all ${
                isOccupied
                  ? 'border-slate-300'
                  : isCleaning
                  ? 'border-amber-200 bg-amber-50/20'
                  : isMaintenance
                  ? 'border-slate-200 opacity-75'
                  : 'border-slate-200 hover:border-slate-400'
              }`}
            >
              <div>
                {/* Bed Header */}
                <div className="flex items-start justify-between">
                  <div>
                    <span className="font-mono text-base font-bold text-slate-900 block">
                      {bed.code}
                    </span>
                    <span className="text-[11px] text-slate-500 block">
                      {bed.ward} · {bed.floor}
                    </span>
                  </div>

                  <span className={`text-xs font-semibold ${
                    isOccupied
                      ? 'text-slate-900'
                      : isAvailable
                      ? 'text-emerald-700'
                      : isCleaning
                      ? 'text-amber-700'
                      : 'text-slate-500'
                  }`}>
                    {bed.status}
                  </span>
                </div>

                {/* Rate */}
                <div className="mt-2 text-xs text-slate-500 font-mono">
                  Rate: ₹{bed.dailyRate.toLocaleString('en-IN')}/day
                </div>

                {/* Patient details if occupied */}
                {isOccupied && (
                  <div className="mt-3 pt-3 border-t border-slate-100">
                    <span className="text-[11px] text-slate-400 uppercase font-semibold block">
                      Admitted Patient
                    </span>
                    <span
                      onClick={() => {
                        if (bed.patientId) setSelectedPatientId(bed.patientId);
                      }}
                      className="text-xs font-bold text-slate-900 hover:text-blue-700 cursor-pointer block mt-0.5"
                    >
                      {bed.patientName}
                    </span>
                    <div className="flex items-center gap-2 text-[11px] text-slate-500 font-mono mt-0.5">
                      <span>{bed.patientMrn}</span>
                      <span className="text-slate-300">·</span>
                      <span>Since {bed.admittedSince}</span>
                    </div>
                  </div>
                )}

                {/* Cleaning state */}
                {isCleaning && (
                  <div className="mt-3 pt-3 border-t border-amber-100 text-xs text-amber-800">
                    Bed stripped & awaiting housekeeping sterilization.
                  </div>
                )}
              </div>

              {/* Action buttons on card */}
              <div className="mt-4 pt-3 border-t border-slate-100 flex items-center justify-between gap-2 text-xs">
                {isAvailable && (
                  <button
                    onClick={() => setIsAdmitModalOpen(true)}
                    className="w-full py-1.5 px-2 font-semibold text-slate-900 bg-slate-100 hover:bg-slate-200 rounded text-center transition-colors"
                  >
                    + Assign Patient
                  </button>
                )}

                {isOccupied && (
                  <div className="flex items-center justify-between w-full gap-2">
                    <button
                      onClick={() => {
                        if (bed.patientId) setSelectedPatientId(bed.patientId);
                      }}
                      className="px-2.5 py-1 font-medium text-slate-700 bg-slate-100 hover:bg-slate-200 rounded text-xs transition-colors"
                    >
                      Chart
                    </button>
                    <button
                      onClick={() => {
                        if (window.confirm(`Release Bed ${bed.code} to Cleaning?`)) {
                          updateBedStatus(bed.id, 'Cleaning');
                        }
                      }}
                      className="px-2.5 py-1 font-medium text-rose-700 hover:bg-rose-50 rounded text-xs transition-colors"
                    >
                      Release Bed
                    </button>
                  </div>
                )}

                {isCleaning && (
                  <button
                    onClick={() => updateBedStatus(bed.id, 'Available')}
                    className="w-full py-1.5 px-2 font-semibold text-emerald-800 bg-emerald-50 hover:bg-emerald-100 border border-emerald-200 rounded text-center transition-colors"
                  >
                    Mark Cleaned & Ready
                  </button>
                )}

                {isMaintenance && (
                  <button
                    onClick={() => updateBedStatus(bed.id, 'Available')}
                    className="w-full py-1.5 px-2 font-semibold text-slate-700 bg-slate-100 hover:bg-slate-200 rounded text-center transition-colors"
                  >
                    Set Operational
                  </button>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
