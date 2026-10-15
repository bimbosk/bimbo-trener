# Tréner — rozcestník

Špecifikácia softvérovej časti: ako sa dáta dostanú z Garminu do databázy, ako je databáza
členená, ako tréner drží pamäť, ako vznikajú predpisy a cez čo s databázou pracujú
asistenti. Kód vznikne v `scripts/` (zatiaľ neexistuje); inštaluje ho
[aplikácia](../application/README.md). Moje konvencie vlastní [Beh](../running/README.md).

**Záväznosť.** Stránky tejto oblasti spolu tvoria špecifikáciu. **MUSÍ / NESMIE** je
záväzná požiadavka; **MÁ** odporúčanie, odchýlku treba zdôvodniť; **otvorené** je v [registri](../decisions/README.md). Názvy tabuliek, príkazov a nástrojov sú
návrh, kým ich implementácia nepotvrdí. Všetko tu je k 15. 10. 2026 **navrhnuté, nie
implementované** ([stav implementácie](implementation-status.md)).

## 1. Čo a prečo

| Stránka | Čo tu nájdeš |
| --- | --- |
| [Cieľ a požiadavky](goal-and-requirements.md) | Produkt jednou vetou, príklady rozhovorov, pevné požiadavky MUSÍ/NESMIE, čo produkt nesľubuje. |
| [Architektúra](architecture.md) | Vrstvy nad SQLite, tok dát od hodiniek po odpoveď, čo beží kde. |

## 2. Dáta

| Stránka | Čo tu nájdeš |
| --- | --- |
| [Dátový adresár](data-directory.md) | Môj zdieľaný adresár: štruktúra, marker, výber a pripojenie, lokálny config, pravidlá pre sync. |
| [Dátový model](data-model.md) | Tabuľky SQLite, ich životnosť, čo je namerané a čo vlastné, fulltext. |
| [Sťahovanie z Garminu](garmin-sync.md) | Skript nad garminconnect: prihlásenie, cooldown, exit kódy, spúšťanie na klik a plánovane, záložné cesty. |
| [Import FIT](fit-import.md) | Z FIT súboru do tabuliek cez Garmin FIT SDK; idempotencia; čo sa počíta pri importe. |
| [Zálohy](backups.md) | Záloha pred importom nových dát, posledných 5, export denníka, obnova z FIT súborov. |

## 3. Tréner

| Stránka | Čo tu nájdeš |
| --- | --- |
| [Pamäť a denník](memory-and-journal.md) | Vrstvy pamäte, rozpočet kontextu, skilly načítaj/ulož, čo sa zapisuje kedy. |
| [Predpisy](prescriptions.md) | Predpis ako záznam, rotácia typov, progresia, porovnanie s realitou po úsekoch. |
| [Analýzy](analyses.md) | Odvodené ukazovatele: tempo pri rovnakom tepe, drift, ekvivalentná rýchlosť, reporty, varovania. |

## 4. Rozhrania a prevádzka

| Stránka | Čo tu nájdeš |
| --- | --- |
| [Rozhrania](interfaces.md) | Moduly, CLI príkazy, MCP nástroje a ich anotácie, skilly. |
| [Bezpečnosť](security.md) | Čo neopúšťa počítač, token, hranice ciest, čo MCP nesmie. |

## 5. Stav

| Stránka | Čo tu nájdeš |
| --- | --- |
| [Stav implementácie](implementation-status.md) | Etapy a čo je hotové (k 15. 10. 2026 nič). |
| [Backlog](backlog.md) | Možnosti navyše oproti Garmin Connect a kedy ich zaradiť. |
