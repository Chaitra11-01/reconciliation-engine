# Cross-System Reconciliation Engine

A full-stack reconciliation application built for the AdosX Engineering take-home assignment.

The application imports records from two systems, handles intentionally dirty data, identifies discrepancies, enforces tenant isolation, and provides a React interface for reviewing the results.

## Tech Stack

- Backend: Django
- Frontend: React + Vite
- Database: SQLite
- Language: Python / JavaScript
- API: Django JSON endpoints

## Project Structure

```text
reconciliation-engine/
├── backend/
│   ├── core/
│   ├── reconciler/
│   └── manage.py
├── frontend/
├── data/
│   ├── system_a.csv
│   ├── system_b.csv
│   └── locations.csv
├── DECISIONS.md
└── README.md