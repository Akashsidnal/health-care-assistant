@echo off
title MediCare Cloud - Smart Healthcare Monitoring System
color 0B

echo ===============================================================================
echo                MEDICARE CLOUD - SMART HEALTHCARE MONITORING SYSTEM
echo             Dept. of Information Science & Engineering, CEC Bengaluru
echo ===============================================================================
echo.

cd /d "C:\Users\AKASH N SIDNAL\MediCareCloud\backend"

echo [*] Initializing database and preloaded demo records...
python seed_data.py
echo.

echo [*] Launching MediCare Cloud Server on 0.0.0.0:5000...
echo.
echo ===============================================================================
echo   ACCESS URLS:
echo   Local Browser : http://127.0.0.1:5000
echo   Phone/Tablet  : http://192.168.0.102:5000  (on same Wi-Fi)
echo.
echo   DEMO LOGIN ACCOUNTS (or click 1-Click buttons on screen):
echo   - Physician / Doctor : doctor@smarthealth.demo  ^| Pass: password123
echo   - Patient            : patient@smarthealth.demo ^| Pass: password123
echo ===============================================================================
echo.

start "" "http://127.0.0.1:5000/login"

python run.py

pause
