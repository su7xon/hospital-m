import React, { useState } from 'react';
import { useHospital } from '../context/HospitalContext';
import { BillingInvoice, InvoiceItem } from '../types/hms';
import {
  DollarSign,
  Plus,
  Printer,
  CheckCircle2,
  Clock,
  FileText,
  CreditCard,
  Building,
  Search
} from 'lucide-react';

export const BillingView: React.FC = () => {
  const {
    invoices,
    patients,
    createInvoice,
    updateInvoicePayment,
    selectedInvoiceForPrint,
    setSelectedInvoiceForPrint,
    setIsNewInvoiceModalOpen,
    isNewInvoiceModalOpen,
    showToast
  } = useHospital();

  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState<'All' | 'Paid' | 'Pending' | 'Partially Paid'>('All');

  // New Invoice Form state
  const [selectedPatientId, setSelectedPatientId] = useState('');
  const [items, setItems] = useState<InvoiceItem[]>([
    { id: '1', description: 'General Consultation / Physician Rounds', category: 'Consultation', quantity: 1, unitPrice: 1000, total: 1000 }
  ]);
  const [taxPercent, setTaxPercent] = useState(5);
  const [discountAmt, setDiscountAmt] = useState(0);
  const [payStatus, setPayStatus] = useState<BillingInvoice['paymentStatus']>('Pending');
  const [payMethod, setPayMethod] = useState<BillingInvoice['paymentMethod']>('Cash');
  const [insuranceName, setInsuranceName] = useState('');
  const [billNotes, setBillNotes] = useState('');

  // Item form inputs
  const [newItemDesc, setNewItemDesc] = useState('');
  const [newItemCat, setNewItemCat] = useState<InvoiceItem['category']>('Room / Bed');
  const [newItemQty, setNewItemQty] = useState(1);
  const [newItemPrice, setNewItemPrice] = useState(1500);

  // Financial aggregates
  const totalBilled = invoices.reduce((acc, curr) => acc + curr.grandTotal, 0);
  const totalCollected = invoices.filter(i => i.paymentStatus === 'Paid').reduce((acc, curr) => acc + curr.grandTotal, 0);
  const totalPending = invoices.filter(i => i.paymentStatus !== 'Paid').reduce((acc, curr) => acc + curr.grandTotal, 0);

  const filteredInvoices = invoices.filter(inv => {
    const matchesSearch =
      inv.invoiceNumber.toLowerCase().includes(search.toLowerCase()) ||
      inv.patientName.toLowerCase().includes(search.toLowerCase()) ||
      inv.patientMrn.toLowerCase().includes(search.toLowerCase());
    const matchesStatus = statusFilter === 'All' || inv.paymentStatus === statusFilter;
    return matchesSearch && matchesStatus;
  });

  const handleAddItem = () => {
    if (!newItemDesc.trim()) return;
    const total = newItemQty * newItemPrice;
    setItems(prev => [
      ...prev,
      {
        id: `item-${Date.now()}`,
        description: newItemDesc.trim(),
        category: newItemCat,
        quantity: newItemQty,
        unitPrice: newItemPrice,
        total
      }
    ]);
    setNewItemDesc('');
    setNewItemQty(1);
  };

  const handleRemoveItem = (id: string) => {
    setItems(prev => prev.filter(i => i.id !== id));
  };

  const handleCreateInvoiceSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedPatientId) {
      showToast('Please select a patient.');
      return;
    }
    if (items.length === 0) {
      showToast('Please add at least one line item to the bill.');
      return;
    }

    const subtotal = items.reduce((acc, curr) => acc + curr.total, 0);
    const tax = Math.round((subtotal * taxPercent) / 100);

    createInvoice({
      patientId: selectedPatientId,
      items,
      tax,
      discount: discountAmt,
      paymentStatus: payStatus,
      paymentMethod: payStatus === 'Paid' ? payMethod : undefined,
      insuranceProvider: payMethod === 'Insurance / TPA' ? insuranceName : undefined,
      notes: billNotes
    });

    setIsNewInvoiceModalOpen(false);
    // Reset form
    setSelectedPatientId('');
    setItems([{ id: '1', description: 'General Consultation / Physician Rounds', category: 'Consultation', quantity: 1, unitPrice: 1000, total: 1000 }]);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 pb-2 border-b border-slate-200">
        <div>
          <h1 className="text-xl font-bold text-slate-900 tracking-tight">
            Patient Billing & Financial Accounts
          </h1>
          <p className="text-xs text-slate-500 mt-0.5">
            Hospital tariffs, inpatient folios, itemized charges, and payment settlements.
          </p>
        </div>

        <button
          onClick={() => setIsNewInvoiceModalOpen(true)}
          className="flex items-center justify-center gap-1.5 px-3 py-1.5 text-xs font-semibold text-white bg-slate-900 hover:bg-slate-800 rounded-md transition-colors w-full sm:w-auto shadow-xs"
        >
          <Plus className="w-3.5 h-3.5" />
          <span>Generate New Bill</span>
        </button>
      </div>

      {/* KPI Stats */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
        <div className="bg-white p-4 rounded-lg border border-slate-200 shadow-2xs">
          <span className="text-xs font-medium text-slate-500 block">Total Billed Revenue</span>
          <span className="text-2xl font-bold font-mono text-slate-900 tabular-nums block mt-1">
            ₹{totalBilled.toLocaleString('en-IN', { maximumFractionDigits: 0 })}
          </span>
          <span className="text-[11px] text-slate-400 mt-1 block">Cumulative invoices issued</span>
        </div>

        <div className="bg-white p-4 rounded-lg border border-slate-200 shadow-2xs">
          <span className="text-xs font-medium text-slate-500 block">Collected Payments</span>
          <span className="text-2xl font-bold font-mono text-emerald-700 tabular-nums block mt-1">
            ₹{totalCollected.toLocaleString('en-IN', { maximumFractionDigits: 0 })}
          </span>
          <span className="text-[11px] text-emerald-600 mt-1 block">Settled via cash, card & TPA</span>
        </div>

        <div className="bg-white p-4 rounded-lg border border-slate-200 shadow-2xs">
          <span className="text-xs font-medium text-slate-500 block">Pending Inpatient Receivables</span>
          <span className="text-2xl font-bold font-mono text-amber-700 tabular-nums block mt-1">
            ₹{totalPending.toLocaleString('en-IN', { maximumFractionDigits: 0 })}
          </span>
          <span className="text-[11px] text-amber-600 mt-1 block">Awaiting discharge settlement</span>
        </div>
      </div>

      {/* Filter and Search */}
      <div className="bg-white p-3.5 rounded-lg border border-slate-200 shadow-2xs space-y-3">
        <div className="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-3">
          <div className="relative flex-1 max-w-md">
            <Search className="w-4 h-4 absolute left-3 top-2.5 text-slate-400" />
            <input
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search invoice number, patient name, MRN..."
              className="w-full pl-9 pr-3 py-1.5 text-xs bg-slate-50 border border-slate-200 rounded-md focus:bg-white focus:outline-hidden"
            />
          </div>

          <div className="flex items-center gap-1 text-xs overflow-x-auto scrollbar-none pb-0.5 touch-pan-x">
            <span className="text-slate-500 mr-2 shrink-0">Payment Status:</span>
            {(['All', 'Paid', 'Pending', 'Partially Paid'] as const).map(st => (
              <button
                key={st}
                onClick={() => setStatusFilter(st)}
                className={`px-2.5 py-1 text-xs font-medium rounded transition-colors whitespace-nowrap shrink-0 ${
                  statusFilter === st
                    ? 'bg-slate-900 text-white shadow-2xs'
                    : 'text-slate-600 hover:bg-slate-100'
                }`}
              >
                {st}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Invoices Table */}
      <div className="bg-white rounded-lg border border-slate-200 shadow-2xs overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs border-collapse">
            <thead>
              <tr className="bg-slate-50/80 border-b border-slate-200 text-slate-600 font-semibold">
                <th className="py-2.5 px-4 font-medium">Invoice # & Date</th>
                <th className="py-2.5 px-4 font-medium">Patient Details</th>
                <th className="py-2.5 px-4 font-medium">Itemized Breakdown</th>
                <th className="py-2.5 px-4 font-medium">Grand Total</th>
                <th className="py-2.5 px-4 font-medium">Settlement Status</th>
                <th className="py-2.5 px-4 font-medium text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {filteredInvoices.map(inv => (
                <tr key={inv.id} className="hover:bg-slate-50/60 transition-colors">
                  <td className="py-3 px-4 whitespace-nowrap">
                    <span className="font-mono font-bold text-slate-900 block">
                      {inv.invoiceNumber}
                    </span>
                    <span className="text-[11px] font-mono text-slate-400 block">
                      {inv.issuedAt}
                    </span>
                  </td>

                  <td className="py-3 px-4 whitespace-nowrap">
                    <span className="font-semibold text-slate-900 block">
                      {inv.patientName}
                    </span>
                    <span className="text-[11px] font-mono text-slate-500 block">
                      {inv.patientMrn} · {inv.patientPhone}
                    </span>
                  </td>

                  <td className="py-3 px-4 max-w-xs text-slate-600">
                    <span className="block font-medium text-slate-800">
                      {inv.items.length} line item(s)
                    </span>
                    <span className="text-[11px] text-slate-400 truncate block">
                      {inv.items.map(i => i.description).join(', ')}
                    </span>
                  </td>

                  <td className="py-3 px-4 whitespace-nowrap font-mono tabular-nums">
                    <span className="font-bold text-slate-900 text-sm block">
                      ₹{inv.grandTotal.toLocaleString('en-IN', { maximumFractionDigits: 2 })}
                    </span>
                    {inv.discount > 0 && (
                      <span className="text-[10px] text-emerald-600 block">
                        Discount: ₹{inv.discount}
                      </span>
                    )}
                  </td>

                  <td className="py-3 px-4 whitespace-nowrap">
                    <span className={`text-xs font-semibold block ${
                      inv.paymentStatus === 'Paid'
                        ? 'text-emerald-700'
                        : inv.paymentStatus === 'Partially Paid'
                        ? 'text-amber-700'
                        : 'text-rose-700'
                    }`}>
                      {inv.paymentStatus}
                    </span>
                    {inv.paymentMethod && (
                      <span className="text-[11px] text-slate-500 block">
                        via {inv.paymentMethod}
                      </span>
                    )}
                  </td>

                  <td className="py-3 px-4 text-right whitespace-nowrap space-x-2">
                    {inv.paymentStatus !== 'Paid' && (
                      <button
                        onClick={() => updateInvoicePayment(inv.id, 'Paid', 'UPI / Bank Transfer')}
                        className="px-2.5 py-1 text-xs font-semibold text-emerald-800 bg-emerald-50 hover:bg-emerald-100 border border-emerald-200 rounded transition-colors"
                      >
                        Mark Paid
                      </button>
                    )}
                    <button
                      onClick={() => setSelectedInvoiceForPrint(inv)}
                      className="px-2.5 py-1 text-xs font-semibold text-slate-700 bg-slate-100 hover:bg-slate-200 rounded transition-colors inline-flex items-center gap-1"
                    >
                      <Printer className="w-3 h-3 text-slate-600" />
                      <span>Print Receipt</span>
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* CREATE INVOICE MODAL */}
      {isNewInvoiceModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-3 sm:p-6 bg-slate-900/50 backdrop-blur-xs">
          <div className="bg-white rounded-xl border border-slate-200 shadow-xl w-full max-w-2xl max-h-[92vh] flex flex-col overflow-hidden">
            <div className="px-6 py-4 border-b border-slate-200 bg-slate-50/80 flex items-center justify-between">
              <h3 className="text-sm font-bold text-slate-900">
                Generate Patient Inpatient / OPD Invoice
              </h3>
              <button
                onClick={() => setIsNewInvoiceModalOpen(false)}
                className="text-slate-400 hover:text-slate-600 text-sm font-bold"
              >
                ✕
              </button>
            </div>

            <form onSubmit={handleCreateInvoiceSubmit} className="flex-1 overflow-y-auto p-6 space-y-4 text-xs">
              {/* Select Patient */}
              <div>
                <label className="font-semibold text-slate-700 block mb-1">Select Patient</label>
                <select
                  value={selectedPatientId}
                  onChange={(e) => {
                    const patId = e.target.value;
                    setSelectedPatientId(patId);
                    const p = patients.find(item => item.id === patId);
                    if (p && p.bedNumber) {
                      // Add room charge row automatically
                      setItems([
                        {
                          id: 'bed-charge',
                          description: `Room & Nursing Charges (${p.ward} · Bed ${p.bedNumber})`,
                          category: 'Room / Bed',
                          quantity: 2,
                          unitPrice: 1800,
                          total: 3600
                        },
                        {
                          id: 'doc-visit',
                          description: `Attending Doctor Inpatient Care (${p.assignedDoctorName})`,
                          category: 'Consultation',
                          quantity: 2,
                          unitPrice: 1000,
                          total: 2000
                        }
                      ]);
                    }
                  }}
                  required
                  className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded"
                >
                  <option value="">-- Choose Patient Record --</option>
                  {patients.map(p => (
                    <option key={p.id} value={p.id}>
                      {p.name} ({p.mrn}) · {p.ward || 'OPD'} · Status: {p.status}
                    </option>
                  ))}
                </select>
              </div>

              {/* Item Builder */}
              <div>
                <label className="font-semibold text-slate-700 block mb-1.5">
                  Invoice Line Items ({items.length})
                </label>

                {/* Items List */}
                <div className="border border-slate-200 rounded-lg overflow-hidden divide-y divide-slate-100 mb-3 bg-white">
                  {items.map(item => (
                    <div key={item.id} className="p-2.5 flex items-center justify-between gap-3 text-xs">
                      <div>
                        <span className="font-medium text-slate-900 block">{item.description}</span>
                        <span className="text-[11px] text-slate-400">
                          {item.category} · {item.quantity} x ₹{item.unitPrice}
                        </span>
                      </div>
                      <div className="flex items-center gap-3">
                        <span className="font-mono font-semibold text-slate-900">₹{item.total}</span>
                        <button
                          type="button"
                          onClick={() => handleRemoveItem(item.id)}
                          className="text-slate-400 hover:text-rose-600"
                        >
                          ✕
                        </button>
                      </div>
                    </div>
                  ))}
                </div>

                {/* Quick Add Line Item */}
                <div className="p-3 bg-slate-50 rounded-lg border border-slate-200 space-y-2">
                  <span className="text-[11px] font-semibold text-slate-600 block">Add Line Charge</span>
                  <div className="grid grid-cols-1 sm:grid-cols-4 gap-2">
                    <input
                      type="text"
                      placeholder="Service / Medication / Procedure"
                      value={newItemDesc}
                      onChange={(e) => setNewItemDesc(e.target.value)}
                      className="sm:col-span-2 px-2.5 py-1.5 bg-white border border-slate-200 rounded text-xs"
                    />
                    <select
                      value={newItemCat}
                      onChange={(e) => setNewItemCat(e.target.value as any)}
                      className="px-2 py-1.5 bg-white border border-slate-200 rounded text-xs"
                    >
                      <option value="Room / Bed">Room / Bed</option>
                      <option value="Consultation">Consultation</option>
                      <option value="Medication">Medication</option>
                      <option value="Lab Test">Lab Test</option>
                      <option value="Nursing">Nursing</option>
                      <option value="Procedure">Procedure</option>
                    </select>
                    <div className="flex items-center gap-1">
                      <input
                        type="number"
                        placeholder="Price"
                        value={newItemPrice}
                        onChange={(e) => setNewItemPrice(Number(e.target.value))}
                        className="w-full px-2 py-1.5 bg-white border border-slate-200 rounded text-xs font-mono"
                      />
                      <button
                        type="button"
                        onClick={handleAddItem}
                        className="px-3 py-1.5 font-semibold text-white bg-slate-800 hover:bg-slate-900 rounded shrink-0"
                      >
                        + Add
                      </button>
                    </div>
                  </div>
                </div>
              </div>

              {/* Financial Calculation */}
              <div className="grid grid-cols-2 gap-4 pt-2">
                <div>
                  <label className="font-semibold text-slate-700 block mb-1">Applicable Tax (% GST)</label>
                  <input
                    type="number"
                    value={taxPercent}
                    onChange={(e) => setTaxPercent(Number(e.target.value))}
                    className="w-full px-3 py-1.5 bg-slate-50 border border-slate-200 rounded font-mono"
                  />
                </div>

                <div>
                  <label className="font-semibold text-slate-700 block mb-1">Discount (₹)</label>
                  <input
                    type="number"
                    value={discountAmt}
                    onChange={(e) => setDiscountAmt(Number(e.target.value))}
                    className="w-full px-3 py-1.5 bg-slate-50 border border-slate-200 rounded font-mono"
                  />
                </div>

                <div>
                  <label className="font-semibold text-slate-700 block mb-1">Payment Status</label>
                  <select
                    value={payStatus}
                    onChange={(e) => setPayStatus(e.target.value as any)}
                    className="w-full px-3 py-1.5 bg-slate-50 border border-slate-200 rounded"
                  >
                    <option value="Pending">Pending</option>
                    <option value="Paid">Paid (Settled)</option>
                    <option value="Partially Paid">Partially Paid</option>
                  </select>
                </div>

                <div>
                  <label className="font-semibold text-slate-700 block mb-1">Payment Method</label>
                  <select
                    value={payMethod}
                    onChange={(e) => setPayMethod(e.target.value as any)}
                    className="w-full px-3 py-1.5 bg-slate-50 border border-slate-200 rounded"
                  >
                    <option value="Cash">Cash</option>
                    <option value="Card">Card (POS)</option>
                    <option value="UPI / Bank Transfer">UPI / Bank Transfer</option>
                    <option value="Insurance / TPA">Insurance / TPA Cashless</option>
                  </select>
                </div>
              </div>

              {payMethod === 'Insurance / TPA' && (
                <div>
                  <label className="font-semibold text-slate-700 block mb-1">TPA Insurance Provider & Policy #</label>
                  <input
                    type="text"
                    placeholder="e.g. Star Health / ICICI Lombard Pre-Auth #88912"
                    value={insuranceName}
                    onChange={(e) => setInsuranceName(e.target.value)}
                    className="w-full px-3 py-1.5 bg-slate-50 border border-slate-200 rounded"
                  />
                </div>
              )}

              <div>
                <label className="font-semibold text-slate-700 block mb-1">Billing Remarks</label>
                <input
                  type="text"
                  placeholder="e.g. Interim running bill / Full settlement upon discharge"
                  value={billNotes}
                  onChange={(e) => setBillNotes(e.target.value)}
                  className="w-full px-3 py-1.5 bg-slate-50 border border-slate-200 rounded"
                />
              </div>

              <div className="flex items-center justify-end gap-2 pt-4 border-t border-slate-100">
                <button
                  type="button"
                  onClick={() => setIsNewInvoiceModalOpen(false)}
                  className="px-4 py-2 font-semibold text-slate-700 bg-slate-100 hover:bg-slate-200 rounded"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-5 py-2 font-semibold text-white bg-slate-900 hover:bg-slate-800 rounded"
                >
                  Generate Invoice
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* PRINT OFFICIAL INVOICE MODAL (CLEAN A4 HOSPITAL TEMPLATE) */}
      {selectedInvoiceForPrint && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-2 sm:p-4 bg-slate-900/60 backdrop-blur-xs overflow-y-auto">
          <div className="bg-white rounded-lg border border-slate-300 shadow-2xl w-full max-w-3xl my-6 p-8 space-y-6 text-slate-900 print-full">
            {/* Print Header */}
            <div className="flex items-start justify-between border-b-2 border-slate-900 pb-4">
              <div>
                <h2 className="text-xl font-bold tracking-tight text-slate-900 uppercase">
                  Aegis Health Hospital
                </h2>
                <p className="text-xs text-slate-600 mt-0.5">
                  Metropolitan Multispecialty Care · Campus B
                </p>
                <p className="text-[11px] text-slate-500 font-mono">
                  Reg No: HSP/MH/2019/8491 · GSTIN: 27AABCA1234F1Z8
                </p>
              </div>

              <div className="text-right">
                <span className="text-xs font-mono font-bold block text-slate-900">
                  {selectedInvoiceForPrint.invoiceNumber}
                </span>
                <span className="text-[11px] text-slate-500 font-mono block">
                  Date: {selectedInvoiceForPrint.issuedAt}
                </span>
                <span className={`text-xs font-bold inline-block mt-1 px-2 py-0.5 border ${
                  selectedInvoiceForPrint.paymentStatus === 'Paid'
                    ? 'border-emerald-600 text-emerald-700'
                    : 'border-amber-600 text-amber-700'
                }`}>
                  {selectedInvoiceForPrint.paymentStatus.toUpperCase()}
                </span>
              </div>
            </div>

            {/* Patient & Admission Info Strip */}
            <div className="grid grid-cols-2 gap-4 text-xs bg-slate-50 p-4 rounded border border-slate-200">
              <div>
                <span className="text-slate-400 block font-semibold">PATIENT INFORMATION</span>
                <span className="font-bold text-sm text-slate-900 block mt-0.5">
                  {selectedInvoiceForPrint.patientName}
                </span>
                <span className="font-mono text-slate-600 block">MRN: {selectedInvoiceForPrint.patientMrn}</span>
                <span className="font-mono text-slate-600 block">Phone: {selectedInvoiceForPrint.patientPhone}</span>
              </div>

              <div>
                <span className="text-slate-400 block font-semibold">ADMISSION & DISCHARGE</span>
                <span className="font-mono text-slate-800 block mt-0.5">
                  Intake: {selectedInvoiceForPrint.admissionDate}
                </span>
                <span className="font-mono text-slate-800 block">
                  Discharge: {selectedInvoiceForPrint.dischargeDate || 'Ongoing Inpatient Stay'}
                </span>
                {selectedInvoiceForPrint.insuranceProvider && (
                  <span className="text-slate-700 block mt-1">
                    TPA: {selectedInvoiceForPrint.insuranceProvider}
                  </span>
                )}
              </div>
            </div>

            {/* Line Items Table */}
            <table className="w-full text-xs border-collapse">
              <thead>
                <tr className="border-b border-slate-300 font-semibold text-slate-700 text-left">
                  <th className="py-2">Item Description</th>
                  <th className="py-2">Category</th>
                  <th className="py-2 text-right">Qty</th>
                  <th className="py-2 text-right">Rate</th>
                  <th className="py-2 text-right">Amount (₹)</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-200">
                {selectedInvoiceForPrint.items.map((item, idx) => (
                  <tr key={idx} className="text-slate-800">
                    <td className="py-2.5 font-medium">{item.description}</td>
                    <td className="py-2.5 text-slate-500">{item.category}</td>
                    <td className="py-2.5 text-right font-mono">{item.quantity}</td>
                    <td className="py-2.5 text-right font-mono">₹{item.unitPrice.toLocaleString('en-IN')}</td>
                    <td className="py-2.5 text-right font-mono font-semibold">₹{item.total.toLocaleString('en-IN')}</td>
                  </tr>
                ))}
              </tbody>
            </table>

            {/* Calculation Totals */}
            <div className="flex justify-end pt-2">
              <div className="w-64 space-y-1.5 text-xs">
                <div className="flex justify-between text-slate-600">
                  <span>Subtotal:</span>
                  <span className="font-mono">₹{selectedInvoiceForPrint.subtotal.toLocaleString('en-IN')}</span>
                </div>
                {selectedInvoiceForPrint.tax > 0 && (
                  <div className="flex justify-between text-slate-600">
                    <span>GST Tax:</span>
                    <span className="font-mono">₹{selectedInvoiceForPrint.tax.toLocaleString('en-IN')}</span>
                  </div>
                )}
                {selectedInvoiceForPrint.discount > 0 && (
                  <div className="flex justify-between text-emerald-700">
                    <span>Discount:</span>
                    <span className="font-mono">-₹{selectedInvoiceForPrint.discount.toLocaleString('en-IN')}</span>
                  </div>
                )}
                <div className="flex justify-between text-base font-bold text-slate-900 border-t border-slate-300 pt-2">
                  <span>Total Due:</span>
                  <span className="font-mono">₹{selectedInvoiceForPrint.grandTotal.toLocaleString('en-IN')}</span>
                </div>
              </div>
            </div>

            {/* Footer / Signatures */}
            <div className="pt-8 border-t border-slate-200 flex items-end justify-between text-[11px] text-slate-500">
              <div>
                <p>Computer generated invoice. No physical signature required.</p>
                <p className="font-mono">For billing queries: billing@aegishealth.org</p>
              </div>
              <div className="text-right border-t border-slate-400 pt-2 w-48">
                <span className="block font-semibold text-slate-800">Authorized Accounts Desk</span>
                <span className="text-[10px]">Aegis Health Hospital</span>
              </div>
            </div>

            {/* Action Bar (hidden on print) */}
            <div className="no-print pt-4 border-t border-slate-100 flex items-center justify-end gap-2">
              <button
                type="button"
                onClick={() => setSelectedInvoiceForPrint(null)}
                className="px-4 py-2 text-xs font-semibold text-slate-700 bg-slate-100 hover:bg-slate-200 rounded"
              >
                Close Preview
              </button>
              <button
                type="button"
                onClick={() => window.print()}
                className="px-4 py-2 text-xs font-semibold text-white bg-slate-900 hover:bg-slate-800 rounded flex items-center gap-1.5"
              >
                <Printer className="w-3.5 h-3.5" />
                <span>Print Document</span>
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
