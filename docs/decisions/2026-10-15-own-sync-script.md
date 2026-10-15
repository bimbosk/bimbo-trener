# Vlastný sťahovač nad garminconnect, nie GarminDB

**Dátum:** 15. 10. 2026 · **Stav:** platí · **Oblasť:** [Sťahovanie](../coach/garmin-sync.md)

## Rozhodnutie

Dáta z Garmin Connect sťahuje malý vlastný Python skript nad aktuálnou knižnicou
`python-garminconnect`, ktorý stiahne iba nové aktivity v originálnom FIT formáte a odovzdá
ich importu. Spúšťa sa na klik (skratka) aj plánovanou úlohou raz denne, oboje volá ten istý
kód. Ručný export z webu Garmin Connect ostáva záložnou cestou; hromadný export účtu slúži
na doplnenie histórie. GarminDB sa nepoužije.

## Dôvod

GarminDB prináša druhú databázu s cudzou schémou vedľa mojej, pevne viazanú staršiu verziu
knižnice, tichý úspech po neúspešnom prihlásení (kód 0) a sťahuje celý zdravotný profil.
Vlastný skript má jedno prostredie, jednu schému a aktuálnu knižnicu. Častejšie než denné
sťahovanie zvyšuje riziko blokácie účtu Garminom bez prínosu pri jednom behu denne.

## Dôsledky

- Skript sa nikdy neprihlasuje heslom automaticky; bez tokenov skončí s chybou, pri 429
  nastaví cooldown ([sťahovanie](../coach/garmin-sync.md)).
- Predvolená stratégia prihlasovania knižnice s `curl_cffi` sa nevypína.
- Na počítači bez prihlásenia do Garminu tlačidlo oznámi, že tu sťahovanie nie je
  nastavené; konzultácia funguje.
- Ak Garmin zmení prihlasovanie, do opravy knižnice sa používa ručný export.
