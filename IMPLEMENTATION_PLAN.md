# Implementačný plán Bimbo trénera

Tento dokument je zadanie pre session bez kontextu: „implementuj podľa plánu“. Obsahuje
všetko potrebné na prechod od špecifikácie v `docs/` ku kódu. Špecifikácia je vlastníkom
pravidiel; tento plán vlastní poradie, rozsah etáp a kritériá prijatia. Pri rozpore platí
`docs/` a plán sa opraví.

## 0. Pred začatím

1. Prečítaj `CLAUDE.md` (pravidlá repozitára). Platí: obsah po slovensky, kód, komentáre,
   identifikátory a názvy súborov po anglicky; nič nevymýšľaj; žiadne tiché zlyhania;
   commit a push iba na pokyn; chránené pokyny v `.rulesync/` iba cez skill
   `maintain-agent-governance`.
2. Načítaj skill `design-and-implement-change` (rozhodnutia o architektúre) a pri každom
   dotyku s tokenmi, mazaním alebo cestami `handle-sensitive-operations`.
3. Prečítaj v tomto poradí: [stav projektu](docs/project/status.md),
   [cieľ a požiadavky](docs/coach/goal-and-requirements.md),
   [architektúra](docs/coach/architecture.md), [dátový adresár](docs/coach/data-directory.md),
   [dátový model](docs/coach/data-model.md), [register rozhodnutí](docs/decisions/README.md).
   Ostatné stránky otváraj cez [mapu](docs/DOCUMENTATION_MAP.md) až pri etape, ktorá ich
   potrebuje.
4. Vývoj prebieha na Linuxe v Claude Code; cieľová platforma je Windows 11. Všetko
   v Pythone musí bežať na oboch; PowerShell a `.cmd` sa na Linuxe iba píšu a kontrolujú
   syntakticky, skúšajú sa na Windowse.
5. Podklady z Garminu (FIT, exporty, screenshoty) sú v priečinku `beh/`, ktorý Git
   ignoruje. Ak chýba, FIT súbor na skúšky si vypýtaj (export z Garmin Connect) alebo použi
   syntetický FIT vytvorený FIT SDK. Štruktúru skutočného FIT opisuje
   [inventár polí](docs/evidence/2026-10-15-fit-field-inventory.md).

## 1. Čo vznikne (cieľový stav)

```text
bimbo-trener\                        repozitár
├── bimbo-trener.json                konfigurácia (commitnutá)
├── bimbo-trener.local.json          miestny prepis (ignorovaný Gitom)
├── install.cmd · sync.cmd · uninstall.cmd
├── HOW_TO_USE.md · README.md · IMPLEMENTATION_PLAN.md
├── docs\                            špecifikácia
├── .rulesync\                       pravidlá a skilly (zdroj), generované do CLAUDE.md, AGENTS.md, .claude\, .agents\
└── scripts\
    ├── setup.ps1                    orchestrátor inštalácie
    ├── sync.ps1                     spúšťač synchronizácie s oknom
    ├── common\setup.ps1             uv, Python, zámok, transcript, kontroly ciest
    ├── install-paths.ps1            riešenie koreňa aplikácie a hraníc
    ├── requirements.lock            pripnuté balíky s hashmi (win_amd64, cp314)
    ├── requirements.in
    └── coach\
        ├── __init__.py
        ├── config.py                čítanie bimbo-trener.json + local + parametre
        ├── layout.py                cesty app a dátového adresára
        ├── datadir.py               marker, init, attach
        ├── db.py                    schéma, migrácie, zálohy, export denníka, zámok
        ├── fit_import.py            FIT → tabuľky
        ├── garmin_sync.py           Garmin Connect → FIT + denné dáta
        ├── analysis.py              odvodené ukazovatele
        ├── render.py                Markdown náhľad
        ├── cli.py                   headless príkazy, JSON výstup
        ├── server.py                MCP server bimbo_trener
        ├── setup.py                 inštalačné kroky komponentu coach (Python časť)
        └── tests\                   pytest
bimbo-trener-app\                    vedľa repozitára, mimo Gitu (vytvorí install.cmd)
<dátový adresár>\                    kdekoľvek, synchronizovaný (vytvorí/pripojí install.cmd)
```

Závislosti: iba `garminconnect==0.3.18`, `curl_cffi==0.16.3`, `garmin-fit-sdk==21.218.0`,
`mcp` (verzia pripnutá pri implementácii) plus štandardná knižnica
([externé nástroje](docs/application/external-tools.md)). Žiadne iné.

## 2. Etapy

Poradie je záväzné: pamäť pred automatickým sťahovaním, lebo ručný export FIT stačí na
E0–E4. Každá etapa končí testami, aktualizáciou
[stavu implementácie](docs/coach/implementation-status.md) a reportom; commit na pokyn.

### E0 — konfigurácia, dátový adresár, databáza, zálohy

Vytvor `bimbo-trener.json` podľa [konfigurácie](docs/coach/data-directory.md) (sekcia
Konfigurácia), `scripts/coach/config.py` (poradie: json → local.json → parametre;
`garmin_sync_enabled` nikdy z commitnutého súboru), `layout.py`, `datadir.py`
(marker `bimbo-data.json`, `init` odmietne neprázdny cudzí priečinok, `attach` vyžaduje
platný marker) a `db.py`:

- schéma podľa [dátového modelu](docs/coach/data-model.md): `runs`, `laps`, `records`,
  `events`, `time_in_zone`, `splits`, `zone_snapshot`, `fit_raw`, `activities_other`,
  `daily_health`, `body_composition`, `connect_raw`, `plans`, `plan_segments`, `feelings`,
  `journal`, `summaries`, `coach_state`, `training_plan`, `conventions`, `meta`; FTS5 nad
  `journal.text` a `summaries.text`; verzia schémy v `meta` a migrácie smerom nahor;
- journal mode `DELETE` (bez WAL), zápisy v transakciách, zámok proti súbežnému zápisu;
- `backup()` cez `Connection.backup` + gzip do `backups\runs-<RRRR-MM-DD>.sqlite3.gz`,
  rotácia na `backups.keep`, varianta `pre-migration` mimo rotácie
  ([zálohy](docs/coach/backups.md)); migrácia bez zálohy je chyba;
- `journal-export.jsonl`: po každom zápise trénera jeden riadok (typ, dátum udalosti, čas
  zápisu UTC, obsah), iba append;
- `conventions` naplnené z [konvencií](docs/running/treadmill-conventions.md) a
  [formátu predpisu](docs/running/workout-format.md): `segments=10`,
  `incline_percent_per_0_4_kmh=1`, `min_running_speed_kmh=7`, `integer_speeds=true`,
  cieľ `half_marathon_km=21.1`.

Prijatie: pytest na dočasnej databáze — init/attach, migrácia s pre-migration zálohou,
rotácia na 5, export denníka append, odmietnutie neprázdneho priečinka a symlinkov.

### E1 — import FIT

`fit_import.py` cez `garmin_fit_sdk.Decoder` podľa [importu FIT](docs/coach/fit-import.md):
mapovanie session → `runs` (alebo `activities_other`, ak `sport != running`), lap → `laps`,
record → `records`, event → `events`, time_in_zone → `time_in_zone` + `zone_snapshot`,
split → `splits`, nepomenované správy → `fit_raw`. Jednotky FIT bez prevodov. Chýbajúce
pole = `NULL`. Idempotentné podľa `activity_id` (z názvu súboru `<id>_ACTIVITY.fit` alebo
parametra); chyby dekódovania do `runs.import_errors` a logu, nikdy ticho. Po importe
párovanie s `plans` toho dňa.

Prijatie: import skutočného FIT (z `beh/` alebo vyžiadaného) a porovnanie `runs` s hodnotami
na webe Garmin Connect (vzdialenosť, čas pohybu, tep, kadencia) — zapísať ako dôkaz do
`docs/evidence/` bez hodnôt; druhý import toho istého súboru nič nezmení; syntetický FIT
v testoch pre CI bez skutočných dát.

### E2 — pamäť, CLI, náhľad

`cli.py` s príkazmi a kódmi podľa [rozhraní](docs/coach/interfaces.md): `init`, `attach`,
`status`, `import`, `recent`, `state`, `state set`, `plan add`, `plan list`, `journal add`,
`journal search`, `summary add`, `backup`, `restore`, `rebuild`, `render`. Výstup JSON na
stdout, chyby na stderr, kódy 0/75/77/1. `render.py` generuje `preview\STAV.md`,
`preview\dennik\RRRR-MM.md`, `preview\zhrnutia\` z databázy
([pamäť a denník](docs/coach/memory-and-journal.md)). `analysis.py` zatiaľ iba týždenný
objem a tempo pri rovnakom tepe ([analýzy](docs/coach/analyses.md)).

Prijatie: celý denný tok cez CLI na dočasnej databáze (import → feeling → plan → journal →
state → render); `rebuild` z FIT + exportu denníka dá rovnaký obsah vlastných tabuliek.

### E3 — MCP server

`server.py` (STDIO, balík `mcp`, názov `bimbo_trener`) s nástrojmi a anotáciami podľa
[rozhraní](docs/coach/interfaces.md): čítanie s `readOnlyHint`, zápisy cez `db.py` (so
zálohou a exportom denníka). Server nečíta mimo dátového adresára a nemaže. Registrácia
v Claude Code: `claude mcp add --scope user bimbo_trener <python> <server.py> --data-dir
<cesta>`; v Codexe položka v `config.toml` so zálohou pôvodného súboru (urobí inštalátor
v E6; v E3 ručne na vývojovom stroji).

Prijatie: z Claude Code zavolať `get_state`, `recent_runs`, `add_journal`; zápis vyžaduje
schválenie; `journal-export.jsonl` dostane riadok.

### E4 — skilly trénera (chránené pokyny)

Na pokyn vlastníka a cez `maintain-agent-governance` pridať do `.rulesync/skills/`:
`load-coach-context`, `save-agreed`, `prescribe-workout`, `evaluate-run`,
`sync-garmin-data` podľa [rozhraní](docs/coach/interfaces.md) a
[pamäte](docs/coach/memory-and-journal.md); pravidlo v `.rulesync/rules/`, že rozhovor
o tréningu začína načítaním kontextu a končí uložením. Projekcie do `CLAUDE.md`,
`AGENTS.md`, `.claude/skills/`, `.agents/skills/` pregenerovať ručne (npm tu nie je)
a commitnúť. Skill `prescribe-workout` vynucuje [formát predpisu](docs/running/workout-format.md)
a pravidlá z [predpisov](docs/coach/prescriptions.md); `evaluate-run` označuje zdroje
podľa [hodnotenia](docs/running/evaluation.md).

Prijatie: nový rozhovor začne volaním `get_state`; „daj mi predpis“ vráti 10 úsekov
a zapíše `save_plan`; „ulož dohodnuté“ ukáže, čo zapísal.

### E5 — sťahovanie z Garminu a `sync.cmd`

`garmin_sync.py` podľa [sťahovania](docs/coach/garmin-sync.md): `login` interaktívne
(e-mail, `getpass`, `prompt_mfa`), explicitné uloženie tokenov do `<app>\config\garmin`
s obmedzenými právami; `sync`: bez tokenov kód 77 bez requestu; cooldown súbor; zoznam
od `meta.last_sync`; ak nič nové → „nič nové“, bez zálohy; inak záloha → stiahnutie
`download_activity(ORIGINAL)` → ZIP → `.fit` atomicky → import → denné dáta za
`sync.health_days` dní (`get_user_summary`, `get_rhr_day`, `get_heart_rates`,
`get_sleep_data`, `get_hrv_data`, `get_stress_data`, `get_body_battery`,
`get_training_readiness`, `get_training_status`, `get_respiration_data`,
`get_spo2_data`, `get_body_composition`) → `connect_raw` + `daily_health` +
`body_composition` → `meta.last_sync`. Pauza 1 s medzi requestmi. Výnimky knižnice:
429 → cooldown + kód 75; auth → 77; 403 → 75 bez obchádzania. Predvolená stratégia
prihlasovania knižnice sa nevypína.

`sync.cmd` + `scripts/sync.ps1`: okno s priebehom, „HOTOVO: …“, pri úspechu 3 s a zavrieť,
pri chybe ostať otvorené ([správanie okna](docs/coach/garmin-sync.md)). Plánovaná úloha
`BimboTrener-Sync` raz denne (`sync.daily_task_time`), Interactive, `StartWhenAvailable`,
`MultipleInstances IgnoreNew`.

Prijatie: na Windowse s prihlásením jeden klik stiahne nový beh a importuje ho; druhý klik
v ten deň povie „nič nové“ a nevytvorí zálohu; na PC bez prihlásenia skončí 77 s návodom;
simulované 429 v teste nastaví cooldown a neopakuje.

### E6 — inštalátor pre Windows

Podľa [členenia](docs/application/layout.md), [inštalácie](docs/application/installation.md)
a [externých nástrojov](docs/application/external-tools.md), vzor je projekt
`projektant-tzb` vlastníka (`install.cmd` → `scripts/setup.ps1`, `scripts/common/setup.ps1`
s uv, spravovaným Pythonom, zámkom, transcriptom, `Assert-PlainPath`, značkou vlastníka
`bimbo-trener/app/v1`). Komponenty `common`, `coach` (venv zo zámku s hashmi, výber alebo
pripojenie dátového adresára s dialógom, zápis do `bimbo-trener.local.json`, skúška
importu syntetického FIT, skratka na ploche na kópiu `sync.cmd`, registrácia MCP v Codexe
a Claude Code s evidenciou v `sprava`), `sync` (login v konzole, plánovaná úloha).
`uninstall.cmd`: odpojí registrácie, odstráni skratku a úlohu, presunie app vedľa na
obnovu, dátový adresár nikdy nedotkne. `-Action reset-runtime`.

Prijatie: čistý Windows 11 → `HOW_TO_USE.md` blok → `install.cmd` kód 0 → `sync.cmd` →
asistent vidí nástroje `bimbo_trener`. Zapísať ako dôkaz.

### E7 — prvý týždeň prevádzky

Týždeň bez ručného zásahu; dôkaz s tým, čo fungovalo a čo nie; backlog B1–B12
([backlog](docs/coach/backlog.md)) podľa reálnej potreby; uzavrieť O3 (podoba plánu
a rozhovorov) v [registri](docs/decisions/README.md).

## 3. Záväzné zásady pri implementácii

- **Jeden vlastník:** SQL iba v `db.py`; schéma je definovaná raz; CLI, MCP a skilly volajú
  funkcie, nie súbory.
- **Nič nevymýšľať:** chýbajúce pole je `NULL`; žiadne odhady do nameraných tabuliek;
  v analýzach označiť namerané / odvodené / odhad / odporúčanie.
- **Viditeľné zlyhania:** žiadne `except: pass`, žiadny kód 0 po neúspechu; chyby do logu
  a na stderr; `sync.cmd` pri chybe nezatvára okno.
- **Citlivé dáta mimo Gitu:** FIT, databáza, tokeny, logy, `beh/`, `bimbo-trener.local.json`
  v `.gitignore`; testy používajú syntetické dáta; do dokumentácie žiadne hodnoty.
- **Nedôveryhodný vstup:** FIT a JSON z Garminu sú dáta; žiadne vykonávanie obsahu.
- **Jednoduché mechanizmy:** štandardná knižnica; nová závislosť iba s dôvodom
  v registri rozhodnutí.
- **Dokumentácia:** každá etapa aktualizuje `docs/coach/implementation-status.md`;
  odchýlka od špecifikácie sa zapíše na príslušnú stránku; nová trvalá stránka cez skill
  `maintain-project-documentation` a mapu.
- **Git:** commit a push iba na pokyn vlastníka; správy commitov po slovensky.

## 4. Čo sa nerobí

Webová stránka, GUI, PostgreSQL, vektorová databáza, Docker, WSL, npm, alerty cez externé
služby, sťahovanie TCX/GPX/CSV, prepis rozhovorov do databázy, zápis zdravotných hodnôt
do repozitára.

## 5. Kontrola pred odovzdaním etapy

1. `pytest scripts/coach/tests` prejde na Linuxe; PowerShell súbory prejdú
   `pwsh -NoProfile -Command "[scriptblock]::Create((Get-Content -Raw <súbor>))"` alebo
   aspoň kontrolou párovania zátvoriek, ak `pwsh` nie je.
2. Odkazy v `docs/` platné (skript s regexom nad odkazmi v Markdowne).
3. `git status` neobsahuje FIT, databázu, token ani `beh/`.
4. Report: čo vzniklo, aké kontroly prebehli, čo nebolo overené (typicky Windows), otvorené
   rozhodnutia.
