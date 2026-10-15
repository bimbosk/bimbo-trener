# Import FIT

Z FIT súboru do tabuliek `runs`, `laps`, `records`, `events` cez oficiálne Garmin FIT SDK
([rozhodnutie](../decisions/2026-10-15-fit-source-of-truth.md)).

## Vstup

Všetky `.fit` súbory v `data/fit/` a `data/fit/manual/`, ktoré ešte nie sú v `runs`
(podľa identifikátora aktivity z FIT alebo z názvu súboru). Import je idempotentný: ten istý
súbor druhýkrát nič nezmení.

## Postup

1. `Decoder(Stream.from_file(path)).read()` → `messages`, `errors`. Chyby dekódovania sa
   zapíšu do logu a do `runs.import_errors`; súbor sa neimportuje potichu čiastočne bez
   označenia.
2. `session_mesgs` → jeden riadok `runs`. Mapovanie polí FIT → stĺpce drží `fit_import.py`;
   pole, ktoré v správe nie je, ostáva `NULL`.
3. `lap_mesgs` → `laps`; `record_mesgs` → `records`; `event_mesgs` → `events`.
4. Miesto (pás/vonku) z `sub_sport` (`treadmill`, `generic`, …); ak chýba, `NULL`, nie
   odhad.
5. Pred zápisom záloha databázy ([zálohy](backups.md)); zápis v jednej transakcii.
6. Po importe: pokus o spárovanie s predpisom na ten deň (`plans.status = proposed`,
   dátum sa zhoduje) → `plans.activity_id`, stav `done`
   ([predpisy](prescriptions.md)). Nejednoznačné prípady sa nepárujú a zapíšu do logu.

## Čo sa pri importe nepočíta

Odvodené ukazovatele (ekvivalentná rýchlosť, drift, tempo pri tepe) sa počítajú na
vyžiadanie vo vrstve analýz, nie pri importe, aby zmena vzorca nevyžadovala reimport
([analýzy](analyses.md)).

## Dáta z môjho textu z 29. 8. 2026

Štyri behy bez dátumu ([dôkaz](../evidence/2026-08-29-baseline.md)) sa dajú zapísať do
`runs` iba so `source = owner_text`, bez `activity_id` z Garminu a s dátumom `NULL` alebo
odhadom označeným v poznámke. Či sa to urobí, je otvorené rozhodnutie O2; prednosť má
hromadný export účtu, ktorý prinesie ich FIT súbory.

## Overenie importu

Prvý import sa overí porovnaním stĺpcov `runs` s hodnotami na webe Garmin Connect pre ten
istý beh (vzdialenosť, čas pohybu, tep) a zapíše sa ako dôkaz.
