@echo off
title AirGuard - Divide & Conquer Air Traffic Collision Threat Detector
echo =====================================================================
echo  AirGuard - Divide & Conquer Air Traffic Collision Threat Detector
echo  DAA Assignment 2 - Academic Simulation
echo =====================================================================
echo.
echo Launching AirGuard Application...
py -3.13 main.py
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Trying fallback launcher...
    python main.py
)
pause
