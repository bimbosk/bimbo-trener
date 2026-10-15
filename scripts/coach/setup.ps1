# Coach component: venv from the hash-pinned lock, data directory (dialog), Python setup (schema, probes, MCP
# registration), desktop shortcut to sync.cmd; optional `sync` component: Garmin login and the daily task.
function Prepare-CoachRuntime {
    param($Context)
    $venv = Join-Path $Context.Root 'runtime\venv'
    Assert-PlainPath -Path $venv
    if (-not (Test-Path -LiteralPath (Join-Path $venv 'Scripts\python.exe'))) {
        Invoke-Checked -Program $Context.Uv -Arguments @('venv', '--python', $Context.WorkstationPython, '--no-python-downloads', $venv) | Out-Host
    }
    $python = Join-Path $venv 'Scripts\python.exe'
    $lock = Join-Path $Context.RepositoryRoot 'scripts\requirements.lock'
    Invoke-Checked -Program $Context.Uv -Arguments @('pip', 'install', '--python', $python, '--require-hashes', '--no-deps', '-r', $lock) | Out-Host
    return $python
}

function Select-DataDirectory {
    param($Context, [string]$DataDirectory)
    if (-not [string]::IsNullOrWhiteSpace($DataDirectory)) { return [IO.Path]::GetFullPath($DataDirectory) }
    $config = Read-ProjectConfig -RepositoryRoot $Context.RepositoryRoot
    $configured = [Environment]::ExpandEnvironmentVariables([string]$config.data_dir)
    if ($configured -and (Test-Path -LiteralPath (Join-Path $configured 'bimbo-data.json'))) { return [IO.Path]::GetFullPath($configured) }
    Add-Type -AssemblyName System.Windows.Forms
    $dialog = New-Object System.Windows.Forms.FolderBrowserDialog
    $dialog.Description = 'Vyberte datovy adresar Bimbo trenera (synchronizovany priecinok, napr. D:\Sync\Bimbo-data). Existujuci sa pripoji, prazdny sa vytvori.'
    $dialog.ShowNewFolderButton = $true
    if ($configured) { $dialog.SelectedPath = $configured }
    if ($dialog.ShowDialog() -ne [System.Windows.Forms.DialogResult]::OK) { throw 'Datovy adresar nebol vybrany; instalacia zastavena.' }
    return [IO.Path]::GetFullPath($dialog.SelectedPath)
}

function Install-CoachShortcut {
    param([string]$Root)
    $manifest = Join-Path $Root 'sprava\shortcut.json'
    $link = Join-Path ([Environment]::GetFolderPath('DesktopDirectory')) 'Stiahni data z Garminu.lnk'
    Assert-PlainPath -Path $link; Assert-PlainPath -Path $manifest
    if ((Test-Path -LiteralPath $link) -and -not (Test-Path -LiteralPath $manifest)) { throw 'Skratka na ploche uz existuje a nepatri tomuto instalatoru.' }
    $shell = New-Object -ComObject WScript.Shell
    try {
        $temporary = Join-Path $Root 'runtime\shortcut-pending.lnk'
        $shortcut = $shell.CreateShortcut($temporary)
        $shortcut.TargetPath = Join-Path $Root 'sync.cmd'
        $shortcut.WorkingDirectory = $Root
        $shortcut.Description = 'Bimbo trener: stiahnutie novych dat z Garmin Connect'
        $shortcut.IconLocation = "$env:WINDIR\System32\shell32.dll,238"
        $shortcut.Save()
        @{ path = $link; sha256 = (Get-FileHash -LiteralPath $temporary -Algorithm SHA256).Hash } | ConvertTo-Json | Set-Content -LiteralPath $manifest -Encoding UTF8
        Copy-Item -LiteralPath $temporary -Destination $link -Force
        Remove-Item -LiteralPath $temporary
    } finally { [Runtime.InteropServices.Marshal]::ReleaseComObject($shell) | Out-Null }
}

function Install-CoachComponent {
    param($Context, [string]$Selected, [string]$DataDirectory = '')
    if ($Selected -notin @('all', 'coach', 'sync')) { return }
    $python = Prepare-CoachRuntime -Context $Context
    $dataDirectory = Select-DataDirectory -Context $Context -DataDirectory $DataDirectory
    Assert-DataDirectoryBoundary -DataDirectory $dataDirectory -Root $Context.Root -RepositoryRoot $Context.RepositoryRoot
    Push-Location $Context.Root
    try {
        Invoke-Checked -Program $python -Arguments @('-m', 'scripts.coach.setup', '--root', $Context.Root, '--repo', $Context.RepositoryRoot, '--data-dir', $dataDirectory) | Out-Host
    } finally { Pop-Location }
    # The data dir may have been written into bimbo-trener.local.json of both roots; refresh the app copy.
    $local = Join-Path $Context.RepositoryRoot 'bimbo-trener.local.json'
    if (Test-Path -LiteralPath $local) { Copy-Item -LiteralPath $local -Destination (Join-Path $Context.Root 'bimbo-trener.local.json') -Force }
    Install-CoachShortcut -Root $Context.Root
    return 'coach'
}

function Install-SyncComponent {
    param($Context, [string]$Selected)
    if ($Selected -ne 'sync') { return }
    $python = Join-Path $Context.Root 'runtime\venv\Scripts\python.exe'
    Write-Host 'Prihlasenie do Garmin Connect: zadajte e-mail, heslo (nezobrazuje sa) a MFA kod.'
    Push-Location $Context.Root
    try {
        Invoke-Checked -Program $python -Arguments @('-m', 'scripts.coach.cli', '--root', $Context.Root, 'login') | Out-Host
        $tokenDir = Join-Path $Context.Root 'config\garmin'
        if (Test-Path -LiteralPath $tokenDir) {
            $sid = [Security.Principal.WindowsIdentity]::GetCurrent().User.Value
            & icacls.exe $tokenDir /inheritance:r /grant:r "*$($sid):(OI)(CI)F" | Out-Null
        }
        foreach ($root in @($Context.RepositoryRoot, $Context.Root)) {
            Invoke-Checked -Program $python -Arguments @('-c', "from pathlib import Path; from scripts.coach.config import write_local_override; write_local_override(Path(r'$root'), {'garmin_sync_enabled': True})") | Out-Host
        }
        $config = Read-ProjectConfig -RepositoryRoot $Context.RepositoryRoot
        $at = if ($config.sync -and $config.sync.daily_task_time) { [string]$config.sync.daily_task_time } else { '07:30' }
        $syncCmd = Join-Path $Context.Root 'sync.cmd'
        Invoke-Checked -Program $python -Arguments @('-c', "from scripts.coach import task; print(task.enable(r'$syncCmd', r'$($Context.Root)', '$at'))") | Out-Host
    } finally { Pop-Location }
    return 'sync'
}
