# Zbierať všetko, čo Garmin dáva

**Dátum:** 15. 10. 2026 · **Stav:** platí · **Oblasť:** [Dátový model](../coach/data-model.md)

## Rozhodnutie

Sťahovač ukladá do databázy všetko, čo z môjho účtu Garmin Connect vie získať: všetky
aktivity (nie iba behy) s originálnymi FIT súbormi, a denné zdravotné dáta z hodiniek
Venu 4 a váhy Index S2 (hmotnosť a zloženie tela, pokojový tep, HRV, spánok, stres, Body
Battery, Training Readiness, Training Status, dýchanie, SpO2, kroky a intenzívne minúty).
Surové JSON odpovede sa uchovávajú vedľa normalizovaných stĺpcov.

## Dôvod

Zatiaľ nie je známe, ktoré dáta budú pre koučovanie užitočné; to sa zistí priebežne
z nazbieraných dát. Čo sa nestiahne dnes, sa neskôr dopĺňa ťažko (Garmin denné hodnoty
dopočítava a mení). Náklad je malý: niekoľko requestov navyše pri jednom dennom spustení.

## Dôsledky

- Tabuľky `daily_health` a `body_composition` plus surový JSON v `connect_raw`
  ([dátový model](../coach/data-model.md)).
- Sťahovač pri každom spustení znova stiahne denné dáta za posledné 4 dni a prepíše ich
  ([sťahovanie](../coach/garmin-sync.md)).
- Tréner tieto dáta číta iba ako denný súhrn (jedno číslo na deň a metriku); krivky po
  minútach sa do kontextu nenačítavajú ([pamäť a denník](../coach/memory-and-journal.md)).
- Rozhodnutie neduplikovať Garmin Connect ostáva: dáta sa zbierajú, nie zobrazujú
  ([rozhodnutie](2026-10-15-no-gui-no-web.md)).
