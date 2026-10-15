# Shared root resolver (docs/application/layout.md): install_root from bimbo-trener.json, or the installed app itself.
$script:OwnerTag = 'bimbo-trener/app/v1'

function Test-FullyQualifiedInstallPath {
    param([string]$Path)
    return $Path -match '^(?:[A-Za-z]:[\\/]|[\\/]{2}[^\\/]+[\\/][^\\/]+(?:[\\/]|$))'
}

function Read-ProjectConfig {
    param([string]$RepositoryRoot)
    $configPath = Join-Path $RepositoryRoot 'bimbo-trener.json'
    Assert-PlainPath -Path $configPath
    if (-not (Test-Path -LiteralPath $configPath)) { throw "Chyba bimbo-trener.json v $RepositoryRoot." }
    $config = [IO.File]::ReadAllText($configPath) | ConvertFrom-Json
    $localPath = Join-Path $RepositoryRoot 'bimbo-trener.local.json'
    Assert-PlainPath -Path $localPath
    if (Test-Path -LiteralPath $localPath) {
        $local = [IO.File]::ReadAllText($localPath) | ConvertFrom-Json
        foreach ($property in $local.PSObject.Properties) {
            if ($config.PSObject.Properties.Name -contains $property.Name) { $config.($property.Name) = $property.Value }
            else { $config | Add-Member -NotePropertyName $property.Name -NotePropertyValue $property.Value }
        }
    }
    return $config
}

function Resolve-InstallationRoot {
    param([string]$InstallDirectory = '', [string]$ScriptsDirectory = $PSScriptRoot)
    if (-not [string]::IsNullOrWhiteSpace($InstallDirectory)) {
        if (-not (Test-FullyQualifiedInstallPath -Path $InstallDirectory)) { throw 'InstallDirectory musi byt absolutna cesta.' }
        return [IO.Path]::GetFullPath($InstallDirectory)
    }
    $bundledRoot = Split-Path -Parent $ScriptsDirectory
    $marker = Join-Path $bundledRoot '.bimbo-trener-installer'
    Assert-PlainPath -Path $marker
    if (Test-Path -LiteralPath $marker) {
        if ([IO.File]::ReadAllText($marker).Trim() -ne $script:OwnerTag) { throw 'Adresar prikazov ma neznamu znacku vlastnika.' }
        return [IO.Path]::GetFullPath($bundledRoot)
    }
    $config = Read-ProjectConfig -RepositoryRoot $bundledRoot
    if ([string]::IsNullOrWhiteSpace($config.install_root)) { throw 'bimbo-trener.json musi obsahovat install_root.' }
    $root = [Environment]::ExpandEnvironmentVariables([string]$config.install_root)
    if (-not (Test-FullyQualifiedInstallPath -Path $root)) {
        if ($root -ne '../bimbo-trener-app') { throw 'Relativny install_root musi byt ../bimbo-trener-app.' }
        $root = Join-Path $bundledRoot $root
    }
    if ($root -match '%[^%]+%' -or -not (Test-FullyQualifiedInstallPath -Path $root)) { throw 'install_root musi byt absolutna cesta so znamymi premennymi prostredia.' }
    return [IO.Path]::GetFullPath($root)
}

function Assert-InstallationBoundary {
    param([string]$Root, [string]$ScriptsDirectory)
    $separator = [IO.Path]::DirectorySeparatorChar
    $full = [IO.Path]::GetFullPath($Root).TrimEnd($separator, [IO.Path]::AltDirectorySeparatorChar)
    if (Test-Path -LiteralPath (Join-Path $full '.git')) { throw 'Git repozitar nemoze byt instalacny adresar.' }
    $volume = [IO.Path]::GetPathRoot($full).TrimEnd($separator, [IO.Path]::AltDirectorySeparatorChar)
    if ($full -eq $volume) { throw 'Koren disku nemoze byt instalacny adresar.' }
    $repository = [IO.Path]::GetFullPath((Split-Path -Parent $ScriptsDirectory)).TrimEnd($separator, [IO.Path]::AltDirectorySeparatorChar)
    if ($full -eq $repository) {
        $marker = Join-Path $full '.bimbo-trener-installer'
        if (-not (Test-Path $marker) -or [IO.File]::ReadAllText($marker).Trim() -ne $script:OwnerTag) { throw 'Repozitar nemoze byt instalacny adresar.' }
        return
    }
    if ($full.StartsWith($repository + $separator, [StringComparison]::OrdinalIgnoreCase) -or
        $repository.StartsWith($full + $separator, [StringComparison]::OrdinalIgnoreCase)) {
        throw 'Instalacny adresar a repozitar sa nesmu prekryvat.'
    }
}

function Assert-DataDirectoryBoundary {
    param([string]$DataDirectory, [string]$Root, [string]$RepositoryRoot)
    if (-not (Test-FullyQualifiedInstallPath -Path $DataDirectory)) { throw 'Datovy adresar musi byt absolutna cesta.' }
    if ($DataDirectory.StartsWith('\\')) { throw 'Datovy adresar nesmie byt sietova cesta (UNC).' }
    $separator = [IO.Path]::DirectorySeparatorChar
    $data = [IO.Path]::GetFullPath($DataDirectory).TrimEnd($separator)
    foreach ($other in @($Root, $RepositoryRoot)) {
        $full = [IO.Path]::GetFullPath($other).TrimEnd($separator)
        if ($data -eq $full -or $data.StartsWith($full + $separator, [StringComparison]::OrdinalIgnoreCase) -or
            $full.StartsWith($data + $separator, [StringComparison]::OrdinalIgnoreCase)) {
            throw 'Datovy adresar sa nesmie prekryvat s aplikaciou ani s repozitarom.'
        }
    }
}
