# Dátový model

Schéma SQLite v dátovom adresári. Jediný vlastník všetkých zapisovaných dát
([rozhodnutie](../decisions/2026-10-15-sqlite-single-owner.md)). Názvy sú návrh, kým ich
`db.py` neimplementuje; potom je zdrojom pravdy kód a táto stránka opisuje význam.

## Tabuľky podľa pôvodu a životnosti

### Namerané (z FIT, iba pridávanie)

| Tabuľka | Obsah | Kľúč |
| --- | --- | --- |
| `runs` | jeden riadok na aktivitu: identifikátor Garmin, čas štartu (lokálny aj UTC), šport, miesto (pás/vonku z FIT `sub_sport`), vzdialenosť, celkový čas, čas pohybu, uplynutý čas, priemerné a najlepšie tempo, tep priemer/max, výkon priemer/max, kadencia priemer/max, dĺžka kroku, vertikálny pomer, oscilácia, kontakt so zemou, Training Effect aeróbny/anaeróbny, záťaž, kalórie, čas behu/chôdze/nečinnosti, cesta k FIT, zdroj (`garmin_sync`, `manual_fit`, `owner_text`), čas importu | `activity_id` |
| `laps` | kolá z FIT: poradie, začiatok, trvanie, vzdialenosť, priemerné tempo, tep priemer/max, kadencia | `activity_id`, `lap_index` |
| `records` | sekundové záznamy: čas, vzdialenosť, rýchlosť, tep, kadencia, výkon, dynamika (čo FIT obsahuje) | `activity_id`, `timestamp` |
| `events` | pauzy, zmeny (FIT `event`): typ, čas | `activity_id`, `timestamp` |

Chýbajúce pole = `NULL`. Jednotky sú metrické a uložené tak, ako ich dáva FIT (metre,
sekundy, m/s), prevody robí vrstva analýz.

### Vlastné (tréner a ja)

| Tabuľka | Obsah | Životnosť |
| --- | --- | --- |
| `plans` | predpis: dátum, pre ktorý platí; typ tréningu; celkový čas; stav (`proposed`, `done`, `skipped`); odkaz na `runs.activity_id`, ktorý ho splnil; kto vytvoril; poznámka | pridáva sa, stav sa mení |
| `plan_segments` | 10 úsekov predpisu: poradie, trvanie, rýchlosť km/h (celé číslo), sklon % | s predpisom |
| `feelings` | pocit k behu: `activity_id` alebo dátum, hodnota (`easy`, `ok`, `hard`), voľný text, čas zápisu | iba pridávanie |
| `journal` | denník: dátum, typ (`feeling`, `note`, `circumstance`, `decision`, `conversation_summary`), text, odkaz na beh alebo predpis, čas zápisu | iba pridávanie, nikdy sa nemaže |
| `summaries` | zhrnutia období: druh (`week`, `month`), obdobie, text, čas zápisu | pridávanie; nová verzia nahrádza staršiu toho istého obdobia |
| `coach_state` | jeden riadok: aktuálny stav trénera ako text (fáza plánu, čo je na rade, posledné rozhodnutia, otvorené otázky), aktuálne pohodlné rýchlosti, čas aktualizácie | prepisuje sa; história v zálohách |
| `training_plan` | dlhodobý plán: cieľ, fázy s rozsahom dátumov a zámerom, míľniky (12, 15, 17, 19, 21,1 km) s plánovaným a skutočným dátumom, verzia | mení sa zriedka, verzuje sa |
| `conventions` | moje pravidlá ako kľúč/hodnota: `segments=10`, `incline_per_0_4_kmh=1`, `min_running_speed=7`, … | takmer nikdy |
| `meta` | verzia schémy, `data_id`, čas poslednej synchronizácie a importu | — |

### Fulltext

Virtuálna tabuľka FTS5 nad `journal.text` a `summaries.text` (tokenizér `unicode61
remove_diacritics 2`) pre otázky do minulosti („kedy som sa sťažoval na koleno“).

## Vzťahy

- `plans.activity_id` → `runs` (ktorý beh predpis splnil); porovnanie po úsekoch používa
  `plan_segments` a `records` ([predpisy](prescriptions.md)).
- `journal.activity_id` / `journal.plan_id` voliteľne viažu záznam k behu alebo predpisu.
- `feelings` je samostatná tabuľka, aby pocit bol dotazovateľná hodnota, a zároveň sa
  zapíše aj ako `journal` záznam typu `feeling` kvôli chronológii.

## Čo do databázy nepatrí

- Prihlasovací token Garminu, surové JSON odpovede Garmin Connect (iba ak by boli potrebné
  pre pole, ktoré FIT nemá; vtedy ako samostatná tabuľka `connect_summary` s `activity_id`).
- Prepisy rozhovorov (otvorené O6); závery áno.
