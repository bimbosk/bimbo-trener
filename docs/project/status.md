# Stav projektu

Jediná stránka aktuálneho stavu. Pri zmene sa aktualizuje dátum aj text.

**Stav k 15. októbru 2026.** Projekt je v návrhovej fáze. Repozitár obsahuje pravidlá
agentov a túto dokumentáciu; kód, databáza ani inštalátor zatiaľ nevznikli. Špecifikácia
je úplná pre začatie implementácie: zariadenia sú známe (Venu 4, Index S2, Edge 1040),
obsah FIT súboru a polia Garmin Connect sú zinventarizované, verzie overené, rozhodnutia
zapísané. Otvorená ostáva iba podoba plánu a rozhovorov (O3), ktorá sa preberie po prvých
dátach.

## Podľa oblastí

| Oblasť | Stav | Podrobne |
| --- | --- | --- |
| Beh (moje konvencie) | Zapísané; aktuálne rýchlosti a výkonnosť bude držať stav trénera v databáze; namerané hodnoty v dokumentácii nie sú. | [Beh](../running/README.md) |
| Tréner (špecifikácia) | Navrhnuté: dátový adresár, dátový model, sťahovanie, import, pamäť, predpisy, rozhrania. Nič nie je implementované. | [Stav implementácie](../coach/implementation-status.md) |
| Aplikácia a inštalátor | Navrhnuté; nenapísané. | [Aplikácia](../application/README.md) |
| Integrácie | Garmin Connect: cesty, riziká, zariadenia a volania na denné dáta preskúmané. Asistenti: spôsob napojenia cez MCP navrhnutý. | [Integrácie](../integrations/README.md) |
| Používanie | Návody sú cieľový návrh. | [Používanie](../usage/README.md) |
| Dokumentácia | Založená 15. 10. 2026. | [Dokumentácia](documentation.md) |

## Najbližšie kroky

Zadanie pre implementáciu je v [implementačnom pláne](../../IMPLEMENTATION_PLAN.md).

1. Schéma databázy a import jedného FIT súboru exportovaného z Garmin Connect
   ([import FIT](../coach/fit-import.md)).
2. Pamäť: tabuľky denníka a stavu, skilly na načítanie a uloženie kontextu
   ([pamäť a denník](../coach/memory-and-journal.md)).
3. Skript sťahovania z Garmin Connect s cooldownom ([sťahovanie](../coach/garmin-sync.md)).
4. Inštalátor pre Windows a MCP server pre asistentov ([aplikácia](../application/README.md),
   [rozhrania](../coach/interfaces.md)).
5. Prvý týždeň reálnej prevádzky a zápis výsledku do dôkazov.
