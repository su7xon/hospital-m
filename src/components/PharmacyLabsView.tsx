import React, { useState } from 'react';
import { useHospital } from '../context/HospitalContext';
import { MedicineItem, LabOrder } from '../types/hms';
import {
  Pill,
  FlaskConical,
  AlertTriangle,
  Plus,
  Search,
  CheckCircle2,
  Package,
  Clock,
  ArrowRight
} from 'lucide-react';

export const PharmacyLabsView: React.FC = () => {
  const {
    medicines,
    labOrders,
    patients,
    dispenseMedicine,
    addMedicine,
    createLabOrder,
    updateLabResult,
    showToast
  } = useHospital();

  const [activeSubTab, setActiveSubTab] = useState<'pharmacy' | 'labs'>('pharmacy');
  const [medSearch, setMedSearch] = useState('');
  const [medCategory, setMedCategory] = useState<string>('All');

  // Dispense modal
  const [selectedMedForDispense, setSelectedMedForDispense] = useState<MedicineItem | null>(null);
  const [dispenseQty, setDispenseQty] = useState(1);
  const [dispenseRecipient, setDispenseRecipient] = useState('');

  // Add Med modal
  const [isAddMedOpen, setIsAddMedOpen] = useState(false);
  const [newMedName, setNewMedName] = useState('');
  const [newGenericName, setNewGenericName] = useState('');
  const [newCategory, setNewCategory] = useState<MedicineItem['category']>('Antibiotics');
  const [newDosage, setNewDosage] = useState<MedicineItem['dosageForm']>('Tablet');
  const [newStock, setNewStock] = useState(100);
  const [newUnit, setNewUnit] = useState('Tablets');
  const [newMinStock, setNewMinStock] = useState(30);
  const [newPrice, setNewPrice] = useState(25);
  const [newBatch, setNewBatch] = useState('BAT-2026');
  const [newExpiry, setNewExpiry] = useState('2028-12-31');

  // Lab Order modal
  const [isNewLabModalOpen, setIsNewLabModalOpen] = useState(false);
  const [labPatientId, setLabPatientId] = useState('');
  const [labTestName, setLabTestName] = useState('');
  const [labDept, setLabDept] = useState<LabOrder['department']>('Biochemistry');
  const [labPriority, setLabPriority] = useState<LabOrder['priority']>('Routine');
  const [labDoctor, setLabDoctor] = useState('Dr. Rajesh Sharma');

  // Result entry modal
  const [activeLabForResult, setActiveLabForResult] = useState<LabOrder | null>(null);
  const [resultText, setResultText] = useState('');

  // Filter medicines
  const filteredMeds = medicines.filter(m => {
    const matchesCategory = medCategory === 'All' || m.category === medCategory;
    const matchesSearch =
      m.name.toLowerCase().includes(medSearch.toLowerCase()) ||
      m.genericName.toLowerCase().includes(medSearch.toLowerCase()) ||
      m.code.toLowerCase().includes(medSearch.toLowerCase());
    return matchesCategory && matchesSearch;
  });

  const lowStockCount = medicines.filter(m => m.stock <= m.minStock).length;
  const pendingLabsCount = labOrders.filter(l => l.status !== 'Completed').length;
  const statLabsCount = labOrders.filter(l => l.priority === 'STAT Urgent' && l.status !== 'Completed').length;

  const handleDispenseSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedMedForDispense) return;
    const ok = dispenseMedicine(selectedMedForDispense.id, Number(dispenseQty));
    if (ok) {
      setSelectedMedForDispense(null);
      setDispenseQty(1);
    }
  };

  const handleAddMedSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    addMedicine({
      name: newMedName,
      genericName: newGenericName,
      category: newCategory,
      dosageForm: newDosage,
      stock: Number(newStock),
      unit: newUnit,
      minStock: Number(newMinStock),
      unitPrice: Number(newPrice),
      batchNumber: newBatch,
      expiryDate: newExpiry
    });
    setIsAddMedOpen(false);
    setNewMedName('');
    setNewGenericName('');
  };

  const handleCreateLabSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const pat = patients.find(p => p.id === labPatientId);
    if (!pat) {
      showToast('Please select a valid patient.');
      return;
    }

    createLabOrder({
      patientName: pat.name,
      patientMrn: pat.mrn,
      testName: labTestName,
      department: labDept,
      orderedBy: labDoctor,
      status: 'Pending',
      priority: labPriority
    });

    setIsNewLabModalOpen(false);
    setLabTestName('');
  };

  const handleFinalizeResultSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!activeLabForResult || !resultText.trim()) return;
    updateLabResult(activeLabForResult.id, resultText.trim());
    setActiveLabForResult(null);
    setResultText('');
  };

  return (
    <div className="space-y-6">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 pb-2 border-b border-slate-200">
        <div>
          <h1 className="text-xl font-bold text-slate-900 tracking-tight">
            Pharmacy Formulary & Diagnostics Laboratory
          </h1>
          <p className="text-xs text-slate-500 mt-0.5">
            Hospital formulary inventory, bedside dispensation, and clinical diagnostic requisitions.
          </p>
        </div>

        {/* View Toggle Tabs (Segmented buttons - full width on mobile) */}
        <div className="flex items-center gap-1 p-1 bg-slate-100 rounded-lg w-full sm:w-auto">
          <button
            onClick={() => setActiveSubTab('pharmacy')}
            className={`flex-1 sm:flex-initial text-center px-3 py-1.5 text-xs font-semibold rounded-md transition-colors ${
              activeSubTab === 'pharmacy'
                ? 'bg-white text-slate-900 shadow-2xs'
                : 'text-slate-600 hover:text-slate-900'
            }`}
          >
            Formulary Stock ({medicines.length})
          </button>
          <button
            onClick={() => setActiveSubTab('labs')}
            className={`flex-1 sm:flex-initial text-center px-3 py-1.5 text-xs font-semibold rounded-md transition-colors ${
              activeSubTab === 'labs'
                ? 'bg-white text-slate-900 shadow-2xs'
                : 'text-slate-600 hover:text-slate-900'
            }`}
          >
            Diagnostics & Labs ({labOrders.length})
          </button>
        </div>
      </div>

      {/* SUB-TAB 1: PHARMACY FORMULARY */}
      {activeSubTab === 'pharmacy' && (
        <div className="space-y-4">
          {/* Quick Metrics & Actions Bar */}
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 bg-white p-3.5 rounded-lg border border-slate-200 shadow-2xs">
            <div className="flex flex-wrap items-center gap-4 text-xs text-slate-600">
              <div>
                <span className="text-slate-400">Total Formulary SKUs:</span>{' '}
                <strong className="font-mono text-slate-900">{medicines.length} items</strong>
              </div>
              <span className="text-slate-300">·</span>
              <div>
                <span className="text-slate-400">Low Stock Reorder Alerts:</span>{' '}
                <strong className={`font-mono ${lowStockCount > 0 ? 'text-amber-700' : 'text-slate-900'}`}>
                  {lowStockCount} items
                </strong>
              </div>
            </div>

            <button
              onClick={() => setIsAddMedOpen(true)}
              className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold text-white bg-slate-900 hover:bg-slate-800 rounded-md transition-colors shadow-xs"
            >
              <Plus className="w-3.5 h-3.5" />
              <span>Add New Medicine</span>
            </button>
          </div>

          {/* Search & Category Filter */}
          <div className="bg-white p-3 rounded-lg border border-slate-200 shadow-2xs flex flex-col md:flex-row items-stretch md:items-center justify-between gap-3">
            <div className="relative flex-1 max-w-md">
              <Search className="w-4 h-4 absolute left-3 top-2.5 text-slate-400" />
              <input
                type="text"
                value={medSearch}
                onChange={(e) => setMedSearch(e.target.value)}
                placeholder="Search medication name, generic composition, code..."
                className="w-full pl-9 pr-3 py-1.5 text-xs bg-slate-50 border border-slate-200 rounded-md focus:bg-white focus:outline-hidden"
              />
            </div>

            <div className="flex items-center gap-2 text-xs">
              <span className="text-slate-500">Category:</span>
              <select
                value={medCategory}
                onChange={(e) => setMedCategory(e.target.value)}
                className="bg-slate-50 border border-slate-200 rounded px-2.5 py-1.5 text-xs text-slate-700 focus:outline-hidden"
              >
                <option value="All">All Categories</option>
                <option value="Antibiotics">Antibiotics</option>
                <option value="Cardiovascular">Cardiovascular</option>
                <option value="Analgesics">Analgesics</option>
                <option value="Respiratory">Respiratory</option>
                <option value="IV Fluids">IV Fluids</option>
                <option value="Emergency">Emergency</option>
              </select>
            </div>
          </div>

          {/* Medicines Table */}
          <div className="bg-white rounded-lg border border-slate-200 shadow-2xs overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs border-collapse">
                <thead>
                  <tr className="bg-slate-50/80 border-b border-slate-200 text-slate-600 font-semibold">
                    <th className="py-2.5 px-4 font-medium">Drug Code & Name</th>
                    <th className="py-2.5 px-4 font-medium">Generic Composition</th>
                    <th className="py-2.5 px-4 font-medium">Category / Dosage Form</th>
                    <th className="py-2.5 px-4 font-medium">Stock On Hand</th>
                    <th className="py-2.5 px-4 font-medium">Unit Price</th>
                    <th className="py-2.5 px-4 font-medium">Batch / Expiry</th>
                    <th className="py-2.5 px-4 font-medium text-right">Dispense</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {filteredMeds.map(med => {
                    const isLow = med.stock <= med.minStock;
                    return (
                      <tr key={med.id} className="hover:bg-slate-50/60 transition-colors">
                        <td className="py-3 px-4">
                          <span className="font-semibold text-slate-900 block">
                            {med.name}
                          </span>
                          <span className="font-mono text-[11px] text-slate-400 block">
                            {med.code}
                          </span>
                        </td>

                        <td className="py-3 px-4 text-slate-700">
                          {med.genericName}
                        </td>

                        <td className="py-3 px-4 whitespace-nowrap">
                          <span className="font-medium text-slate-800 block">{med.category}</span>
                          <span className="text-[11px] text-slate-400 block">{med.dosageForm}</span>
                        </td>

                        <td className="py-3 px-4 whitespace-nowrap font-mono tabular-nums">
                          <span className={`font-bold block ${isLow ? 'text-amber-700' : 'text-slate-900'}`}>
                            {med.stock} {med.unit}
                          </span>
                          {isLow ? (
                            <span className="text-[11px] text-amber-700 block font-medium">
                              ⚠ Low Stock (Min: {med.minStock})
                            </span>
                          ) : (
                            <span className="text-[11px] text-slate-400 block">
                              Min threshold: {med.minStock}
                            </span>
                          )}
                        </td>

                        <td className="py-3 px-4 font-mono whitespace-nowrap">
                          ₹{med.unitPrice.toFixed(2)}
                        </td>

                        <td className="py-3 px-4 whitespace-nowrap font-mono text-[11px] text-slate-500">
                          <span>Batch: {med.batchNumber}</span>
                          <span className="block text-slate-400">Exp: {med.expiryDate}</span>
                        </td>

                        <td className="py-3 px-4 text-right whitespace-nowrap">
                          <button
                            onClick={() => {
                              setSelectedMedForDispense(med);
                              setDispenseQty(1);
                            }}
                            className="px-2.5 py-1 text-xs font-semibold text-slate-800 bg-slate-100 hover:bg-slate-200 border border-slate-200 rounded transition-colors"
                          >
                            Dispense
                          </button>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {/* SUB-TAB 2: DIAGNOSTICS & LABS */}
      {activeSubTab === 'labs' && (
        <div className="space-y-4">
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 bg-white p-3.5 rounded-lg border border-slate-200 shadow-2xs">
            <div className="flex flex-wrap items-center gap-4 text-xs text-slate-600">
              <div>
                <span className="text-slate-400">Total Requisitions:</span>{' '}
                <strong className="font-mono text-slate-900">{labOrders.length}</strong>
              </div>
              <span className="text-slate-300">·</span>
              <div>
                <span className="text-slate-400">Pending Tests:</span>{' '}
                <strong className="font-mono text-slate-900">{pendingLabsCount}</strong>
              </div>
              <span className="text-slate-300">·</span>
              <div>
                <span className="text-slate-400">STAT Urgent:</span>{' '}
                <strong className={`font-mono ${statLabsCount > 0 ? 'text-rose-700' : 'text-slate-900'}`}>
                  {statLabsCount} orders
                </strong>
              </div>
            </div>

            <button
              onClick={() => setIsNewLabModalOpen(true)}
              className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold text-white bg-slate-900 hover:bg-slate-800 rounded-md transition-colors shadow-xs"
            >
              <Plus className="w-3.5 h-3.5" />
              <span>Order Diagnostic Test</span>
            </button>
          </div>

          {/* Labs Table */}
          <div className="bg-white rounded-lg border border-slate-200 shadow-2xs overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs border-collapse">
                <thead>
                  <tr className="bg-slate-50/80 border-b border-slate-200 text-slate-600 font-semibold">
                    <th className="py-2.5 px-4 font-medium">Requisition & Date</th>
                    <th className="py-2.5 px-4 font-medium">Patient Details</th>
                    <th className="py-2.5 px-4 font-medium">Investigation / Department</th>
                    <th className="py-2.5 px-4 font-medium">Ordering Doctor</th>
                    <th className="py-2.5 px-4 font-medium">Priority</th>
                    <th className="py-2.5 px-4 font-medium">Status & Diagnostic Findings</th>
                    <th className="py-2.5 px-4 font-medium text-right">Result Entry</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {labOrders.map(lab => (
                    <tr key={lab.id} className="hover:bg-slate-50/60 transition-colors">
                      <td className="py-3 px-4 whitespace-nowrap">
                        <span className="font-mono font-semibold text-slate-900 block">
                          {lab.orderNumber}
                        </span>
                        <span className="text-[11px] text-slate-400 font-mono block">
                          {lab.orderedDate}
                        </span>
                      </td>

                      <td className="py-3 px-4 whitespace-nowrap">
                        <span className="font-semibold text-slate-900 block">{lab.patientName}</span>
                        <span className="font-mono text-[11px] text-slate-500 block">{lab.patientMrn}</span>
                      </td>

                      <td className="py-3 px-4">
                        <span className="font-semibold text-slate-800 block">{lab.testName}</span>
                        <span className="text-[11px] text-slate-500 block">{lab.department}</span>
                      </td>

                      <td className="py-3 px-4 whitespace-nowrap text-slate-700">
                        {lab.orderedBy}
                      </td>

                      <td className="py-3 px-4 whitespace-nowrap">
                        <span className={`text-xs font-semibold ${
                          lab.priority === 'STAT Urgent' ? 'text-rose-700' : 'text-slate-600'
                        }`}>
                          {lab.priority}
                        </span>
                      </td>

                      <td className="py-3 px-4 max-w-sm">
                        <span className="text-xs font-semibold text-slate-800 block mb-0.5">
                          {lab.status}
                        </span>
                        {lab.resultSummary ? (
                          <p className="text-[11px] text-slate-700 font-mono bg-slate-50 p-1.5 rounded border border-slate-100">
                            {lab.resultSummary}
                          </p>
                        ) : (
                          <span className="text-[11px] text-slate-400 italic">Processing in lab...</span>
                        )}
                      </td>

                      <td className="py-3 px-4 text-right whitespace-nowrap">
                        <button
                          onClick={() => {
                            setActiveLabForResult(lab);
                            setResultText(lab.resultSummary || '');
                          }}
                          className="px-2.5 py-1 text-xs font-semibold text-slate-700 hover:text-slate-900 bg-slate-100 hover:bg-slate-200 rounded transition-colors"
                        >
                          {lab.status === 'Completed' ? 'Edit Findings' : 'Log Result'}
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {/* DISPENSE MODAL */}
      {selectedMedForDispense && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/50 backdrop-blur-xs">
          <div className="bg-white rounded-xl border border-slate-200 shadow-xl w-full max-w-md p-5 space-y-4">
            <h3 className="text-sm font-bold text-slate-900">
              Dispense Medication to Patient
            </h3>
            <div className="bg-slate-50 p-3 rounded-lg border border-slate-200 text-xs">
              <span className="font-bold text-slate-900 block">{selectedMedForDispense.name}</span>
              <span className="text-slate-500 block">{selectedMedForDispense.genericName}</span>
              <span className="font-mono text-slate-600 block mt-1">
                Stock: {selectedMedForDispense.stock} {selectedMedForDispense.unit} · Unit Price: ₹{selectedMedForDispense.unitPrice}
              </span>
            </div>

            <form onSubmit={handleDispenseSubmit} className="space-y-3 text-xs">
              <div>
                <label className="font-semibold text-slate-700 block mb-1">
                  Quantity to Dispense ({selectedMedForDispense.unit})
                </label>
                <input
                  type="number"
                  min="1"
                  max={selectedMedForDispense.stock}
                  value={dispenseQty}
                  onChange={(e) => setDispenseQty(Number(e.target.value))}
                  required
                  className="w-full px-3 py-1.5 bg-slate-50 border border-slate-200 rounded font-mono"
                />
              </div>

              <div>
                <label className="font-semibold text-slate-700 block mb-1">
                  Patient or Ward Allocation Note
                </label>
                <input
                  type="text"
                  placeholder="e.g. Bed ICU-02 (Rohan Deshmukh)"
                  value={dispenseRecipient}
                  onChange={(e) => setDispenseRecipient(e.target.value)}
                  className="w-full px-3 py-1.5 bg-slate-50 border border-slate-200 rounded"
                />
              </div>

              <div className="flex items-center justify-end gap-2 pt-2">
                <button
                  type="button"
                  onClick={() => setSelectedMedForDispense(null)}
                  className="px-3 py-1.5 font-semibold text-slate-700 bg-slate-100 hover:bg-slate-200 rounded"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-1.5 font-semibold text-white bg-slate-900 hover:bg-slate-800 rounded"
                >
                  Confirm Dispensation
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* ADD NEW MEDICINE MODAL */}
      {isAddMedOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/50 backdrop-blur-xs">
          <div className="bg-white rounded-xl border border-slate-200 shadow-xl w-full max-w-lg p-5 space-y-4 max-h-[90vh] overflow-y-auto">
            <h3 className="text-sm font-bold text-slate-900">
              Add New Medicine to Formulary
            </h3>

            <form onSubmit={handleAddMedSubmit} className="space-y-3 text-xs">
              <div>
                <label className="font-semibold text-slate-700 block mb-1">Brand Name & Strength</label>
                <input
                  type="text"
                  placeholder="e.g. Augmentin 625 Duo"
                  value={newMedName}
                  onChange={(e) => setNewMedName(e.target.value)}
                  required
                  className="w-full px-3 py-1.5 bg-slate-50 border border-slate-200 rounded"
                />
              </div>

              <div>
                <label className="font-semibold text-slate-700 block mb-1">Generic / Chemical Name</label>
                <input
                  type="text"
                  placeholder="e.g. Amoxicillin + Clavulanic Acid"
                  value={newGenericName}
                  onChange={(e) => setNewGenericName(e.target.value)}
                  required
                  className="w-full px-3 py-1.5 bg-slate-50 border border-slate-200 rounded"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="font-semibold text-slate-700 block mb-1">Therapeutic Category</label>
                  <select
                    value={newCategory}
                    onChange={(e) => setNewCategory(e.target.value as any)}
                    className="w-full px-3 py-1.5 bg-slate-50 border border-slate-200 rounded"
                  >
                    <option value="Antibiotics">Antibiotics</option>
                    <option value="Cardiovascular">Cardiovascular</option>
                    <option value="Analgesics">Analgesics</option>
                    <option value="Respiratory">Respiratory</option>
                    <option value="IV Fluids">IV Fluids</option>
                    <option value="Emergency">Emergency</option>
                    <option value="Vitamins">Vitamins</option>
                  </select>
                </div>

                <div>
                  <label className="font-semibold text-slate-700 block mb-1">Dosage Form</label>
                  <select
                    value={newDosage}
                    onChange={(e) => setNewDosage(e.target.value as any)}
                    className="w-full px-3 py-1.5 bg-slate-50 border border-slate-200 rounded"
                  >
                    <option value="Tablet">Tablet</option>
                    <option value="Capsule">Capsule</option>
                    <option value="Injection">Injection</option>
                    <option value="IV Infusion">IV Infusion</option>
                    <option value="Syrup">Syrup</option>
                    <option value="Ointment">Ointment</option>
                  </select>
                </div>

                <div>
                  <label className="font-semibold text-slate-700 block mb-1">Initial Stock Quantity</label>
                  <input
                    type="number"
                    value={newStock}
                    onChange={(e) => setNewStock(Number(e.target.value))}
                    required
                    className="w-full px-3 py-1.5 bg-slate-50 border border-slate-200 rounded font-mono"
                  />
                </div>

                <div>
                  <label className="font-semibold text-slate-700 block mb-1">Unit of Measure</label>
                  <input
                    type="text"
                    value={newUnit}
                    onChange={(e) => setNewUnit(e.target.value)}
                    required
                    className="w-full px-3 py-1.5 bg-slate-50 border border-slate-200 rounded"
                  />
                </div>

                <div>
                  <label className="font-semibold text-slate-700 block mb-1">Minimum Reorder Level</label>
                  <input
                    type="number"
                    value={newMinStock}
                    onChange={(e) => setNewMinStock(Number(e.target.value))}
                    required
                    className="w-full px-3 py-1.5 bg-slate-50 border border-slate-200 rounded font-mono"
                  />
                </div>

                <div>
                  <label className="font-semibold text-slate-700 block mb-1">Unit Price (₹)</label>
                  <input
                    type="number"
                    step="0.01"
                    value={newPrice}
                    onChange={(e) => setNewPrice(Number(e.target.value))}
                    required
                    className="w-full px-3 py-1.5 bg-slate-50 border border-slate-200 rounded font-mono"
                  />
                </div>

                <div>
                  <label className="font-semibold text-slate-700 block mb-1">Batch Number</label>
                  <input
                    type="text"
                    value={newBatch}
                    onChange={(e) => setNewBatch(e.target.value)}
                    required
                    className="w-full px-3 py-1.5 bg-slate-50 border border-slate-200 rounded font-mono"
                  />
                </div>

                <div>
                  <label className="font-semibold text-slate-700 block mb-1">Expiry Date</label>
                  <input
                    type="date"
                    value={newExpiry}
                    onChange={(e) => setNewExpiry(e.target.value)}
                    required
                    className="w-full px-3 py-1.5 bg-slate-50 border border-slate-200 rounded font-mono"
                  />
                </div>
              </div>

              <div className="flex items-center justify-end gap-2 pt-3 border-t border-slate-100">
                <button
                  type="button"
                  onClick={() => setIsAddMedOpen(false)}
                  className="px-3 py-1.5 font-semibold text-slate-700 bg-slate-100 hover:bg-slate-200 rounded"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-1.5 font-semibold text-white bg-slate-900 hover:bg-slate-800 rounded"
                >
                  Add to Inventory
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* NEW LAB ORDER MODAL */}
      {isNewLabModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/50 backdrop-blur-xs">
          <div className="bg-white rounded-xl border border-slate-200 shadow-xl w-full max-w-md p-5 space-y-4">
            <h3 className="text-sm font-bold text-slate-900">
              Create Diagnostic Requisition
            </h3>

            <form onSubmit={handleCreateLabSubmit} className="space-y-3 text-xs">
              <div>
                <label className="font-semibold text-slate-700 block mb-1">Select Patient</label>
                <select
                  value={labPatientId}
                  onChange={(e) => setLabPatientId(e.target.value)}
                  required
                  className="w-full px-3 py-1.5 bg-slate-50 border border-slate-200 rounded"
                >
                  <option value="">-- Choose patient --</option>
                  {patients.map(p => (
                    <option key={p.id} value={p.id}>
                      {p.name} ({p.mrn}) · {p.ward || 'OPD'}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="font-semibold text-slate-700 block mb-1">Test / Investigation Name</label>
                <input
                  type="text"
                  placeholder="e.g. Arterial Blood Gas (ABG), Serum Electrolytes, CT Head"
                  value={labTestName}
                  onChange={(e) => setLabTestName(e.target.value)}
                  required
                  className="w-full px-3 py-1.5 bg-slate-50 border border-slate-200 rounded"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="font-semibold text-slate-700 block mb-1">Department</label>
                  <select
                    value={labDept}
                    onChange={(e) => setLabDept(e.target.value as any)}
                    className="w-full px-3 py-1.5 bg-slate-50 border border-slate-200 rounded"
                  >
                    <option value="Biochemistry">Biochemistry</option>
                    <option value="Hematology">Hematology</option>
                    <option value="Radiology">Radiology</option>
                    <option value="Microbiology">Microbiology</option>
                    <option value="Pathology">Pathology</option>
                  </select>
                </div>

                <div>
                  <label className="font-semibold text-slate-700 block mb-1">Clinical Priority</label>
                  <select
                    value={labPriority}
                    onChange={(e) => setLabPriority(e.target.value as any)}
                    className="w-full px-3 py-1.5 bg-slate-50 border border-slate-200 rounded font-semibold"
                  >
                    <option value="Routine">Routine</option>
                    <option value="STAT Urgent">STAT Urgent</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="font-semibold text-slate-700 block mb-1">Ordering Physician</label>
                <input
                  type="text"
                  value={labDoctor}
                  onChange={(e) => setLabDoctor(e.target.value)}
                  required
                  className="w-full px-3 py-1.5 bg-slate-50 border border-slate-200 rounded"
                />
              </div>

              <div className="flex items-center justify-end gap-2 pt-3 border-t border-slate-100">
                <button
                  type="button"
                  onClick={() => setIsNewLabModalOpen(false)}
                  className="px-3 py-1.5 font-semibold text-slate-700 bg-slate-100 hover:bg-slate-200 rounded"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-1.5 font-semibold text-white bg-slate-900 hover:bg-slate-800 rounded"
                >
                  Issue Requisition
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* ENTER RESULT MODAL */}
      {activeLabForResult && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/50 backdrop-blur-xs">
          <div className="bg-white rounded-xl border border-slate-200 shadow-xl w-full max-w-md p-5 space-y-4">
            <h3 className="text-sm font-bold text-slate-900">
              Log Diagnostic Findings & Lab Result
            </h3>
            <p className="text-xs text-slate-600">
              Requisition: <strong>{activeLabForResult.orderNumber}</strong> ({activeLabForResult.testName}) for <strong>{activeLabForResult.patientName}</strong>
            </p>

            <form onSubmit={handleFinalizeResultSubmit} className="space-y-3 text-xs">
              <div>
                <label className="font-semibold text-slate-700 block mb-1">
                  Findings / Reference Values
                </label>
                <textarea
                  rows={4}
                  value={resultText}
                  onChange={(e) => setResultText(e.target.value)}
                  placeholder="e.g. Hemoglobin: 13.2 g/dL (Normal: 12.0-16.0). WBC: 7,800/uL. Platelets: 240,000/uL."
                  required
                  className="w-full p-2.5 bg-slate-50 border border-slate-200 rounded font-mono"
                />
              </div>

              <div className="flex items-center justify-end gap-2 pt-2">
                <button
                  type="button"
                  onClick={() => setActiveLabForResult(null)}
                  className="px-3 py-1.5 font-semibold text-slate-700 bg-slate-100 hover:bg-slate-200 rounded"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-1.5 font-semibold text-white bg-emerald-800 hover:bg-emerald-900 rounded"
                >
                  Finalize & Sign Result
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
