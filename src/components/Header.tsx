import React, { useState, useEffect } from 'react';
import { useHospital, ActiveTab } from '../context/HospitalContext';
import {
  Search,
  Plus,
  AlertCircle,
  RefreshCw,
  Building2,
  Clock
} from 'lucide-react';

export const Header: React.FC = () => {
  const {
    activeTab,
    setActiveTab,
    setIsSearchOpen,
    setIsAdmitModalOpen,
    setIsEmergencyModalOpen,
    emergencyCases,
    resetAllData
  } = useHospital();

  const [currentTime, setCurrentTime] = useState('');

  useEffect(() => {
    const updateTime = () => {
      const now = new Date();
      setCurrentTime(
        now.toLocaleTimeString('en-US', {
          hour: '2-digit',
          minute: '2-digit',
          second: '2-digit',
          hour12: false
        })
      );
    };
    updateTime();
    const interval = setInterval(updateTime, 1000);
    return () => clearInterval(interval);
  }, []);

  const navItems: { id: ActiveTab; label: string; shortLabel?: string }[] = [
    { id: 'overview', label: 'Overview' },
    { id: 'patients', label: 'Patients' },
    { id: 'beds', label: 'Bed Allocation', shortLabel: 'Beds' },
    { id: 'appointments', label: 'Appointments' },
    { id: 'pharmacy-labs', label: 'Pharmacy & Labs', shortLabel: 'Pharmacy' },
    { id: 'billing', label: 'Billing' },
    { id: 'doctors', label: 'Medical Staff', shortLabel: 'Staff' }
  ];

  const activeERCount = emergencyCases.filter(e => e.status === 'Waiting' || e.status === 'In Treatment').length;

  return (
    <header className="sticky top-0 z-40 bg-white border-b border-slate-200 w-full">
      {/* Top Bar Container - Perfectly balanced across screen widths without overflow */}
      <div className="max-w-7xl mx-auto px-3 sm:px-4 lg:px-6">
        <div className="flex items-center justify-between gap-2 lg:gap-3 xl:gap-4 h-16">
          
          {/* Zone 1: Brand Wordmark */}
          <div className="flex items-center gap-2 shrink-0">
            <button
              onClick={() => setActiveTab('overview')}
              className="flex items-center gap-2 text-left group focus:outline-hidden"
            >
              <div className="w-8 h-8 rounded-lg bg-slate-900 text-white flex items-center justify-center font-bold text-sm tracking-wider shadow-xs">
                <span className="text-emerald-400 font-mono text-base font-semibold">+</span>
              </div>
              <div>
                <span className="text-sm sm:text-base font-bold text-slate-900 tracking-tight block leading-tight">
                  Aegis Health
                </span>
                <span className="text-[10px] sm:text-[11px] text-slate-500 font-medium hidden md:block leading-tight">
                  Clinical Operations
                </span>
              </div>
            </button>
          </div>

          {/* Zone 2: Navigation Links with quiet underlines */}
          <nav className="hidden lg:flex items-center gap-0.5 xl:gap-1.5 min-w-0">
            {navItems.map(item => {
              const isActive = activeTab === item.id;
              return (
                <button
                  key={item.id}
                  onClick={() => setActiveTab(item.id)}
                  className={`px-2 xl:px-2.5 py-1.5 text-xs xl:text-sm font-medium transition-colors whitespace-nowrap shrink-0 relative rounded-md ${
                    isActive
                      ? 'text-slate-900 font-semibold'
                      : 'text-slate-600 hover:text-slate-900 hover:bg-slate-50'
                  }`}
                >
                  <span className="hidden xl:inline">{item.label}</span>
                  <span className="xl:hidden inline">{item.shortLabel || item.label}</span>
                  {isActive && (
                    <span className="absolute bottom-0 left-2 right-2 h-0.5 bg-slate-900 rounded-full" />
                  )}
                </button>
              );
            })}
          </nav>

          {/* Zone 3: Search, Emergency Intake & Admit Patient Actions (Always in view) */}
          <div className="flex items-center gap-1 sm:gap-2 shrink-0">
            {/* Quick Search trigger */}
            <button
              onClick={() => setIsSearchOpen(true)}
              className="flex items-center justify-center p-2 sm:px-2.5 sm:py-1.5 text-xs text-slate-500 bg-slate-100 hover:bg-slate-200/80 rounded-md transition-colors border border-slate-200 shrink-0"
              title="Search patients, MRN or records (Cmd+K)"
            >
              <Search className="w-3.5 h-3.5 text-slate-500 shrink-0" />
              <span className="hidden 2xl:inline ml-1.5">Search MRN / Patient</span>
              <span className="hidden md:inline 2xl:hidden ml-1.5">Search</span>
              <kbd className="hidden 2xl:inline-block ml-1 px-1 py-0.2 text-[10px] font-mono bg-white rounded border border-slate-300 text-slate-600">
                ⌘K
              </kbd>
            </button>

            {/* Shift clock (tabular numerals - on ultra wide screens) */}
            <div className="hidden 2xl:flex items-center gap-1.5 px-2 py-1 text-xs text-slate-600 font-mono tabular-nums bg-slate-50 border border-slate-200 rounded-md shrink-0">
              <Clock className="w-3.5 h-3.5 text-slate-400" />
              <span>{currentTime || '08:00:00'}</span>
            </div>

            {/* Emergency Intake Trigger */}
            <button
              onClick={() => setIsEmergencyModalOpen(true)}
              className={`flex items-center gap-1 sm:gap-1.5 px-2 sm:px-2.5 py-1.5 text-xs font-semibold rounded-md transition-colors border shrink-0 ${
                activeERCount > 0
                  ? 'bg-rose-50 border-rose-200 text-rose-700 hover:bg-rose-100 shadow-2xs'
                  : 'bg-slate-100 border-slate-200 text-slate-700 hover:bg-slate-200'
              }`}
              title="Emergency Department Triage Intake"
            >
              <AlertCircle className="w-3.5 h-3.5 text-rose-600 shrink-0" />
              <span className="whitespace-nowrap hidden min-[400px]:inline">ER Intake</span>
              <span className="whitespace-nowrap min-[400px]:hidden">ER</span>
              {activeERCount > 0 && (
                <span className="font-mono text-[10px] sm:text-[11px] font-bold px-1 sm:px-1.5 py-0.2 rounded bg-rose-200/70 text-rose-800">
                  {activeERCount}
                </span>
              )}
            </button>

            {/* Primary Action: Admit Patient */}
            <button
              onClick={() => setIsAdmitModalOpen(true)}
              className="flex items-center gap-1 sm:gap-1.5 px-2 sm:px-3 py-1.5 text-xs font-semibold text-white bg-slate-900 hover:bg-slate-800 rounded-md transition-colors whitespace-nowrap shrink-0 shadow-xs"
              title="Admit new patient to bed"
            >
              <Plus className="w-3.5 h-3.5 shrink-0" />
              <span className="whitespace-nowrap hidden sm:inline">Admit Patient</span>
              <span className="whitespace-nowrap sm:hidden">Admit</span>
            </button>

            {/* Reset Demo Data button */}
            <button
              onClick={() => {
                if (window.confirm('Reset all hospital records to default clinical dataset?')) {
                  resetAllData();
                }
              }}
              className="p-1.5 text-slate-400 hover:text-slate-600 rounded-md transition-colors shrink-0"
              title="Reset verified demo data"
            >
              <RefreshCw className="w-3.5 h-3.5 shrink-0" />
            </button>
          </div>
        </div>

        {/* Mobile / Tablet Nav strip (screens below lg) */}
        <div className="lg:hidden flex items-center gap-1.5 overflow-x-auto py-2.5 border-t border-slate-100 -mx-3 sm:-mx-4 px-3 sm:px-4 scrollbar-none overscroll-x-contain touch-pan-x">
          {navItems.map(item => {
            const isActive = activeTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => setActiveTab(item.id)}
                className={`px-3 py-1.5 text-xs font-semibold whitespace-nowrap rounded-full transition-all shrink-0 active:scale-95 ${
                  isActive
                    ? 'bg-slate-900 text-white shadow-xs'
                    : 'text-slate-600 bg-slate-100/80 hover:bg-slate-200/70 hover:text-slate-900'
                }`}
              >
                {item.label}
              </button>
            );
          })}
        </div>
      </div>
    </header>
  );
};
