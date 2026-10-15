# Orchestrator only: shared session, then one call per component (docs/application/installation.md).
[CmdletBinding()]
param([string]$InstallDirectory = '', [string]$DataDirectory = '',
    [ValidateSet('all', 'common', 'coach', 'sync')][string]$Component = 'all',
    [ValidateSet('install', 'uninstall', 'reset-runtime')][string]$Action = 'install')

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$ProgressPreference = 'SilentlyContinue'

. (Join-Path $PSScriptRoot 'common\setup.ps1')
. (Join-Path $PSScriptRoot 'install-paths.ps1')
. (Join-Path $PSScriptRoot 'coach\setup.ps1')

$session = $null
$resultCode = 1
try {
    $session = Open-InstallationSession -InstallDirectory $InstallDirectory -Action $Action -Component $Component -ScriptsDirectory $PSScriptRoot
    if ($Action -eq 'install') {
        $context = Install-CommonEnvironment -Session $session
        $installed = @(
            Install-CoachComponent -Context $context -Selected $Component -DataDirectory $DataDirectory
            Install-SyncComponent -Context $context -Selected $Component
        )
        if ($Component -notin @('all', 'common') -and $installed -notcontains $Component) { throw "Komponent $Component nema instalacne volanie." }
        Write-Host ''
        Write-Host 'HOTOVO. Zatvorte a znova otvorte Claude Code / Codex, aby nacitali server bimbo_trener.' -ForegroundColor Green
        Write-Host "Logy a evidencia: $($session.Root)"
        if ($Component -ne 'sync') { Write-Host 'Stahovanie z Garminu zapnete na tomto PC cez: install.cmd -Component sync' }
    } else {
        Invoke-EnvironmentManagement -Session $session -Action $Action
    }
    $resultCode = 0
} catch {
    Write-Host ('NASTAVENIE ZLYHALO: ' + $_.Exception.Message) -ForegroundColor Red
    Write-Host 'Odstrante uvedenu pricinu a spustite rovnaky instalator znova.'
    if ($null -ne $session -and $session.TranscriptStarted) { Write-Host "Log: $($session.LogPath)" }
} finally { Close-InstallationSession -Session $session }
exit $resultCode
