# Sťahovanie z Garmin Connect

Skript `garmin_sync` stiahne moje nové aktivity v originálnom FIT formáte a odovzdá ich
importu ([rozhodnutie](../decisions/2026-10-15-own-sync-script.md)). Vlastnosti účtu,
prihlásenia a limitov Garminu vlastní [Garmin Connect](../integrations/garmin-connect.md).

## Spúšťanie

| Spúšťač | Kedy | Čo urobí |
| --- | --- | --- |
| skratka „Stiahni dáta z Garminu“ na ploche | po behu, keď hodinky dosynchronizovali | spustí ten istý skript a ukáže správu: „1 nový beh: 15. 10. 5,90 km“ / „nič nové“ / „Garmin odmietol, skús o 90 minút“ / „na tomto PC nie je sťahovanie nastavené“ |
| plánovaná úloha Windows | raz denne, napr. ráno, v režime Interactive (iba keď som prihlásený) | to isté bez okna; výsledok do logu |

Obidva volajú `cli.py sync`. Druhé súbežné spustenie sa odmietne zámkom.

## Postup jedného behu

1. Načítať lokálny config; ak `garmin_sync_enabled` nie je `true` alebo chýba token,
   skončiť kódom 77 bez jediného sieťového requestu.
2. Ak platí cooldown (súbor s časom), skončiť kódom 0 s informáciou.
3. Prihlásiť sa tokenom (`login(tokenstore)`); knižnica token obnoví sama. Nikdy
   neprihlasovať heslom.
4. Zoznam aktivít od posledného známeho dátumu (`get_activities_by_date`), filtrovať beh.
5. Pre každú novú aktivitu: `download_activity(..., ORIGINAL)` → ZIP → vybrať `.fit` →
   zapísať atomicky do `data/fit/<activity_id>.fit`. Existujúci súbor sa nesťahuje znova.
   Pauza 1 s medzi requestmi.
6. Zavolať import ([import FIT](fit-import.md)).
7. Zapísať do `meta` čas synchronizácie, do logu súhrn.

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
