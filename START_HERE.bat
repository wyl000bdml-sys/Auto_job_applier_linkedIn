@echo off
title LinkedIn Job Assistant - Beginner Setup
cd /d "%~dp0"
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0setup-for-beginners.ps1"
if errorlevel 1 (
  echo.
  echo Setup stopped because an item needs attention.
)
pause
