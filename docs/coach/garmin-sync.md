# Sťahovanie z Garmin Connect

Skript `garmin_sync` stiahne moje nové aktivity v originálnom FIT formáte a odovzdá ich
importu ([rozhodnutie](../decisions/2026-10-15-own-sync-script.md)). Vlastnosti účtu,
prihlásenia a limitov Garminu vlastní [Garmin Connect](../integrations/garmin-connect.md).

## Spúšťanie

| Spúšťač | Kedy | Čo urobí |
| --- | --- | --- |
| `sync.cmd` v koreni repozitára (dvojklik) | po behu, keď hodinky dosynchronizovali | spustí `scripts\sync.ps1`, ten nájde app vedľa repozitára a zavolá `cli.py sync`; na konci okno so správou: „1 nový beh: 15. 10., 7,0 km“ / „nič nové“ / „Garmin odmietol, skús o 90 minút“ / „na tomto PC nie je sťahovanie nastavené“ |
| skratka „Stiahni dáta z Garminu“ na ploche | to isté | inštalátor ju nasmeruje na kópiu `sync.cmd` v aplikácii; funguje aj bez otvoreného repozitára |
| skill „stiahni dáta“ v rozhovore | poviem trénerovi „stiahni dáta“ | skill `sync-garmin-data` spustí `sync.cmd`, prečíta jeho výsledok a tréner hneď pokračuje hodnotením nového behu ([rozhrania](interfaces.md)) |
| plánovaná úloha Windows | raz denne, napr. ráno, v režime Interactive (iba keď som prihlásený) | to isté bez okna; výsledok do logu |

## Správanie okna `sync.cmd`

`sync.cmd` otvorí jedno konzolové okno a nechá ho otvorené počas celého behu:

1. Hneď vypíše „Sťahujem dáta z Garminu…“ a potom priebeh po krokoch, ako ich skript hlási:
   prihlásenie tokenom, zoznam aktivít, stiahnutie každého FIT (názov a dátum), import,
   denné zdravotné dáta za posledné dni, záloha a zápis.
2. Na konci vypíše výsledok jedným riadkom: „HOTOVO: 1 nový beh: 15. 10., 7,0 km“ alebo
   „HOTOVO: nič nové“.
3. Pri úspechu počká 3 sekundy a okno sa samo zavrie.
4. Pri chybe (kód 75, 77 alebo 1) vypíše, čo sa stalo a čo robiť, a okno ostane otvorené,
   kým ho nezavriem; nič sa neskryje.

Skill „stiahni dáta“ a plánovaná úloha spúšťajú ten istý skript bez okna a čítajú výsledok
z logu a z `meta`.

Všetky cesty volajú ten istý `sync.cmd` → `cli.py sync`. Druhé súbežné spustenie sa odmietne
zámkom. Výsledok ide vždy aj do `logs\sync.log` a do `meta` v databáze, takže skill aj okno
čítajú ten istý stav.

## Postup jedného behu

1. Načítať konfiguráciu; ak `garmin_sync_enabled` nie je `true` alebo chýba token,
   skončiť kódom 77 bez jediného sieťového requestu.
2. Ak platí cooldown (súbor s časom), skončiť kódom 0 s informáciou.
3. Prihlásiť sa tokenom (`login(tokenstore)`); knižnica token obnoví sama. Nikdy
   neprihlasovať heslom.
4. Prečítať `meta.last_sync`; zoznam aktivít od tohto dátumu (`get_activities_by_date`),
   všetky typy; behy idú do `runs`, ostatné do `activities_other`. Ak zoznam je prázdny
   a denné dáta za posledné dni sa nezmenili, skončiť „nič nové“ bez zálohy a bez zápisu.
4a. Ak je čo zapísať: záloha databázy podľa [záloh](backups.md).
5. Pre každú novú aktivitu: `download_activity(..., ORIGINAL)` → ZIP → vybrať `.fit` →
   zapísať atomicky do `data/fit/<activity_id>.fit`. Existujúci súbor sa nesťahuje znova.
   Pauza 1 s medzi requestmi.
6. Zavolať import ([import FIT](fit-import.md)).
6a. Denné zdravotné dáta za posledné 4 dni: `get_user_summary`, `get_rhr_day`,
   `get_heart_rates`, `get_sleep_data`, `get_hrv_data`, `get_stress_data`,
   `get_body_battery`, `get_training_readiness`, `get_training_status`,
   `get_respiration_data`, `get_spo2_data`, `get_body_composition`; surový JSON do
   `connect_raw`, normalizované hodnoty do `daily_health` a `body_composition`
   (prepis, idempotentne). Pauza 1 s medzi requestmi; spolu rádovo 50 requestov.
7. Zapísať `meta.last_sync` (UTC), do logu súhrn, do `journal-export.jsonl` nič (import
   nie je zápis trénera).

## Chyby a kódy

| Kód | Význam | Reakcia |
| --- | --- | --- |
| 0 | OK alebo preskočené pre cooldown | — |
| 75 | 429 alebo prechodná sieťová chyba | nastaviť cooldown 90 min, správa v okne, skúsiť nabudúce |
| 77 | tokeny chýbajú alebo sú neplatné, alebo sťahovanie na tomto PC nie je zapnuté | správa s návodom: spustiť prihlásenie v konzole |
| 1 | neočakávaná chyba | traceback v logu, správa v okne |

Pri 403 po platnom prihlásení skript zaloguje, že Garmin blokuje klienta, a skončí 75.
Nikdy sa nepokúša obísť blokáciu rotáciou účtov, adries ani častým opakovaním.

## Prvé prihlásenie

Raz na každom počítači, kde sa má sťahovať, v konzole (`cli.py login`): e-mail, heslo bez
zobrazenia, MFA kód. Token sa uloží do `<app>\config\garmin` s obmedzenými právami
a po prihlásení sa explicitne uloží (knižnica potláča chybu zápisu). Heslo sa nikam
neukladá.

## Záložné cesty

- **Ručný export z webu:** connect.garmin.com → aktivita → ozubené koliesko → Export
  Original → ZIP do `data/fit/manual/`; import ho spracuje pri najbližšom spustení.
- **Kopírovanie z hodiniek:** kábel, Prieskumník, `GARMIN\Activity`, súbory do
  `data/fit/manual/` (MTP nemá písmeno disku, robocopy nefunguje).
- **Hromadný export účtu** na históriu: ZIP rozbaliť, FIT súbory do `data/fit/manual/`.

## Obmedzenia

- Skript ide do cloudu, nie do hodiniek: ak telefón beh ešte nenahral, nič nenájde.
- Knižnica je neoficiálna; pri zmene prihlasovania Garminom sa do opravy používa ručný
  export ([Garmin Connect](../integrations/garmin-connect.md)).
