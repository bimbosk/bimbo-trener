@echo off
setlocal
chcp 65001 >nul
cd /d "%TEMP%"
(
    powershell.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\setup.ps1" -Action uninstall %*
    if errorlevel 1 (
        echo Odinstalovanie Bimbo trenera vyzaduje pozornost.
        pause
        exit /b 1
    )
    pause
    exit /b 0
)
