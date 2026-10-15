@echo off
setlocal
chcp 65001 >nul
rem Keep the parent cmd process outside the directory that uninstall may relocate.
cd /d "%TEMP%"
(
    powershell.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\setup.ps1" %*
    if errorlevel 1 (
        echo Instalacia Bimbo trenera vyzaduje pozornost.
        pause
        exit /b 1
    )
    pause
    exit /b 0
)
