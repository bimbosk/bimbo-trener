# Stav projektu

Jediná stránka aktuálneho stavu. Pri zmene sa aktualizuje dátum aj text.

**Stav k 15. októbru 2026.** Projekt je v návrhovej fáze. Repozitár obsahuje pravidlá
agentov a túto dokumentáciu; kód, databáza ani inštalátor zatiaľ nevznikli.

## Podľa oblastí

| Oblasť | Stav | Podrobne |
| --- | --- | --- |
| Beh (moje konvencie) | Zapísané; aktuálne rýchlosti a výkonnosť bude držať stav trénera v databáze. | [Beh](../running/README.md) |
| Tréner (špecifikácia) | Navrhnuté: dátový adresár, dátový model, sťahovanie, import, pamäť, predpisy, rozhrania. Nič nie je implementované. | [Stav implementácie](../coach/implementation-status.md) |
| Aplikácia a inštalátor | Navrhnuté; nenapísané. | [Aplikácia](../application/README.md) |
| Integrácie | Garmin Connect: cesty a riziká preskúmané. Asistenti: spôsob napojenia navrhnutý. | [Integrácie](../integrations/README.md) |
| Používanie | Návody sú cieľový návrh. | [Používanie](../usage/README.md) |
| Dokumentácia | Založená 15. 10. 2026. | [Dokumentácia](documentation.md) |

## Najbližšie kroky

1. Uzavrieť [otvorené rozhodnutia](../decisions/README.md#otvorené-rozhodnutia).
2. Schéma databázy a import jedného FIT súboru exportovaného z Garmin Connect
   ([import FIT](../coach/fit-import.md)).
3. Pamäť: tabuľky denníka a stavu, skilly na načítanie a uloženie kontextu
   ([pamäť a denník](../coach/memory-and-journal.md)).
4. Skript sťahovania z Garmin Connect s cooldownom ([sťahovanie](../coach/garmin-sync.md)).
5. Inštalátor pre Windows a MCP server pre asistentov ([aplikácia](../application/README.md),
   [rozhrania](../coach/interfaces.md)).
6. Prvý týždeň reálnej prevádzky a zápis výsledku do dôkazov.
