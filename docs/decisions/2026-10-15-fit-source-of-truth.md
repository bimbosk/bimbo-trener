# FIT súbor ako zdroj pravdy nameraných dát

**Dátum:** 15. 10. 2026 · **Stav:** platí · **Oblasť:** [Import FIT](../coach/fit-import.md)

## Rozhodnutie

Namerané dáta o behu pochádzajú výhradne z originálneho FIT súboru z hodiniek, stiahnutého
z Garmin Connect alebo skopírovaného z hodiniek. Parsuje sa oficiálnym Garmin FIT SDK pre
Python. Screenshoty z Garmin Connect slúžia iba na kontrolu, nie ako zdroj.

## Dôvod

FIT súbor obsahuje všetko, čo Garmin zobrazuje, plus sekundový priebeh a kolá, a vlastný
export originálu je úplný vrátane Garmin metrík, ktoré partnerské API filtruje
([prieskum](../evidence/2026-10-15-garmin-research.md)). Čítanie zo screenshotu je nepresné
a porušuje pravidlo, že hodnoty sa nevymýšľajú.

## Dôsledky

- FIT súbory sa uchovávajú v dátovom adresári natrvalo, jeden na beh; nikdy sa neprepisujú
  ([dátový adresár](../coach/data-directory.md)).
- Databáza je z FIT súborov kedykoľvek znovu postaviteľná; to je posledná istota pri
  poškodení databázy alebo konflikte synchronizácie ([zálohy](../coach/backups.md)).
- Pole, ktoré FIT neobsahuje, ostáva v databáze prázdne.
- Hodnoty z môjho textu z 29. 8. 2026 sa do databázy nezapisujú; história príde ako FIT
  z Garmin Connect ([rozhodnutie O2](README.md#otvorené-rozhodnutia)).
