@echo off
title MAD Lab SQL Database - Live Chrome Dashboard
color 0B
echo ====================================================================
echo      MAD LAB - EXPERIMENT 5 DATABASE LOCALHOST SYNC DASHBOARD
echo ====================================================================
echo.

echo [1/3] Enabling ADB reverse port forwarding (Phone -^> Laptop)...
adb reverse tcp:5000 tcp:5000 >nul 2>&1
if %errorlevel% equ 0 (
    echo   [OK] Phone is bridged to Laptop via ADB reverse tcp:5000
) else (
    echo   [INFO] Phone wireless or Wi-Fi mode active (Endpoint: http://10.98.74.31:5000)
)

echo.
echo [2/3] Launching Google Chrome to http://localhost:5000 ...
start "" "http://localhost:5000"

echo.
echo [3/3] Starting Local Python SQL Database Sync Server on port 5000...
echo ====================================================================
echo  Press Ctrl+C to stop the server anytime.
echo ====================================================================
python "C:\Users\gokularun\Projects\mad-lab-sync-dashboard\server.py"
pause
