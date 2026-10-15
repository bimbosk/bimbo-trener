# Architektúra

## Tok dát

```text
beh → hodinky Garmin → telefón → Garmin Connect (cloud)
                                        │
            skratka „Stiahni dáta“ alebo plánovaná úloha (1× denne)
                                        ▼
                     garmin_sync: nové aktivity → FIT súbory do data/fit/
                                        ▼
                     fit_import: FIT → SQLite (runs, laps, records)
                                        ▼
                 SQLite v dátovom adresári (sync nástroj → všetky moje PC)
                                        ▲
          MCP server / CLI ─── Claude Code, Codex: čítajú stav a denník,
                                zapisujú predpis, pocit, rozhodnutia
```

Záložná cesta: FIT súbor ručne exportovaný z webu Garmin Connect alebo skopírovaný
z hodiniek sa vloží do `data/fit/` a import ho spracuje rovnako.

## Vrstvy nad SQLite

| Vrstva | Modul (návrh) | Zodpovednosť |
| --- | --- | --- |
| databáza | `db.py` | jediné miesto, ktoré pozná schému; vytvorenie, migrácie, záloha pred zápisom |
| import | `fit_import.py` | FIT → tabuľky cez Garmin FIT SDK; idempotentne podľa identifikátora aktivity |
| sťahovanie | `garmin_sync.py` | garminconnect: zoznam nových aktivít, stiahnutie originálu, odovzdanie importu |
| analýzy | `analysis.py` | odvodené ukazovatele a reporty ([analýzy](analyses.md)) |
| CLI | `cli.py` | headless príkazy s JSON výstupom; volá ich skratka, plánovač aj MCP |
| MCP server | `server.py` | nástroje pre asistentov nad tými istými funkciami |
| náhľad | `render.py` | Markdown náhľad denníka a stavu z databázy (iba na čítanie) |

Nikto okrem `db.py` nepíše SQL. Skilly asistentov volajú MCP nástroje, nie súbory
([rozhrania](interfaces.md)).

## Čo beží kde

| Miesto | Čo |
| --- | --- |
| repozitár `bimbo-trener` | kód, inštalátor, dokumentácia, pokyny agentov, konfigurácia `bimbo-trener.json`; otvorený v Claude Code / Codexe |
| app `bimbo-trener-app` (vedľa repozitára, mimo Gitu) | uv, Python, venv so závislosťami, lokálny config, logy, zámok ([členenie](../application/layout.md)) |
| dátový adresár (synchronizovaný) | FIT súbory, databáza, zálohy, náhľady ([dátový adresár](data-directory.md)) |
| Garmin Connect | zdroj aktivít; jediná externá služba |

## Závislosti

Štandardná knižnica Pythonu plus `garminconnect`, `curl_cffi`, `garmin-fit-sdk` a balík
`mcp` pre server ([externé nástroje](../application/external-tools.md)). Žiadny webový
server, žiadne GUI, žiadna vektorová databáza.
