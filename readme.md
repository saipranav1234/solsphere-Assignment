🖥️ System Utility Project

A complete monitoring and management system consisting of:

Frontend (Admin Dashboard) – A web-based dashboard (React + Vite) for viewing machine reports, statuses, and configurations.

Backend (FastAPI) – REST API to receive and serve machine reports.

System Utility (Daemon + Executable) – A Python utility that runs as a daemon on client machines to collect system information.

📂 Project Structure
├── 📁 admin-dashboard/          # Frontend (React + Vite + TS)
├── 📁 system_utility_backend/   # FastAPI backend
└── 📁 system_utility_project/   # System utility + PyInstaller build

🚀 Setup & Usage
1️⃣ Backend (FastAPI)

📍 Location: system_utility_backend/

Install dependencies
cd system_utility_backend
python -m venv venv
source venv/bin/activate   # Linux/Mac
venv\Scripts\activate      # Windows

pip install -r requirements.txt

Run server
python -m uvicorn main:app --reload --host 127.0.0.1 --port 8001

2️⃣ System Utility (Daemon + Executable)

📍 Location: system_utility_project/

Run daemon
python -m system_utility.daemon

Build executable (Windows/Linux)
pyinstaller --onefile system_utility/main.py


Output will be available in dist/.

3️⃣ Frontend (Admin Dashboard)

📍 Location: admin-dashboard/

Install dependencies
cd admin-dashboard
npm install

Start development server
npm run dev

📦 Required Packages
Backend (FastAPI)

fastapi

uvicorn

pydantic

requests

psutil (for system stats collection)

📄 All listed in system_utility_backend/requirements.txt

System Utility (Daemon)

psutil

requests

schedule (if used for periodic checks)

pyinstaller (for building exe)

Frontend (Admin Dashboard)

React

Vite

TypeScript

axios (for API calls)

tailwindcss (if used for styling)

📄 All listed in admin-dashboard/package.json

🛠️ Features

System Utility (Daemon)

Collects system information (CPU, memory, disk, OS, encryption status, etc.)

Sends reports to backend periodically

Can be built into standalone executable

Backend (FastAPI)

REST API to receive machine reports

Stores machine data and serves it to frontend

Provides filtering & sorting

Frontend (Admin Dashboard)

Lists all reporting machines

Displays latest system values

Flags configuration issues (e.g., unencrypted disk, outdated OS)

Shows last check-in time

Provides filters & sorting (OS, status, etc.)

🧑‍💻 Development

Backend API runs on http://127.0.0.1:8001

Frontend calls backend via hardcoded API links inside code

Daemon periodically pushes data to backend