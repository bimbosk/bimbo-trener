# sync.cmd -> this script: runs `cli sync` from the installed app, shows progress, closes after 3 s on success.
[CmdletBinding()]
param([switch]$Quiet)
$ErrorActionPreference = 'Stop'
. (Join-Path $PSScriptRoot 'common\setup.ps1')
. (Join-Path $PSScriptRoot 'install-paths.ps1')
$code = 1
try {
    $root = Resolve-InstallationRoot -ScriptsDirectory $PSScriptRoot
    $python = Join-Path $root 'runtime\venv\Scripts\python.exe'
    if (-not (Test-Path -LiteralPath $python)) { throw "Aplikacia nie je nainstalovana ($root). Spustite install.cmd." }
    Write-Host 'Stahujem data z Garminu...'
    Push-Location $root
    try {
        $env:PYTHONUTF8 = '1'; $env:PYTHONIOENCODING = 'utf-8'
        # Progress lines arrive on stderr, the JSON result on stdout; both are shown, the result is parsed.
        $output = & $python -m scripts.coach.cli --root $root --compact sync 2>&1 | ForEach-Object {
            if ($_ -is [Management.Automation.ErrorRecord]) { Write-Host $_.ToString(); $null } else { $_ }
        } | Where-Object { $_ }
        $code = $LASTEXITCODE
    } finally { Pop-Location }
    $json = ($output | Select-Object -Last 1)
    $message = ''
    if ($json) { try { $message = ([string]$json | ConvertFrom-Json).message } catch { $message = [string]$json } }
    if ($code -eq 0) {
        Write-Host ("HOTOVO: " + $message) -ForegroundColor Green
        if (-not $Quiet) { Start-Sleep -Seconds 3 }
    } else {
        Write-Host ("NEPODARILO SA (kod $code): " + $message) -ForegroundColor Red
        if ($code -eq 77) { Write-Host 'Na tomto pocitaci nie je stahovanie nastavene alebo vyprsalo prihlasenie: install.cmd -Component sync' }
        if ($code -eq 75) { Write-Host 'Garmin docasne odmieta; pockajte uvedeny cas, nic neopakujte hned.' }
        if (-not $Quiet) { Read-Host 'Stlacte Enter na zatvorenie' | Out-Null }
    }
} catch {
    Write-Host ('CHYBA: ' + $_.Exception.Message) -ForegroundColor Red
    if (-not $Quiet) { Read-Host 'Stlacte Enter na zatvorenie' | Out-Null }
    $code = 1
}
exit $code
