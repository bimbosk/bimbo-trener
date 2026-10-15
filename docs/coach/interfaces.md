# Rozhrania

Vrstvy nad databázou: Python moduly → CLI → MCP server →
skilly asistentov. Nikto okrem `db.py` nepíše SQL; MCP a skilly volajú funkcie projektu
([architektúra](architecture.md)). Názvy sú návrh, kým ich implementácia nepotvrdí.

## CLI (`cli.py`, výstup JSON)

| Príkaz | Čo robí | Kto ho volá |
| --- | --- | --- |
| `login` | interaktívne prihlásenie do Garminu, uloženie tokenu | správca v konzole |
| `sync` | stiahnutie nových FIT a import ([sťahovanie](garmin-sync.md)) | skratka, plánovaná úloha |
| `import` | import FIT súborov z `data/fit/` bez sťahovania | skratka po ručnom exporte |
| `init --data-dir` / `attach --data-dir` | nový alebo existujúci dátový adresár | inštalátor |
| `status` | posledná synchronizácia, počet behov, posledný beh, stav zálohy | skratka, MCP |
| `recent --days N` | behy a denník za N dní | MCP |
| `state` / `state set` | čítanie a zápis `coach_state` | MCP |
| `plan add` / `plan list` | zápis a výpis predpisov | MCP |
| `journal add` / `journal search` | zápis a fulltext denníka | MCP |
| `summary add` | zápis zhrnutia obdobia | MCP |
| `backup` / `restore --from` / `rebuild` | zálohy a obnova ([zálohy](backups.md)) | správca |
| `render` | Markdown náhľad do `preview\` | skratka, MCP |

Kódy: 0 OK, 75 dočasné zlyhanie, 77 chýba prihlásenie alebo nastavenie, 1 chyba.

## MCP server (`server.py`, STDIO, názov `bimbo_trener`)

| Nástroj | Anotácia | Čo vráti / urobí |
| --- | --- | --- |
| `get_state` | readOnly | `coach_state` |
| `recent_runs(days)` | readOnly | súhrny behov s pocitom a predpisom |
| `recent_journal(days)` | readOnly | záznamy denníka |
| `search_journal(query)` | readOnly | fulltext nad denníkom a zhrnutiami |
| `get_plan(date)` / `get_training_plan` | readOnly | predpis dňa / dlhodobý plán |
| `compare_plan_run(activity_id)` | readOnly | porovnanie po úsekoch ([predpisy](prescriptions.md)) |
| `analysis(kind, period)` | readOnly | ukazovateľ ([analýzy](analyses.md)) |
| `save_plan(...)` | zápis, schválenie | nový predpis |
| `add_feeling(...)` / `add_journal(...)` | zápis, schválenie | pocit, okolnosť, rozhodnutie, zhrnutie rozhovoru |
| `update_state(text)` | zápis, schválenie | prepis `coach_state` |
| `add_summary(kind, period, text)` | zápis, schválenie | zhrnutie obdobia |
| `set_training_plan(...)` | zápis, schválenie | nová verzia plánu |
| `run_sync()` | zápis, schválenie | spustí `sync`, ak je na tomto PC zapnuté |

Nástroje na čítanie majú `readOnlyHint`, aby ich asistent volal bez schvaľovania
každého volania. Zápisové idú cez `db.py` so zálohou pred zápisom. Server nikdy nečíta
súbory mimo dátového adresára a nemaže ([bezpečnosť](security.md)).

Registrácia v Codexe (`config.toml`) a v Claude Code (`claude mcp add`) je úloha
inštalátora ([asistenti](../integrations/assistants.md)).

## Skilly asistentov (`.rulesync/skills/`, návrh)

| Skill | Kedy | Čo robí |
| --- | --- | --- |
| `load-coach-context` („načítaj kontext“) | na začiatku každého rozhovoru o tréningu | `get_state`, posledné zhrnutie, `recent_journal(7)`, `recent_runs(3)`; nič viac bez otázky |
| `save-agreed` („ulož dohodnuté“) | na konci rozhovoru alebo keď smeruje k záveru | vytiahne závery, doplní chýbajúce zápisy, zhrnutie rozhovoru, `update_state`, prípadne zhrnutie týždňa/mesiaca; ukáže, čo zapísal |
| `prescribe-workout` („daj mi predpis“) | na požiadanie | formát a pravidlá z [predpisov](prescriptions.md), zápis cez `save_plan` |
| `evaluate-run` | po importe alebo na otázku „ako to šlo“ | porovnanie s predpisom, označenie zdrojov, zápis pocitu |

Pridanie skillov mení chránené pokyny a robí sa cez `maintain-agent-governance` na môj pokyn.
