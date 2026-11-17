# MAD Lab Experiment 5 - Localhost Chrome Sync Dashboard & SQL Database

A real-time database synchronization system connecting Android mobile applications (MAD Lab Experiment 5: SQLite Database) to a live local Chrome browser dashboard running on localhost and local Wi-Fi.

## Architecture
- **Mobile Client**: Android Java app with local SQLite (`EmployeeDB.db`) + automatic background HTTP sync engine.
- **Backend Server**: Python Flask REST API running on `localhost:5000` / `0.0.0.0:5000` with SQLite database (`mad_records.db`).
- **Web Dashboard**: Modern, real-time glassmorphism Chrome dashboard showing live order of details, currency formatting, auto-refresh (1.5s), manual add/edit/delete, and CSV/PDF export.
- **Dual Bridge**: Seamless connectivity via ADB reverse port-forwarding (`tcp:5000`) and local Wi-Fi fallback.

## Quick Start
1. Double-click `RUN_DASHBOARD.bat` (or `START_MAD_DASHBOARD.bat` from Downloads).
2. It sets up the port bridge, starts the Python server, and opens Chrome directly to `http://localhost:5000`.
3. Open Experiment 5 on your Android phone, enter details, and tap **ADD**.
4. The record immediately saves to the phone's SQLite database AND appears live on your laptop's Chrome dashboard!
