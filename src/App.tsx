/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React from 'react';
import { HospitalProvider, useHospital } from './context/HospitalContext';
import { Header } from './components/Header';
import { OverviewView } from './components/OverviewView';
import { PatientsView } from './components/PatientsView';
import { BedAllocationView } from './components/BedAllocationView';
import { AppointmentsView } from './components/AppointmentsView';
import { PharmacyLabsView } from './components/PharmacyLabsView';
import { BillingView } from './components/BillingView';
import { DoctorsView } from './components/DoctorsView';
import { PatientDetailModal } from './components/PatientDetailModal';
import { AdmitPatientModal } from './components/AdmitPatientModal';
import { EmergencyModal } from './components/EmergencyModal';
import { BookAppointmentModal } from './components/BookAppointmentModal';
import { CommandPaletteModal } from './components/CommandPaletteModal';

const HospitalAppContent: React.FC = () => {
  const { activeTab, toastMessage } = useHospital();

  return (
    <div className="min-h-screen flex flex-col bg-slate-50 text-slate-900 w-full overflow-x-hidden">
      {/* Top Navigation Bar */}
      <Header />

      {/* Main Content Viewport */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-3 sm:px-6 lg:px-8 py-4 sm:py-6">
        {activeTab === 'overview' && <OverviewView />}
        {activeTab === 'patients' && <PatientsView />}
        {activeTab === 'beds' && <BedAllocationView />}
        {activeTab === 'appointments' && <AppointmentsView />}
        {activeTab === 'pharmacy-labs' && <PharmacyLabsView />}
        {activeTab === 'billing' && <BillingView />}
        {activeTab === 'doctors' && <DoctorsView />}
      </main>

      {/* Clean Hospital Footer */}
      <footer className="no-print mt-auto border-t border-slate-200 bg-white py-4 sm:py-6">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col sm:flex-row items-center justify-between gap-3 text-center sm:text-left text-xs text-slate-500">
          <div className="flex flex-wrap items-center justify-center sm:justify-start gap-2 sm:gap-3">
            <span className="font-bold text-slate-800">Aegis Health</span>
            <span className="text-slate-300 hidden sm:inline" aria-hidden="true">·</span>
            <span>Metro General Hospital</span>
            <span className="text-slate-300 hidden sm:inline" aria-hidden="true">·</span>
            <span className="font-mono text-[11px] text-slate-400">NABH & JCI Accredited</span>
          </div>

          <div className="flex flex-wrap items-center justify-center sm:justify-end gap-2 sm:gap-4 text-xs">
            <span>Clinical Desk</span>
            <span className="text-slate-300" aria-hidden="true">·</span>
            <span className="font-mono text-[11px]">Hotline: 1066 / +91 22 2490 0000</span>
          </div>
        </div>
      </footer>

      {/* Interactive Modals */}
      <PatientDetailModal />
      <AdmitPatientModal />
      <EmergencyModal />
      <BookAppointmentModal />
      <CommandPaletteModal />

      {/* Clinical Action Toast Notification */}
      {toastMessage && (
        <div className="fixed bottom-6 right-6 z-50 bg-slate-900 text-white text-xs px-4 py-2.5 rounded-lg shadow-lg border border-slate-800 flex items-center gap-2 animate-in fade-in slide-in-from-bottom-2 duration-150">
          <span className="w-2 h-2 rounded-full bg-emerald-400 shrink-0" />
          <span>{toastMessage}</span>
        </div>
      )}
    </div>
  );
};

export default function App() {
  return (
    <HospitalProvider>
      <HospitalAppContent />
    </HospitalProvider>
  );
}
