# Dátový model

Schéma SQLite v dátovom adresári. Jediný vlastník všetkých zapisovaných dát
([rozhodnutie](../decisions/2026-10-15-sqlite-single-owner.md)). Názvy sú návrh, kým ich
`db.py` neimplementuje; potom je zdrojom pravdy kód a táto stránka opisuje význam.

## Tabuľky podľa pôvodu a životnosti

### Namerané (z FIT, iba pridávanie)

| Tabuľka | Obsah | Kľúč |
| --- | --- | --- |
| `runs` | jeden riadok na aktivitu: identifikátor Garmin, čas štartu (lokálny aj UTC), šport, miesto (pás/vonku z FIT `sub_sport`), vzdialenosť, celkový čas, čas pohybu, uplynutý čas, priemerné a najlepšie tempo, tep priemer/max, výkon priemer/max, `normalized_power`, `total_work`, `total_strides`, kadencia priemer/max, dĺžka kroku, vertikálny pomer, oscilácia, kontakt so zemou, Training Effect aeróbny/anaeróbny, `training_load_peak`, kalórie, zariadenie a firmvér, cesta k FIT, zdroj (`garmin_sync`, `manual_fit`), čas importu | `activity_id` |
| `laps` | kolá z FIT (hodinky ich robia každý kilometer): poradie, spúšťač, začiatok, trvanie, vzdialenosť, rýchlosť, tep priemer/max, kadencia, výkon, NP, dynamika behu | `activity_id`, `lap_index` |
| `records` | sekundové záznamy: poradie `seq`, čas, vzdialenosť, rýchlosť, tep, kadencia, výkon, kumulovaný výkon, oscilácia, pomer, dĺžka kroku, kontakt so zemou, poloha a výška (vonku) | `activity_id`, `seq` |
| `events` | pauzy, zmeny (FIT `event`): typ, čas | `activity_id`, `timestamp` |
| `time_in_zone` | čas v tepových a výkonových zónach za session a za každé kolo, s hranicami zón | `activity_id`, `reference` (session/lap), `index` |
| `splits` | Garminovo rozpoznanie beh / chôdza / státie: typ, začiatok, trvanie, vzdialenosť, tep | `activity_id`, `split_index` |
| `zone_snapshot` | max tep, pokojový tep, prahový tep, FTP a hranice zón platné v deň behu (z `time_in_zone` a `zones_target`) | `activity_id` |
| `fit_raw` | všetko ostatné z FIT ako JSON: nemapované známe správy (`file_id`, `device_info`, `sport`, `user_profile`, `zones_target`, `device_settings`, `battery`, …), nepomenované správy (číselné ID) a neznáme polia mapovaných správ (`<správa>.unknown_fields`); pri iných športoch aj `record`/`lap` | `activity_id`, `mesg_name`, `mesg_index` |
| `activities_other` | aktivity iného typu než beh (jazdy z Edge 1040, chôdza, …): súhrn zo session + cesta k FIT; bez `laps`/`records`, kým nie sú potrebné | `activity_id` |

### Denné zdravotné dáta (z Garmin Connect, prepisujú sa za posledné 4 dni)

| Tabuľka | Obsah | Kľúč |
| --- | --- | --- |
| `daily_health` | jeden riadok na deň: pokojový tep, HRV (nočný priemer, status), spánok (trvanie, skóre, fázy), stres (priemer), Body Battery (min/max/ráno), Training Readiness, Training Status, dýchanie (priemer), SpO2 (priemer), kroky, intenzívne minúty, kalórie | `date` |
| `body_composition` | jedno váženie: čas, hmotnosť, BMI, tuk %, svalová hmota, kosti, voda %, zdroj (`index_s2`, ručne) | `timestamp` |
| `connect_raw` | surová JSON odpoveď každého volania: dátum, druh (`sleep`, `hrv`, …), JSON, čas stiahnutia | `date`, `kind` |

Normalizované stĺpce sa plnia z JSON pri sťahovaní; ak Garmin pridá alebo zmení pole,
surový JSON ostáva a stĺpce sa dajú doplniť bez nového sťahovania.

Chýbajúce pole = `NULL`. Jednotky sú uložené tak, ako ich dáva FIT (metre, sekundy, m/s,
milimetre a milisekundy pre dynamiku), prevody robí vrstva analýz
([obsah FIT](../evidence/2026-10-15-fit-file-contents.md)).

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
| `meta` | verzia schémy, `data_id`, `last_sync` (UTC, odkedy pýtať Garmin), čas posledného importu, dátum poslednej zálohy | — |

### Fulltext

Virtuálna tabuľka FTS5 nad `journal.text` a `summaries.text` (tokenizér `unicode61
remove_diacritics 2`) pre otázky do minulosti („kedy som sa sťažoval na koleno“).

## Časy

Každý vlastný záznam má dva časy: **dátum udalosti** (lokálny dátum, kedy sa to stalo:
deň behu, deň bolesti, deň rozhodnutia) a **čas zápisu** (UTC s presnosťou na sekundu,
kedy to tréner zapísal). „Čo sa dialo v auguste“ triedi podľa dátumu udalosti; „čo sme sa
dohodli naposledy“ podľa času zápisu. Namerané záznamy majú časy z FIT (UTC) a lokálny čas
štartu.

## Vzťahy

- `plans.activity_id` → `runs` (ktorý beh predpis splnil); porovnanie po úsekoch používa
  `plan_segments` a `records` ([predpisy](prescriptions.md)).
- `journal.activity_id` / `journal.plan_id` voliteľne viažu záznam k behu alebo predpisu.
- `feelings` je samostatná tabuľka, aby pocit bol dotazovateľná hodnota, a zároveň sa
  zapíše aj ako `journal` záznam typu `feeling` kvôli chronológii.

## Čo do databázy nepatrí

- Prihlasovací token Garminu.
- Prepisy rozhovorov; iba závery ([rozhodnutie O6](../decisions/README.md#otvorené-rozhodnutia)).
