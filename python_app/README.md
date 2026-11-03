# Aegis Health — Desktop Edition

Aegis Health ka poora hospital-management dashboard ab **Python + CustomTkinter** desktop app ke roop mein hai. Original React web app bilkul untouched hai; naya code sirf `python_app/` folder ke andar rehta hai.

## Highlights

- **Native desktop GUI** — CustomTkinter, light clinical theme, dark navy sidebar.
- **SQLite persistence** — patients, beds, appointments, ER triage, pharmacy, labs, invoices aur doctors sab local database mein save hote hain.
- **Full workflow** — admission, OPD booking, ER triage, patient chart (vitals, notes, transfer, discharge), dispensation, formulary intake, lab requisitions/results, invoice builder, printable receipts.
- **Printable receipts** — receipt HTML browser mein khulti hai; wahin se print ya PDF save karein.
- **Global patient search** — header search (ya `Ctrl+K`) se patient registry filter hoti hai.
- **Reset demo data** — sidebar ke "Reset demo data" se original seed dataset wapas load hota hai.

## Quick start (Windows)

```bat
cd python_app
run.bat
```

`run.bat` pehli baar virtual environment banata hai, `customtkinter` install karta hai, aur app launch karta hai.

### Manual setup

```powershell
cd python_app
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

Python **3.10+** required hai (3.11 recommended).

## Modules

| Module | What it does |
| --- | --- |
| **Overview** | Live census, bed occupancy, ER triage queue, OPD roster, ward progress, inventory alerts |
| **Patients** | Searchable/filterable registry, full clinical chart, JSON export |
| **Beds** | Ward-wise bed cards, cleaning/maintenance cycle, transfer and admission |
| **Appointments** | OPD scheduling, check-in → consultation → completion workflow, doctor filter |
| **Pharmacy & Labs** | Formulary stock, dispense with stock reconciliation, add medicine, lab orders and signed results |
| **Billing** | Revenue KPIs, invoice filter/search, live line-item builder, printable receipts |
| **Doctors** | Consultant cards, duty toggle, inpatient counts, schedule jump |

## Patient chart

Double-click any patient row (or click a name on the dashboard) to open:
- Summary with latest vitals, diagnoses, care team, emergency contact, labs and notes
- Vitals history + new reading entry
- Clinical progress notes
- Bed transfer
- Discharge summary and bed release

## Data & persistence

- Database: `python_app/data/aegis_health.db`
- Seed data: `python_app/aegis/seed_data.json` (extracted from the original `src/data/mockData.ts`)
- Pehli run par database automatically seed hota hai.
- Database delete karke bhi fresh seed mil sakta hai; ya sidebar se **Reset demo data** use karein.
- `python_app/data/` aur `.venv/` gitignored hain.

## Project structure

```
python_app/
├─ main.py                     # launcher
├─ run.bat                     # one-click Windows start
├─ requirements.txt
├─ data/                       # SQLite database (created at runtime)
└─ aegis/
   ├─ app.py                   # main window, sidebar, header, routing, toasts
   ├─ theme.py                 # colours, fonts, geometry
   ├─ widgets.py               # cards, tables, filters, form helpers, base classes
   ├─ store.py                 # clinical/business rules + SQLite commits
   ├─ database.py              # schema and seeding
   ├─ utils.py                 # formatting helpers
   ├─ seed_data.json
   ├─ views/                   # seven module screens
   └─ dialogs/                 # admission, appointment, ER, chart, pharmacy, billing
```

## Notes

- Receipt print ke liye browser khulti hai. Wahan `Ctrl+P` se printer ya "Save as PDF" choose karein.
- Invoice builder mein patient select karne par standard charges auto-suggest hote hain; qty/rate edit kar sakte hain.
- Dispensation karne par stock automatically kam hota hai aur medicine record mein dispense log save hota hai.
- App offline chalti hai — koi server ya internet required nahi (sirf first-time pip install ke liye internet chahiye).
