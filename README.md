# GradeLens-AI (MemoScan AI)
### Automated Marks Memo Extraction, Verification, & Academic Analytics Engine

[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Next.js](https://img.shields.io/badge/Frontend-Next.js%2016-black?logo=next.js&logoColor=white)](https://nextjs.org)
[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white)](https://python.org)
[![React](https://img.shields.io/badge/React-19-61DAFB?logo=react&logoColor=black)](https://react.dev)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

**GradeLens-AI** is a high-performance academic intelligence system designed for universities and autonomous colleges. It automatically ingests single marks memos, multi-page semester transcripts, class gazettes, and bulk ZIP archives, extracts student scores and subject marks, cross-verifies calculations, flags anomalies for reviewer approval, and exports institutional 5-sheet consolidated Excel workbooks in seconds.

---

## 🌟 Key Capabilities

- **⚡ Smarter & Faster Ingestion**: Drag-and-drop batch processing for PDFs, PNGs, and JPEGs with real-time processing bars.
- **🏛️ Multi-University Parsers**: Out-of-the-box regex and tabular extractors for JNTU (R18/R20/R22), Anna University, autonomous colleges, and general tabulation gazettes.
- **🔍 Hybrid OCR & Digital Engine**: Ultra-fast PyMuPDF text parsing for digital grade sheets, seamlessly falling back to Tesseract OCR with adaptive image preprocessing for low-resolution scanned memos.
- **🛡️ Academic Discrepancy Auditing**: Automatic weighted credit checks comparing extracted SGPA against actual subject marks. Discrepancies are queued with side-by-side verification and original PDF preview.
- **📊 Interactive Institutional Analytics**: Stacked pass/fail/backlog progression charts, branch performance comparisons, and grade frequency leaderboards.
- **📁 5-Sheet Consolidated Excel Export**:
  1. **Student Details**: Master student list with SGPA, CGPA, total backlogs, and verification status.
  2. **Subject Marks**: Granular course rows with internal, external, credits, and grade points.
  3. **Backlogs**: Active uncleared courses flagged for remedial scheduling.
  4. **Summary**: Institutional KPI aggregations.
  5. **Processing Issues**: Full extraction audit log.
- **🔒 Privacy & Local Execution**: Runs 100% locally with zero cloud dependencies or external API fees. Includes one-click data purge compliance.

---

## 🏗️ System Architecture

```
                                  [ Upload Marks Memos ]
                                (PDF / JPG / PNG / ZIP)
                                           │
                                           ▼
                            ┌──────────────────────────────┐
                            │   Hybrid Extraction Engine   │
                            ├──────────────────────────────┤
                            │  1. PyMuPDF Digital Parser   │
                            │  2. OpenCV Image Denoiser    │
                            │  3. Tesseract OCR Fallback   │
                            └──────────────┬───────────────┘
                                           │
                                           ▼
                            ┌──────────────────────────────┐
                            │  Academic Audit & Calculator │
                            ├──────────────────────────────┤
                            │ • SGPA = Σ(Credits × Points) │
                            │ • Cross-Check Integrity      │
                            │ • Backlog Clearance Tracking │
                            └──────────────┬───────────────┘
                                           │
                     ┌─────────────────────┴─────────────────────┐
                     ▼                                           ▼
        [ Verification Review Queue ]                  [ SQLite / PostgreSQL ]
         Side-by-side approval & edit                   Persistent Normalized Store
                     │                                           │
                     └─────────────────────┬─────────────────────┘
                                           ▼
                            ┌──────────────────────────────┐
                            │     Presentation Layer       │
                            ├──────────────────────────────┤
                            │ • Next.js 16 Dashboard UI    │
                            │ • Multi-Tab Analytics        │
                            │ • 5-Sheet Excel Generator    │
                            └──────────────────────────────┘
```

---

## 🚀 Quick Start Guide

### 1. Prerequisites
- **Python 3.11+**
- **Node.js 18+** & npm
- *(Optional for Scanned Images)* **Tesseract OCR**: Windows default `C:\Program Files\Tesseract-OCR\tesseract.exe`.

---

### 2. Backend Setup

```bash
cd backend

# Create and activate virtual environment
python -m venv venv
# Windows:
.\venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start backend server
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```
API documentation is accessible at **`http://127.0.0.1:8000/docs`**.

---

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start Next.js development server
npm run dev
```
Open **`http://localhost:3000`** in your browser.

---

### 4. Running Verification Test Suite

```bash
cd backend

# Run all 13 unit & integration tests
pytest

# Run end-to-end multi-memo verification pipeline
python tests/e2e_runner.py
```

---

## 📂 Repository Structure

```
GradeLens-AI/
├── backend/
│   ├── app/
│   │   ├── analytics/        # GPA/CGPA calculators & metrics
│   │   ├── export/           # 5-Sheet Excel workbook generator
│   │   ├── extractor/        # PyMuPDF, OCR & university parsers
│   │   ├── routers/          # REST API endpoints (upload, review, students, etc.)
│   │   ├── config.py         # App configuration & paths
│   │   ├── database.py       # SQLAlchemy engine & session factory
│   │   ├── models.py         # Relational database models
│   │   ├── schemas.py        # Pydantic validation schemas
│   │   └── main.py           # FastAPI entrypoint
│   ├── tests/                # Pytest suite & E2E verification runner
│   ├── sample_generator.py   # Synthetic marks memo generator
│   └── requirements.txt      # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── app/              # Next.js 16 app layout & page
│   │   ├── components/       # Dashboard, Review, Students, Analytics tabs
│   │   └── lib/              # API clients & TypeScript types
│   ├── package.json
│   └── tsconfig.json
├── sample_memos/             # Test memos (JNTU, Anna Univ, Gazettes)
├── .gitignore
└── README.md
```

---

## 📄 License
This project is licensed under the [MIT License](LICENSE).
