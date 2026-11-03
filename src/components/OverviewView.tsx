import React from 'react';
import { useHospital } from '../context/HospitalContext';
import {
  Users,
  BedDouble,
  AlertTriangle,
  Calendar,
  Stethoscope,
  ArrowUpRight,
  Plus,
  ShieldCheck,
  CheckCircle2,
  Clock,
  FlaskConical,
  Package
} from 'lucide-react';

export const OverviewView: React.FC = () => {
  const {
    patients,
    beds,
    emergencyCases,
    appointments,
    doctors,
    medicines,
    labOrders,
    setActiveTab,
    setIsAdmitModalOpen,
    setIsEmergencyModalOpen,
    setIsNewAppointmentModalOpen,
    setSelectedPatientId,
    updateAppointmentStatus,
    updateEmergencyStatus,
    convertEmergencyToAdmission
  } = useHospital();

  // Metrics calculation
  const admittedPatients = patients.filter(p => p.status === 'Admitted' || p.status === 'ICU');
  const icuPatients = patients.filter(p => p.status === 'ICU');
  const totalBeds = beds.length;
  const occupiedBeds = beds.filter(b => b.status === 'Occupied').length;
  const availableBeds = beds.filter(b => b.status === 'Available').length;
  const cleaningBeds = beds.filter(b => b.status === 'Cleaning').length;
  const occupancyPercentage = Math.round((occupiedBeds / totalBeds) * 100);

  const activeER = emergencyCases.filter(e => e.status === 'Waiting' || e.status === 'In Treatment');
  const todayAppointments = appointments.filter(a => a.date === '2026-10-20' || a.date === new Date().toISOString().substring(0, 10));
  const completedAppointments = todayAppointments.filter(a => a.status === 'Completed').length;
  const doctorsOnDuty = doctors.filter(d => d.onDuty).length;

  const lowStockMeds = medicines.filter(m => m.stock <= m.minStock);
  const pendingStatLabs = labOrders.filter(l => l.priority === 'STAT Urgent' && l.status !== 'Completed');

  return (
    <div className="space-y-6">
      {/* Top Banner / Welcome & Quick Actions */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 pb-2 border-b border-slate-200">
        <div>
          <h1 className="text-xl font-bold text-slate-900 tracking-tight">
            Clinical Operations Center
          </h1>
          <p className="text-xs text-slate-500 mt-0.5">
            Real-time floor occupancy, emergency triage, OPD rosters, and ward status.
          </p>
        </div>
        <div className="flex flex-wrap items-center gap-1.5 sm:gap-2 w-full sm:w-auto">
          <button
            onClick={() => setIsEmergencyModalOpen(true)}
            className="flex-1 sm:flex-initial text-center px-2.5 sm:px-3 py-1.5 text-xs font-semibold text-rose-700 bg-rose-50 hover:bg-rose-100 border border-rose-200 rounded-md transition-colors whitespace-nowrap shadow-2xs"
          >
            + Log ER
          </button>
          <button
            onClick={() => setIsNewAppointmentModalOpen(true)}
            className="flex-1 sm:flex-initial text-center px-2.5 sm:px-3 py-1.5 text-xs font-semibold text-slate-700 bg-white hover:bg-slate-50 border border-slate-200 rounded-md transition-colors whitespace-nowrap shadow-2xs"
          >
            + Book OPD
          </button>
          <button
            onClick={() => setIsAdmitModalOpen(true)}
            className="flex-1 sm:flex-initial text-center px-2.5 sm:px-3 py-1.5 text-xs font-semibold text-white bg-slate-900 hover:bg-slate-800 rounded-md transition-colors whitespace-nowrap shadow-xs"
          >
            + Admit Patient
          </button>
        </div>
      </div>

      {/* KPI Stats Strip */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-2 sm:gap-3">
        {/* Total Inpatient Census */}
        <div className="bg-white p-3 sm:p-4 rounded-lg border border-slate-200 shadow-2xs">
          <span className="text-[11px] sm:text-xs font-medium text-slate-500 block">Admitted Census</span>
          <div className="mt-1 flex flex-wrap items-baseline gap-1.5 sm:gap-2">
            <span className="text-xl sm:text-2xl font-bold text-slate-900 font-mono tabular-nums">
              {admittedPatients.length}
            </span>
            <span className="text-[11px] sm:text-xs text-slate-500">
              ({icuPatients.length} ICU)
            </span>
          </div>
          <span className="text-[10px] sm:text-[11px] text-slate-400 mt-1.5 block">
            Active inpatients
          </span>
        </div>

        {/* Bed Occupancy */}
        <div className="bg-white p-3 sm:p-4 rounded-lg border border-slate-200 shadow-2xs">
          <span className="text-[11px] sm:text-xs font-medium text-slate-500 block">Bed Occupancy</span>
          <div className="mt-1 flex flex-wrap items-baseline gap-1.5 sm:gap-2">
            <span className="text-xl sm:text-2xl font-bold text-slate-900 font-mono tabular-nums">
              {occupancyPercentage}%
            </span>
            <span className="text-[11px] sm:text-xs text-slate-500">
              {occupiedBeds}/{totalBeds}
            </span>
          </div>
          <span className="text-[10px] sm:text-[11px] text-emerald-600 mt-1.5 block">
            {availableBeds} beds free
          </span>
        </div>

        {/* Emergency Active */}
        <div className={`p-3 sm:p-4 rounded-lg border shadow-2xs ${
          activeER.length > 0 ? 'bg-rose-50/40 border-rose-200' : 'bg-white border-slate-200'
        }`}>
          <span className="text-[11px] sm:text-xs font-medium text-slate-600 block">ER Triage Queue</span>
          <div className="mt-1 flex flex-wrap items-baseline gap-1.5 sm:gap-2">
            <span className="text-xl sm:text-2xl font-bold text-rose-700 font-mono tabular-nums">
              {activeER.length}
            </span>
            <span className="text-[11px] sm:text-xs text-slate-500">active</span>
          </div>
          <span className="text-[10px] sm:text-[11px] text-rose-600 mt-1.5 block truncate">
            {emergencyCases.filter(e => e.triageLevel.startsWith('P1') && e.status !== 'Discharged').length} Critical P1
          </span>
        </div>

        {/* Today's OPD */}
        <div className="bg-white p-3 sm:p-4 rounded-lg border border-slate-200 shadow-2xs">
          <span className="text-[11px] sm:text-xs font-medium text-slate-500 block">Today's OPD</span>
          <div className="mt-1 flex flex-wrap items-baseline gap-1.5 sm:gap-2">
            <span className="text-xl sm:text-2xl font-bold text-slate-900 font-mono tabular-nums">
              {todayAppointments.length}
            </span>
            <span className="text-[11px] sm:text-xs text-slate-500">sched</span>
          </div>
          <span className="text-[10px] sm:text-[11px] text-slate-500 mt-1.5 block">
            {completedAppointments} completed
          </span>
        </div>

        {/* Doctors on Duty */}
        <div className="bg-white p-3 sm:p-4 rounded-lg border border-slate-200 shadow-2xs">
          <span className="text-[11px] sm:text-xs font-medium text-slate-500 block">Doctors on Floor</span>
          <div className="mt-1 flex flex-wrap items-baseline gap-1.5 sm:gap-2">
            <span className="text-xl sm:text-2xl font-bold text-slate-900 font-mono tabular-nums">
              {doctorsOnDuty}
            </span>
            <span className="text-[11px] sm:text-xs text-slate-500">of {doctors.length}</span>
          </div>
          <span className="text-[10px] sm:text-[11px] text-slate-400 mt-1.5 block">
            Roster nominal
          </span>
        </div>

        {/* Formulary Stock Alerts */}
        <div className={`p-3 sm:p-4 rounded-lg border shadow-2xs ${
          lowStockMeds.length > 0 ? 'bg-amber-50/40 border-amber-200' : 'bg-white border-slate-200'
        }`}>
          <span className="text-[11px] sm:text-xs font-medium text-slate-600 block">Pharmacy Alerts</span>
          <div className="mt-1 flex flex-wrap items-baseline gap-1.5 sm:gap-2">
            <span className={`text-xl sm:text-2xl font-bold font-mono tabular-nums ${
              lowStockMeds.length > 0 ? 'text-amber-700' : 'text-slate-900'
            }`}>
              {lowStockMeds.length}
            </span>
            <span className="text-[11px] sm:text-xs text-slate-500">low stock</span>
          </div>
          <span className="text-[10px] sm:text-[11px] text-slate-500 mt-1.5 block truncate">
            {pendingStatLabs.length} STAT labs
          </span>
        </div>
      </div>

      {/* Main Grid: ER & Ward Status */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* Left 2 Cols: Emergency Triage Department */}
        <div className="lg:col-span-2 bg-white rounded-lg border border-slate-200 shadow-2xs p-5">
          <div className="flex items-center justify-between pb-3 border-b border-slate-100">
            <div>
              <h2 className="text-sm font-bold text-slate-900">
                Emergency Triage Department (ER)
              </h2>
              <span className="text-xs text-slate-500">
                Prioritized according to Manchester Triage System (P1–P5)
              </span>
            </div>
            <button
              onClick={() => setIsEmergencyModalOpen(true)}
              className="text-xs font-semibold text-slate-700 hover:text-slate-900 flex items-center gap-1"
            >
              <span>Log Patient</span>
              <Plus className="w-3.5 h-3.5" />
            </button>
          </div>

          <div className="mt-4 divide-y divide-slate-100">
            {emergencyCases.length === 0 ? (
              <div className="py-8 text-center text-xs text-slate-400">
                No active emergency cases in triage.
              </div>
            ) : (
              emergencyCases.map(item => {
                const isP1 = item.triageLevel.startsWith('P1');
                const isP2 = item.triageLevel.startsWith('P2');
                return (
                  <div key={item.id} className="py-3.5 first:pt-0 last:pb-0 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                    <div className="min-w-0">
                      <div className="flex items-center gap-2">
                        <span className={`text-xs font-bold ${
                          isP1 ? 'text-rose-700' : isP2 ? 'text-amber-700' : 'text-slate-800'
                        }`}>
                          {item.triageLevel}
                        </span>
                        <span className="text-slate-300" aria-hidden="true">·</span>
                        <span className="text-xs font-semibold text-slate-900">
                          {item.patientName} ({item.age}y/{item.gender.charAt(0)})
                        </span>
                        <span className="text-slate-300" aria-hidden="true">·</span>
                        <span className="text-xs font-mono text-slate-500">
                          Arr: {item.arrivalTime}
                        </span>
                      </div>
                      <p className="text-xs text-slate-600 mt-1 line-clamp-1">
                        {item.chiefComplaint}
                      </p>
                      <div className="flex items-center gap-3 mt-1.5 text-[11px] text-slate-500 font-mono">
                        <span>{item.vitalsBrief}</span>
                        <span className="text-slate-300" aria-hidden="true">·</span>
                        <span className="font-sans text-slate-600">{item.assignedDoctor}</span>
                      </div>
                    </div>

                    {/* Actions */}
                    <div className="flex items-center justify-between sm:justify-end gap-2 w-full sm:w-auto shrink-0 pt-2 sm:pt-0 border-t sm:border-t-0 border-slate-100">
                      <select
                        value={item.status}
                        onChange={(e) => updateEmergencyStatus(item.id, e.target.value as any)}
                        className="text-xs font-medium bg-slate-50 border border-slate-200 rounded px-2 py-1 text-slate-700 focus:outline-hidden focus:border-slate-400"
                      >
                        <option value="Waiting">Waiting</option>
                        <option value="In Treatment">In Treatment</option>
                        <option value="Admitted">Admitted</option>
                        <option value="Discharged">Discharged</option>
                      </select>

                      {item.status !== 'Admitted' && item.status !== 'Discharged' && (
                        <button
                          onClick={() => {
                            // Find first available bed
                            const freeBed = beds.find(b => b.status === 'Available');
                            const doc = doctors.find(d => d.onDuty);
                            if (freeBed && doc) {
                              convertEmergencyToAdmission(item.id, freeBed.id, doc.id);
                            } else {
                              setIsAdmitModalOpen(true);
                            }
                          }}
                          className="px-2.5 py-1 text-xs font-semibold text-slate-800 bg-slate-100 hover:bg-slate-200 border border-slate-200 rounded transition-colors whitespace-nowrap"
                        >
                          Admit to Bed
                        </button>
                      )}
                    </div>
                  </div>
                );
              })
            )}
          </div>
        </div>

        {/* Right 1 Col: Ward Occupancy Snapshot */}
        <div className="bg-white rounded-lg border border-slate-200 shadow-2xs p-5">
          <div className="flex items-center justify-between pb-3 border-b border-slate-100">
            <h2 className="text-sm font-bold text-slate-900">
              Ward Occupancy
            </h2>
            <button
              onClick={() => setActiveTab('beds')}
              className="text-xs font-semibold text-slate-600 hover:text-slate-900 flex items-center gap-1"
            >
              <span>Manage</span>
              <ArrowUpRight className="w-3.5 h-3.5" />
            </button>
          </div>

          <div className="mt-4 space-y-3.5">
            {[
              { name: 'ICU (Intensive Care)', ward: 'ICU' },
              { name: 'General Ward A (Male)', ward: 'General Ward A' },
              { name: 'General Ward B (Female)', ward: 'General Ward B' },
              { name: 'Private Suites', ward: 'Private Suite' },
              { name: 'Emergency Care Bay', ward: 'Emergency Care' }
            ].map(w => {
              const wardBeds = beds.filter(b => b.ward === w.ward);
              const total = wardBeds.length;
              const occ = wardBeds.filter(b => b.status === 'Occupied').length;
              const avail = wardBeds.filter(b => b.status === 'Available').length;
              const clean = wardBeds.filter(b => b.status === 'Cleaning').length;
              const pct = total > 0 ? Math.round((occ / total) * 100) : 0;

              return (
                <div key={w.ward} className="space-y-1.5">
                  <div className="flex items-center justify-between text-xs">
                    <span className="font-semibold text-slate-800">{w.name}</span>
                    <span className="font-mono tabular-nums text-slate-500">
                      {occ}/{total} beds ({pct}%)
                    </span>
                  </div>
                  <div className="w-full h-2 bg-slate-100 rounded-full overflow-hidden flex">
                    <div
                      className="h-full bg-slate-800 transition-all duration-300"
                      style={{ width: `${pct}%` }}
                    />
                    {clean > 0 && (
                      <div
                        className="h-full bg-amber-400 transition-all duration-300"
                        style={{ width: `${(clean / total) * 100}%` }}
                        title={`${clean} beds cleaning`}
                      />
                    )}
                  </div>
                  <div className="flex items-center justify-between text-[11px] text-slate-400">
                    <span>{avail} Available</span>
                    {clean > 0 && <span className="text-amber-600">{clean} Cleaning</span>}
                  </div>
                </div>
              );
            })}
          </div>

          <div className="mt-5 pt-4 border-t border-slate-100 flex items-center justify-between text-xs text-slate-500">
            <span>Hospital Bed Capacity</span>
            <span className="font-mono font-semibold text-slate-800">{occupiedBeds} occupied / {availableBeds} free</span>
          </div>
        </div>

      </div>

      {/* Bottom Grid: Today's Appointments & Admitted Patients Quick Table */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        
        {/* Today's Appointments */}
        <div className="bg-white rounded-lg border border-slate-200 shadow-2xs p-5">
          <div className="flex items-center justify-between pb-3 border-b border-slate-100">
            <div>
              <h2 className="text-sm font-bold text-slate-900">
                Today's Outpatient Clinic (OPD)
              </h2>
              <span className="text-xs text-slate-500">
                Consultation queue & doctor assignments
              </span>
            </div>
            <button
              onClick={() => setActiveTab('appointments')}
              className="text-xs font-semibold text-slate-600 hover:text-slate-900 flex items-center gap-1"
            >
              <span>View Roster</span>
              <ArrowUpRight className="w-3.5 h-3.5" />
            </button>
          </div>

          <div className="mt-3 divide-y divide-slate-100">
            {todayAppointments.slice(0, 5).map(apt => (
              <div key={apt.id} className="py-2.5 flex items-center justify-between gap-3 text-xs">
                <div>
                  <div className="flex items-center gap-2">
                    <span className="font-semibold text-slate-900">{apt.patientName}</span>
                    <span className="text-slate-300">·</span>
                    <span className="font-mono text-slate-500">{apt.timeSlot}</span>
                    <span className="text-slate-300">·</span>
                    <span className="text-slate-500">{apt.type}</span>
                  </div>
                  <p className="text-[11px] text-slate-500 mt-0.5">
                    {apt.doctorName} ({apt.department})
                  </p>
                </div>
                <select
                  value={apt.status}
                  onChange={(e) => updateAppointmentStatus(apt.id, e.target.value as any)}
                  className="text-xs font-medium bg-slate-50 border border-slate-200 rounded px-2 py-1 text-slate-700"
                >
                  <option value="Scheduled">Scheduled</option>
                  <option value="Checked-in">Checked-in</option>
                  <option value="In Consultation">In Consultation</option>
                  <option value="Completed">Completed</option>
                  <option value="Cancelled">Cancelled</option>
                </select>
              </div>
            ))}
          </div>
        </div>

        {/* Current Inpatient Census Quick Access */}
        <div className="bg-white rounded-lg border border-slate-200 shadow-2xs p-5">
          <div className="flex items-center justify-between pb-3 border-b border-slate-100">
            <div>
              <h2 className="text-sm font-bold text-slate-900">
                Inpatient Census (Active)
              </h2>
              <span className="text-xs text-slate-500">
                Currently admitted patients requiring clinical monitoring
              </span>
            </div>
            <button
              onClick={() => setActiveTab('patients')}
              className="text-xs font-semibold text-slate-600 hover:text-slate-900 flex items-center gap-1"
            >
              <span>Patient Directory</span>
              <ArrowUpRight className="w-3.5 h-3.5" />
            </button>
          </div>

          <div className="mt-3 divide-y divide-slate-100">
            {admittedPatients.slice(0, 5).map(pat => {
              const latestVital = pat.vitals[0];
              return (
                <div
                  key={pat.id}
                  onClick={() => setSelectedPatientId(pat.id)}
                  className="py-2.5 flex items-center justify-between gap-3 text-xs hover:bg-slate-50/80 px-1 -mx-1 rounded cursor-pointer transition-colors"
                >
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="font-semibold text-slate-900">{pat.name}</span>
                      <span className="font-mono text-slate-400">({pat.mrn})</span>
                      <span className="text-slate-300">·</span>
                      <span className="font-medium text-slate-700">{pat.bedNumber || 'No Bed'}</span>
                      <span className="text-slate-300">·</span>
                      <span className="text-slate-500">{pat.ward}</span>
                    </div>
                    <p className="text-[11px] text-slate-500 mt-0.5 line-clamp-1">
                      {pat.diagnoses[0] || pat.chiefComplaint}
                    </p>
                  </div>

                  <div className="text-right shrink-0">
                    {latestVital ? (
                      <div className="font-mono text-[11px] text-slate-600">
                        <span>HR {latestVital.heartRate}</span>
                        <span className="mx-1 text-slate-300">|</span>
                        <span>BP {latestVital.bloodPressure}</span>
                      </div>
                    ) : (
                      <span className="text-[11px] text-slate-400">No vitals</span>
                    )}
                    <span className="text-[10px] text-slate-400 block mt-0.5">
                      {pat.assignedDoctorName}
                    </span>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

      </div>

      {/* Operational Clinical Alerts Footer strip */}
      {(lowStockMeds.length > 0 || pendingStatLabs.length > 0) && (
        <div className="bg-amber-50/60 border border-amber-200 rounded-lg p-3.5 flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-xs">
          <div className="flex items-start sm:items-center gap-2 text-amber-900">
            <AlertTriangle className="w-4 h-4 text-amber-700 shrink-0 mt-0.5 sm:mt-0" />
            <div>
              <span className="font-semibold">Hospital Inventory & Lab Action Needed:</span>
              <span className="ml-1 text-amber-800">
                {lowStockMeds.length > 0 && `${lowStockMeds.map(m => m.name).join(', ')} below minimum threshold.`}
                {pendingStatLabs.length > 0 && ` ${pendingStatLabs.length} STAT Urgent lab requisition awaiting completion.`}
              </span>
            </div>
          </div>
          <button
            onClick={() => setActiveTab('pharmacy-labs')}
            className="px-3 py-1 font-semibold text-amber-900 bg-white hover:bg-amber-100 border border-amber-300 rounded text-xs shrink-0 self-start sm:self-auto transition-colors"
          >
            Review in Pharmacy & Labs
          </button>
        </div>
      )}
    </div>
  );
};
