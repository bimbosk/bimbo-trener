# Shared installation session, bootstrap (uv + managed Python) and management actions. Mirrors the pattern of
# projektant-tzb: no global changes, verified owner marker, process lock, transcript, no symlinks or junctions.
$uvVersion = '0.12.24'
$managedPythonMinor = '3.14'
$ownerTag = 'bimbo-trener/app/v1'

function Invoke-Checked {
    param([string]$Program, [string[]]$Arguments)
    $previousErrorAction = $ErrorActionPreference
    $PSNativeCommandUseErrorActionPreference = $false
    $exitCode = $null
    try {
        $ErrorActionPreference = 'Continue'
        $global:LASTEXITCODE = $null
        & $Program @Arguments 2>&1 | ForEach-Object {
            if ($_ -is [Management.Automation.ErrorRecord]) {
                if ($_.FullyQualifiedErrorId -notin @('NativeCommandError', 'NativeCommandErrorMessage')) { throw $_ }
                Write-Host $_.ToString()
            } else { Write-Output $_ }
        }
        $exitCode = $global:LASTEXITCODE
    } finally { $ErrorActionPreference = $previousErrorAction }
    if ($null -eq $exitCode) { throw "Prikaz sa nespustil alebo nevratil navratovy kod: $Program" }
    if ($exitCode -ne 0) { throw "Prikaz zlyhal (kod $exitCode): $Program" }
}

function Assert-PlainPath {
    param([string]$Path)
    $current = [IO.Path]::GetFullPath($Path)
    while ($current) {
        if (Test-Path -LiteralPath $current) {
            if (((Get-Item -LiteralPath $current -Force).Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) {
                throw "Cesta nesmie viest cez symbolicky odkaz ani junction: $current"
            }
        }
        $parent = [IO.Directory]::GetParent($current)
        if ($null -eq $parent) { break }
        $current = $parent.FullName
    }
}

function Assert-PlainTree {
    param([string]$Path)
    Assert-PlainPath -Path $Path
    $pending = [Collections.Generic.Stack[string]]::new(); $pending.Push($Path)
    while ($pending.Count) {
        foreach ($item in @(Get-ChildItem -LiteralPath $pending.Pop() -Force -ErrorAction Stop)) {
            Assert-PlainPath -Path $item.FullName
            if ($item.PSIsContainer) { $pending.Push($item.FullName) }
        }
    }
}

function Remove-UvPythonMinorAlias {
    # uv creates a junction alias for the minor version; the app keeps a plain tree and uses the concrete version.
    param([string]$Root)
    $alias = Join-Path (Join-Path $Root 'runtime\python') ("cpython-$managedPythonMinor-windows-x86_64-none")
    $item = $null
    try { $item = Get-Item -LiteralPath $alias -Force -ErrorAction Stop } catch { return }
    if ($null -eq $item -or $item.LinkType -ne 'Junction') { return }
    [IO.Directory]::Delete($alias, $false)
}

function Ensure-LocalPython {
    param([string]$Uv, [string]$Root)
    Invoke-Checked -Program $Uv -Arguments @('python', 'install', $managedPythonMinor, '--managed-python', '--no-bin', '--no-registry') | Out-Host
    Remove-UvPythonMinorAlias -Root $Root
    $candidate = (Invoke-Checked -Program $Uv -Arguments @('python', 'find', $managedPythonMinor, '--managed-python', '--no-python-downloads', '--resolve-links') | Out-String).Trim()
    if (-not (Test-Path -LiteralPath $candidate)) { throw "Nepodarilo sa pripravit lokalny Python $managedPythonMinor." }
    Assert-PlainPath -Path $candidate
    if (-not $candidate.StartsWith(($Root.TrimEnd('\') + '\'), [StringComparison]::OrdinalIgnoreCase)) { throw 'Python musi byt v instalacnom adresari.' }
    return $candidate
}

function Open-InstallationSession {
    param([string]$InstallDirectory, [string]$Action, [string]$Component, [string]$ScriptsDirectory)
    $session = [pscustomobject]@{ Root = ''; RepositoryRoot = (Split-Path -Parent $ScriptsDirectory); ScriptsDirectory = $ScriptsDirectory
        LocationPushed = $false; LockStream = $null; TranscriptStarted = $false; SavedEnvironment = @{}; LogPath = ''; Mutex = $null }
    try {
        if ([Environment]::OSVersion.Platform -ne [PlatformID]::Win32NT) { throw 'Tento instalator vyzaduje nativny Windows.' }
        Push-Location $session.RepositoryRoot; $session.LocationPushed = $true
        if (-not [Environment]::Is64BitProcess) { throw 'Pouzite 64-bitovy Windows PowerShell.' }
        $principal = [Security.Principal.WindowsPrincipal]::new([Security.Principal.WindowsIdentity]::GetCurrent())
        if ($principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) { throw 'Spustite instalator bezne, nie ako spravca.' }
        $installRoot = Resolve-InstallationRoot -InstallDirectory $InstallDirectory -ScriptsDirectory $ScriptsDirectory
        Assert-InstallationBoundary -Root $installRoot -ScriptsDirectory $ScriptsDirectory
        $hash = [Security.Cryptography.SHA256]::Create()
        try { $key = [BitConverter]::ToString($hash.ComputeHash([Text.Encoding]::UTF8.GetBytes($installRoot.ToUpperInvariant()))).Replace('-', '') } finally { $hash.Dispose() }
        $session.Mutex = [Threading.Mutex]::new($false, ('Local\BimboTrener-' + $key))
        $acquired = $false
        try { $acquired = $session.Mutex.WaitOne(0) } catch [Threading.AbandonedMutexException] { $acquired = $true }
        if (-not $acquired) { throw 'Ina instalacia alebo sprava tejto app uz bezi.' }
        Assert-PlainPath -Path $installRoot
        $ownerFile = Join-Path $installRoot '.bimbo-trener-installer'
        if (Test-Path $installRoot) {
            if (-not (Test-Path $ownerFile)) {
                if (@(Get-ChildItem -LiteralPath $installRoot -Force).Count -gt 0) { throw 'Ciel obsahuje cudzie subory. Zvolte novy instalacny adresar.' }
            } elseif ([IO.File]::ReadAllText($ownerFile).Trim() -ne $ownerTag) { throw 'Adresar ma neznamu znacku vlastnika; nebude zmeneny.' }
            Assert-PlainTree -Path $installRoot
        }
        if ($Action -ne 'install' -and -not (Test-Path $ownerFile)) { throw 'Sprava vyzaduje existujucu instalaciu.' }
        New-Item -ItemType Directory -Force -Path $installRoot | Out-Null
        foreach ($directory in @('runtime', 'config', 'logs', 'sprava')) { New-Item -ItemType Directory -Force -Path (Join-Path $installRoot $directory) | Out-Null }
        $session.LockStream = [IO.File]::Open((Join-Path $installRoot 'sprava\instalacia.lock'), [IO.FileMode]::OpenOrCreate, [IO.FileAccess]::ReadWrite, [IO.FileShare]::None)
        [IO.File]::WriteAllText($ownerFile, $ownerTag)
        $logPath = Join-Path $installRoot ('logs\instalacia-' + (Get-Date -Format 'yyyyMMdd-HHmmss') + '.log')
        Start-Transcript -Path $logPath | Out-Null; $session.TranscriptStarted = $true
        Write-Host "Bimbo trener: $Action / $Component"
        Write-Host "Instalacny adresar: $installRoot"
        $environment = @{
            BIMBO_TRENER_ROOT = $installRoot
            UV_INSTALL_DIR = (Join-Path $installRoot 'runtime\bin'); UV_NO_MODIFY_PATH = '1'
            UV_UNMANAGED_INSTALL = (Join-Path $installRoot 'runtime\bin'); UV_PYTHON_ARCH = 'x86_64'
            UV_PYTHON_INSTALL_DIR = (Join-Path $installRoot 'runtime\python'); UV_PYTHON_BIN_DIR = (Join-Path $installRoot 'runtime\bin')
            UV_PYTHON_INSTALL_REGISTRY = '0'; UV_PYTHON_NO_REGISTRY = '1'; UV_PYTHON_INSTALL_BIN = '0'; UV_NO_CONFIG = '1'
            UV_PROJECT_ENVIRONMENT = ''; UV_PYTHON = ''; VIRTUAL_ENV = ''; PYTHONDONTWRITEBYTECODE = '1'
            TEMP = (Join-Path $installRoot 'runtime\temp'); TMP = (Join-Path $installRoot 'runtime\temp')
            UV_CACHE_DIR = (Join-Path $installRoot 'runtime\cache'); PYTHONUTF8 = '1'; PYTHONIOENCODING = 'utf-8'
        }
        foreach ($key in $environment.Keys) {
            $session.SavedEnvironment[$key] = [Environment]::GetEnvironmentVariable($key, 'Process')
            [Environment]::SetEnvironmentVariable($key, $environment[$key], 'Process')
        }
        New-Item -ItemType Directory -Force -Path $env:TEMP | Out-Null
        [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
        $session.Root = $installRoot; $session.LogPath = $logPath
        return $session
    } catch { Close-InstallationSession -Session $session; throw }
}

function Close-InstallationSession {
    param($Session)
    if ($null -eq $Session) { return }
    try {
        foreach ($key in $Session.SavedEnvironment.Keys) {
            if ($null -eq $Session.SavedEnvironment[$key]) { Remove-Item -LiteralPath ('Env:' + $key) -ErrorAction SilentlyContinue }
            else { [Environment]::SetEnvironmentVariable($key, $Session.SavedEnvironment[$key], 'Process') }
        }
        if ($Session.TranscriptStarted) { Stop-Transcript | Out-Null; $Session.TranscriptStarted = $false }
    } finally {
        if ($null -ne $Session.LockStream) { $Session.LockStream.Dispose(); $Session.LockStream = $null }
        if ($null -ne $Session.Mutex) { $Session.Mutex.ReleaseMutex(); $Session.Mutex.Dispose(); $Session.Mutex = $null }
        if ($Session.LocationPushed) { Pop-Location; $Session.LocationPushed = $false }
    }
}

function Install-CommonEnvironment {
    param($Session)
    $installRoot = $Session.Root
    $uv = Join-Path $installRoot 'runtime\bin\uv.exe'
    if (-not (Test-Path $uv)) {
        Write-Host '[Spolocne prostredie] Instalujem uv z oficialneho instalatora Astral...'
        $uvInstaller = Join-Path $installRoot 'runtime\uv-install.ps1'
        Invoke-WebRequest -UseBasicParsing -Uri "https://astral.sh/uv/$uvVersion/install.ps1" -OutFile $uvInstaller -TimeoutSec 120
        $nativePowerShell = Join-Path $env:SystemRoot 'System32\WindowsPowerShell\v1.0\powershell.exe'
        $previousModulePath = $env:PSModulePath
        try {
            $env:PSModulePath = Join-Path (Split-Path -Parent $nativePowerShell) 'Modules'
            Invoke-Checked -Program $nativePowerShell -Arguments @('-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', $uvInstaller) | Out-Host
        } finally { $env:PSModulePath = $previousModulePath }
    }
    if (-not (Test-Path $uv)) { throw 'Instalator uv nevytvoril ocakavany uv.exe.' }
    $actual = (Invoke-Checked -Program $uv -Arguments @('--version') | Out-String).Trim()
    if ($actual -notmatch ('^uv ' + [regex]::Escape($uvVersion) + '(\s|$)')) { throw "Neocakavana verzia uv: $actual" }
    Write-Host '[Spolocne prostredie] Lokalny Python...'
    $python = Ensure-LocalPython -Uv $uv -Root $installRoot
    Publish-InstallationScripts -Root $installRoot -RepositoryRoot $Session.RepositoryRoot
    return [pscustomobject]@{ Root = $installRoot; RepositoryRoot = $Session.RepositoryRoot; Uv = $uv; WorkstationPython = $python }
}

function Publish-InstallationScripts {
    # Whole scripts tree plus launchers and configuration, replaced through a staging directory.
    param([string]$Root, [string]$RepositoryRoot)
    $target = Join-Path $Root 'scripts'
    $stage = Join-Path $Root ('sprava\scripts-stage-' + [guid]::NewGuid().ToString('N'))
    $source = Join-Path $RepositoryRoot 'scripts'
    Assert-PlainPath -Path $target; Assert-PlainPath -Path $stage
    Get-ChildItem -LiteralPath $source -File -Recurse | Where-Object {
        $_.Extension -in @('.py', '.ps1', '.json', '.lock', '.in') -and $_.FullName -notmatch '[\\/](__pycache__|tests)[\\/]'
    } | ForEach-Object {
        Assert-PlainPath -Path $_.FullName
        $relative = $_.FullName.Substring($source.Length).TrimStart('\', '/')
        $destination = Join-Path $stage $relative
        New-Item -ItemType Directory -Force -Path (Split-Path -Parent $destination) | Out-Null
        Copy-Item -LiteralPath $_.FullName -Destination $destination
    }
    if (Test-Path -LiteralPath $target) {
        $previous = Join-Path $Root ('sprava\scripts-previous-' + (Get-Date -Format 'yyyyMMdd-HHmmss'))
        Move-Item -LiteralPath $target -Destination $previous
    }
    Move-Item -LiteralPath $stage -Destination $target
    foreach ($file in @('install.cmd', 'uninstall.cmd', 'sync.cmd', 'bimbo-trener.json')) {
        Copy-Item -LiteralPath (Join-Path $RepositoryRoot $file) -Destination (Join-Path $Root $file) -Force
    }
    $local = Join-Path $RepositoryRoot 'bimbo-trener.local.json'
    if (Test-Path -LiteralPath $local) { Copy-Item -LiteralPath $local -Destination (Join-Path $Root 'bimbo-trener.local.json') -Force }
}

function Invoke-EnvironmentManagement {
    param($Session, [string]$Action)
    $installRoot = $Session.Root
    $python = Join-Path $installRoot 'runtime\venv\Scripts\python.exe'
    if ($Action -eq 'reset-runtime') {
        if (Test-Path $python) { Invoke-Checked -Program $python -Arguments @('-m', 'scripts.lifecycle', 'unregister', '--root', $installRoot) | Out-Host }
        $runtime = Join-Path $installRoot 'runtime'
        if (Test-Path $runtime) { Assert-PlainTree -Path $runtime; Remove-Item -LiteralPath $runtime -Recurse -Force }
        Write-Host 'Runtime odstraneny. Obnovte ho cez install.cmd; config, logy a sprava zostali; datovy adresar sa nedotkol.'
        return
    }
    if ($Action -eq 'uninstall') {
        if (Test-Path $python) {
            Invoke-Checked -Program $python -Arguments @('-m', 'scripts.lifecycle', 'unregister', '--root', $installRoot) | Out-Host
            Invoke-Checked -Program $python -Arguments @('-c', 'from scripts.coach import task; print(task.disable())') | Out-Host
        }
        Remove-OwnedShortcut -Root $installRoot
        Stop-Transcript | Out-Null; $Session.TranscriptStarted = $false
        $Session.LockStream.Dispose(); $Session.LockStream = $null
        if ($Session.LocationPushed) { Pop-Location; $Session.LocationPushed = $false }
        $parent = [IO.Path]::GetDirectoryName($installRoot.TrimEnd('\'))
        $retained = Join-Path $parent ('.' + [IO.Path]::GetFileName($installRoot.TrimEnd('\')) + '-uninstalled-' + [guid]::NewGuid().ToString('N'))
        Move-Item -LiteralPath $installRoot -Destination $retained -ErrorAction Stop
        Write-Host "Integracie odpojene. Aplikacia je zachovana na obnovu: $retained"
        Write-Host 'Datovy adresar (behy, databaza, zalohy) sa nedotkol. Token Garminu je v presunutej app; po kontrole ho zmazte.'
    }
}

function Remove-OwnedShortcut {
    param([string]$Root)
    $manifest = Join-Path $Root 'sprava\shortcut.json'
    if (-not (Test-Path -LiteralPath $manifest)) { return }
    $entry = Get-Content -LiteralPath $manifest -Raw -Encoding UTF8 | ConvertFrom-Json
    $link = [string]$entry.path
    Assert-PlainPath -Path $link
    if ((Test-Path -LiteralPath $link) -and (Get-FileHash -LiteralPath $link -Algorithm SHA256).Hash -eq $entry.sha256) {
        Remove-Item -LiteralPath $link
    } elseif (Test-Path -LiteralPath $link) {
        Write-Host "Skratka bola zmenena pouzivatelom; ponechana: $link"
    }
    Remove-Item -LiteralPath $manifest
}
