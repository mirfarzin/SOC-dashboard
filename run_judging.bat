@echo off
TITLE PS02 Offline Security Incident Triage Assistant
powershell -ExecutionPolicy Bypass -File "%~dp0run_judging.ps1"
pause
