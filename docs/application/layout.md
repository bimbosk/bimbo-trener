# Členenie aplikácie

## Dva susedné adresáre a dátový adresár

```text
D:\Beh\
├── bimbo-trener\            Git repozitár otvorený v Claude Code / Codexe
└── bimbo-trener-app\        lokálna aplikácia, mimo Gitu
    ├── runtime\             obnoviteľné: bin\uv.exe, python\, venv\, cache\, temp\
    ├── config\              garmin\ (token), overená cesta koreňa
    ├── logs\                transcript inštalácie, logy sync a importu
    ├── sprava\              značka vlastníka, zámok, evidencia skratky a MCP registrácií
    ├── scripts\             kópia skriptov z repozitára
    ├── install.cmd · sync.cmd · uninstall.cmd
    └── .bimbo-trener-installer   značka vlastníctva `bimbo-trener/app/v1`

<ľubovoľný synchronizovaný priečinok>\Bimbo-data\     môj dátový adresár
```

Spúšťače v koreni repozitára: `install.cmd` (inštalácia a správa), `sync.cmd` (stiahnutie dát
z Garminu, [sťahovanie](../coach/garmin-sync.md)), `uninstall.cmd`. Inštalátor ich kopíruje aj
do aplikácie, aby fungovali bez otvoreného repozitára.

Predvolený cieľ aplikácie je hodnota `install_root: "../bimbo-trener-app"`
v `bimbo-trener.json` v koreni repozitára ([konfigurácia](../coach/data-directory.md)),
relatívna ku koreňu repozitára; `-InstallDirectory` je jednorazové prepísanie. Repozitár, koreň disku a prekrývajúce sa cesty sa odmietajú.
Dátový adresár je mimo oboch ([dátový adresár](../coach/data-directory.md)).

## Adresáre a ich zachovanie

| Adresár | Obsah | Zachovanie |
| --- | --- | --- |
| `runtime` | uv, spravovaný Python 3.14, jeden venv `coach` s pripnutými balíkmi | obnoviteľný; maže ho `reset-runtime` |
| `config` | token Garminu, overená cesta koreňa | trvalý; **nesynchronizuje sa** |
| `logs` | `instalacia-<čas>.log`, `sync.log`, `import.log` | trvalý |
| `sprava` | `sprava.json`, `instalacia.lock`, evidencia skratky, MCP registrácií a plánovanej úlohy, `scripts-previous-*` | trvalý |
| `scripts` | kópia skriptov; vymieňa sa cez pripravený adresár | obnovuje inštalácia |

## Komponenty

| Komponent | Čo pripraví | Čo zaregistruje |
| --- | --- | --- |
| `common` | uv, Python, kópiu `scripts` | — |
| `coach` | venv s garminconnect, curl_cffi, garmin-fit-sdk, mcp; výber alebo pripojenie dátového adresára; skúšku importu na vzorovom FIT; skratku „Stiahni dáta z Garminu“ | MCP server `bimbo_trener` v Codexe a Claude Code |
| `sync` (voliteľný, iba na PC s Garmin prihlásením) | prihlásenie do Garminu v konzole; plánovanú úlohu | plánovanú úlohu `BimboTrener-Sync` |

