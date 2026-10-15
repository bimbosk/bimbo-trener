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
| `init --data-dir` / `attach --data-dir [--write-local]` | nový alebo existujúci dátový adresár | inštalátor |
| `config` | výsledná konfigurácia po zlúčení vrstiev | ja, diagnostika |
| `status` | posledná synchronizácia, počet behov, posledný beh, stav zálohy | skratka, MCP |
| `recent --days N` | behy a denník za N dní | MCP |
| `state` / `state set` | čítanie a zápis `coach_state` | MCP |
| `plan add` / `plan list` / `plan show` / `plan status` | zápis, výpis, detail a stav predpisov | MCP |
| `feeling` | zápis pocitu | MCP |
| `journal add` / `journal search` | zápis a fulltext denníka | MCP |
| `summary add` / `summary latest` | zápis a čítanie zhrnutia obdobia | MCP |
| `training-plan show` / `training-plan set` | dlhodobý plán | MCP |
| `analysis <kind>` | `weekly_volume`, `pace_at_hr`, `drift`, `compare`, `warnings` | MCP |
| `health --days N` | denné zdravotné dáta | MCP |
| `backup` / `restore --from` / `rebuild` | zálohy a obnova ([zálohy](backups.md)) | ja, pri probléme |
| `render` | Markdown náhľad do `preview\` | skratka, MCP |

Kódy: 0 OK, 75 dočasné zlyhanie, 77 chýba prihlásenie alebo nastavenie, 1 chyba.

## MCP server (`server.py`, STDIO, názov `bimbo_trener`)

| Nástroj | Anotácia | Čo vráti / urobí |
| --- | --- | --- |
| `get_state` | readOnly | `coach_state` |
| `recent_runs(days)` | readOnly | súhrny behov s pocitom a predpisom |
| `recent_journal(days)` | readOnly | záznamy denníka |
| `search_journal(query)` | readOnly | fulltext nad denníkom a zhrnutiami |
| `get_plan(plan_date, plan_id)` / `list_plans` / `get_training_plan` | readOnly | predpis dňa alebo podľa id, zoznam, dlhodobý plán |
| `recent_health(days)` / `status` / `conventions` | readOnly | denné zdravotné dáta, stav databázy, moje konvencie |
| `compare_plan_run(activity_id)` | readOnly | porovnanie po úsekoch ([predpisy](prescriptions.md)) |
| `analysis(kind, period)` | readOnly | ukazovateľ ([analýzy](analyses.md)) |
| `save_plan(...)` / `set_plan_status(...)` | zápis, schválenie | nový predpis, zmena stavu |
| `add_feeling(...)` / `add_journal(...)` | zápis, schválenie | pocit, okolnosť, rozhodnutie, zhrnutie rozhovoru |
| `update_state(text)` | zápis, schválenie | prepis `coach_state` |
| `add_summary(kind, period, text)` | zápis, schválenie | zhrnutie obdobia |
| `set_training_plan(...)` | zápis, schválenie | nová verzia plánu |
| `run_sync()` / `import_fit()` | zápis, schválenie | spustí `sync`, ak je na tomto PC zapnuté; import ručne vložených FIT |

Nástroje na čítanie majú `readOnlyHint`, aby ich asistent volal bez schvaľovania
každého volania. Zápisové idú cez `db.py` so zálohou pred zápisom. Server nikdy nečíta
súbory mimo dátového adresára a nemaže ([bezpečnosť](security.md)).

Registrácia v Codexe (`config.toml`) a v Claude Code (`claude mcp add`) je úloha
inštalátora ([asistenti](../integrations/assistants.md)).

## Skilly asistentov (`.rulesync/skills/`, návrh)

| Skill | Kedy | Čo robí |
| --- | --- | --- |
| `coach-session` | každý rozhovor o behoch, pocitoch, predpisoch, pláne | začiatok: `get_state`, `recent_journal(7)`, `recent_runs(3)`, `recent_health(3)`; počas: zápisy hneď; koniec („ulož dohodnuté“): doplnenie, zhrnutie rozhovoru, `update_state`, zhrnutie obdobia, výpis zapísaného |
| `prescribe-workout` („daj mi predpis“) | na požiadanie | formát a pravidlá z [predpisov](prescriptions.md), zápis cez `save_plan` |
| `evaluate-run` | po importe alebo na otázku „ako to šlo“ | porovnanie s predpisom, označenie zdrojov, zápis pocitu |
| `sync-garmin-data` („stiahni dáta“) | keď poviem „stiahni dáta“ alebo keď tréner zistí, že dnešný beh v databáze chýba | spustí `sync.cmd` v koreni repozitára, počká na výsledok, prečíta `status` a oznámi, čo pribudlo; pri kóde 75 alebo 77 povie, čo robiť ([sťahovanie](garmin-sync.md)) |

Skilly sú v `.rulesync/skills/` s projekciami do `.claude/skills/` a `.agents/skills/`; pravidlo Tréner
v `.rulesync/rules/10-repository.md` ich smeruje. Zmeny iba cez `maintain-agent-governance`.
