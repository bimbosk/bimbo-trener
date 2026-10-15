# Ako začať na novom počítači

- Potrebujem **Windows 11**, internet a GitHub účet s prístupom do repozitára
  `bimbosk/bimbo-trener` (repozitár je súkromný).
- V Prieskumníkovi otvorím priečinok, kam chcem projekt uložiť, napr. `D:\Beh`.
- Do adresného riadka napíšem **powershell** a stlačím **Enter**. Nespúšťam ho ako správca.
- Skopírujem a vložím celý blok nižšie. Potvrdím prípadnú inštaláciu nástrojov.
- Skript nainštaluje **Git, GitHub CLI a GitHub Desktop** a vytvorí priečinok
  **bimbo-trener**. Inštalátor projektu (`install.cmd`) nespustí; ten je ďalší krok.

```powershell
& {
    $ErrorActionPreference = 'Stop'
    try {
        if ($env:OS -ne 'Windows_NT') {
            throw 'Tento postup je urceny pre Windows.'
        }
        if ((Get-Location).Provider.Name -ne 'FileSystem') {
            throw 'Najprv otvorte PowerShell v beznom priecinku na disku.'
        }

        $target = Join-Path (Get-Location).Path 'bimbo-trener'
        if (Test-Path -LiteralPath $target) {
            throw "Ciel uz existuje: $target. Nic sa neprepise. Ak je to stiahnuty projekt, otvorte ho v asistentovi; inak zvolte iny nadradeny priecinok."
        }

        function Refresh-ToolPath {
            $machinePath = [Environment]::GetEnvironmentVariable('Path', 'Machine')
            $userPath = [Environment]::GetEnvironmentVariable('Path', 'User')
            $env:Path = "$env:Path;$machinePath;$userPath"
        }

        function Run-Checked {
            param([string]$Program, [string[]]$Arguments)
            & $Program @Arguments
            if ($LASTEXITCODE -ne 0) {
                throw "Prikaz $Program zlyhal (kod $LASTEXITCODE). Dalsie kroky sa nespustia."
            }
        }

        function Get-DesktopPath {
            $desktopCommand = Get-Command GitHubDesktop.exe -CommandType Application -ErrorAction SilentlyContinue
            if ($desktopCommand) { return $desktopCommand.Source }
            $desktopPath = Join-Path $env:LOCALAPPDATA 'GitHubDesktop\GitHubDesktop.exe'
            if (Test-Path -LiteralPath $desktopPath -PathType Leaf) { return $desktopPath }
            return $null
        }

        Refresh-ToolPath
        foreach ($tool in @(
            @{ Name = 'git.exe'; Package = 'Git.Git' }
            @{ Name = 'gh.exe'; Package = 'GitHub.cli' }
        )) {
            if (-not (Get-Command $tool.Name -CommandType Application -ErrorAction SilentlyContinue)) {
                $winget = Get-Command winget.exe -CommandType Application -ErrorAction SilentlyContinue
                if (-not $winget) {
                    throw 'Chyba winget. V Microsoft Store nainstalujte alebo aktualizujte App Installer, zatvorte PowerShell a tento postup zopakujte.'
                }
                Write-Host "Instalujem $($tool.Package)..."
                Run-Checked -Program $winget.Source -Arguments @(
                    'install', '--id', $tool.Package, '--exact', '--source', 'winget'
                )
                Refresh-ToolPath
                if (-not (Get-Command $tool.Name -CommandType Application -ErrorAction SilentlyContinue)) {
                    throw "Nastroj $($tool.Name) este nie je dostupny. Zatvorte PowerShell, otvorte ho znova v rovnakom priecinku a zopakujte tento blok."
                }
            }
        }

        $desktop = Get-DesktopPath
        if (-not $desktop) {
            $winget = Get-Command winget.exe -CommandType Application -ErrorAction SilentlyContinue
            if (-not $winget) {
                throw 'Chyba winget. V Microsoft Store nainstalujte alebo aktualizujte App Installer a postup zopakujte.'
            }
            Write-Host 'Instalujem GitHub Desktop...'
            Run-Checked -Program $winget.Source -Arguments @(
                'install', '--id', 'GitHub.GitHubDesktop', '--exact', '--source', 'winget', '--scope', 'user'
            )
            Refresh-ToolPath
            $desktop = Get-DesktopPath
            if (-not $desktop) {
                throw 'GitHub Desktop sa nepodarilo najst v pouzivatelskom priecinku ani v PATH. Odovzdajte spravcovi vystup instalacie.'
            }
        }

        $git = (Get-Command git.exe -CommandType Application).Source
        $gh = (Get-Command gh.exe -CommandType Application).Source
        Run-Checked -Program $git -Arguments @('--version')
        Run-Checked -Program $gh -Arguments @('--version')

        # Windows PowerShell 5.1 nesmie ukoncit blok pri stderr z neprihlaseneho gh.
        $ErrorActionPreference = 'Continue'
        try {
            & $gh auth status --hostname github.com --active *> $null
            $authCode = $LASTEXITCODE
        }
        finally { $ErrorActionPreference = 'Stop' }
        if ($authCode -ne 0) {
            Write-Host 'Prihlaste sa do GitHubu. Kod z tohto okna zadajte v prehliadaci a potvrdte pristup.'
            Run-Checked -Program $gh -Arguments @(
                'auth', 'login', '--hostname', 'github.com', '--git-protocol', 'https', '--web'
            )
        }
        Run-Checked -Program $gh -Arguments @('auth', 'setup-git', '--hostname', 'github.com')

        Write-Host "Stahujem projekt do: $target"
        Run-Checked -Program $git -Arguments @(
            'clone', '--', 'https://github.com/bimbosk/bimbo-trener.git', $target
        )
        foreach ($item in @('.git', 'README.md', 'docs', 'HOW_TO_USE.md')) {
            if (-not (Test-Path -LiteralPath (Join-Path $target $item))) {
                throw "Po stiahnuti chyba ocakavana polozka: $item"
            }
        }

        Write-Host 'Repozitar je stiahnuty. Otvaram GitHub Desktop...'
        Start-Process -FilePath $desktop
        Write-Host 'V GitHub Desktope dokoncite uvodne nastavenie a Sign in to GitHub.com cez prehliadac.'
        Write-Host 'Pouzite rovnaky ucet ako pri stahovani. Ak ste uz prihlaseni, pokracujte.'
        $null = Read-Host 'Ked ste v hlavnom okne GitHub Desktopu, vratte sa sem a stlacte Enter'
        Start-Process -FilePath $desktop -ArgumentList @('--cli-open', ('"{0}"' -f $target))

        Write-Host ''
        Write-Host 'HOTOVO: repozitar je stiahnuty.' -ForegroundColor Green
        Write-Host 'GitHub Desktop dostal pokyn otvorit tento lokalny repozitar. Overte jeho nazov v Current repository.'
        Write-Host "Dalsi krok: v priecinku $target spustite install.cmd (dvojklik)."
        Write-Host 'Potom otvorte priecinok v Claude Code alebo v Codexe.'
    }
    catch {
        Write-Host ''
        Write-Host ("PRIPRAVA SA ZASTAVILA: " + $_.Exception.Message) -ForegroundColor Red
        Write-Host 'Odovzdajte celu chybovu spravu spravcovi projektu.'
    }
}
```

- Prihlásim sa do GitHubu cez otvorený prehliadač podľa pokynov v PowerShelli.
- V **GitHub Desktope** kliknem na **Sign in to GitHub.com** a dokončím úvodné nastavenie.
  Použijem rovnaký účet.
- Vrátim sa do PowerShellu a stlačím **Enter**. V Desktope skontrolujem
  **Current repository → bimbo-trener**. Ak repozitár nevidím: **File → Add local
  repository…** a vyberiem stiahnutý priečinok.
- Spustím `bimbo-trener\install.cmd` (dvojklik). Vytvorí vedľa repozitára
  `bimbo-trener-app`, opýta sa na dátový adresár a napojí trénera na asistentov
  ([inštalácia](docs/application/installation.md)).
- Otvorím priečinok `bimbo-trener` v **Claude Code** alebo v aplikácii **ChatGPT → Codex →
  Pridať projekt** a začnem nový rozhovor: „Načítaj kontext a povedz mi, kde som.“
- Git, GitHub CLI a GitHub Desktop z tohto kroku ostávajú bežnými externými aplikáciami;
  odinštalátor projektu ich neodstraňuje.
- Pri chybe pošlem celé hlásenie správcovi. Existujúci cieľový priečinok skript neprepíše;
  ak už projekt mám, otvorím ho priamo. Celý postup ešte nebol otestovaný na čistom Windowse.
