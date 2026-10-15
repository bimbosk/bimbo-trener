@echo off
setlocal
chcp 65001 >nul
rem Stiahne nove data z Garmin Connect a importuje ich; okno ukaze priebeh a pri uspechu sa po 3 s zavrie.
powershell.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\sync.ps1" %*
exit /b %errorlevel%
