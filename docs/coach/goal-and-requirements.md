# Cieľ a požiadavky

## Produkt jednou vetou

Lokálny tréner, ktorý každý deň stiahne môj beh z Garmin Connect do synchronizovanej
databázy a cez Claude Code alebo Codex mu k nemu dá hodnotenie, ďalší predpis v jeho formáte
a dlhodobý plán, pričom si pamätá všetko, čo sa dohodlo.

## Príklady rozhovorov

- „Včera som bežal, bolo to v pohode, ale ľavé koleno trochu ťahalo.“ → tréner stiahne beh,
  zapíše pocit a koleno, porovná s predpisom, dá predpis na zajtra s ohľadom na koleno.
- „Daj mi predpis.“ → 10 úsekov podľa [formátu](../running/workout-format.md), iný typ než
  posledné dni, zapísaný do databázy.
- „Ako som na tom s kolenom, mám dnes bežať?“ (na inom počítači, v novom okne) → tréner
  načíta stav a posledné dni a odpovie s kontextom.
- „Čo sme robili v auguste a prečo sme pridali intervaly?“ → mesačné zhrnutie a záznam dňa
  s rozhodnutím.
- „Naplánuj mi ďalšie dva mesiace k 15 km.“ → plán s fázami a míľnikmi zapísaný do
  databázy.

## Požiadavky

### Dáta

- MUSÍ: namerané hodnoty pochádzajú z FIT súboru; chýbajúce ostávajú prázdne; nič sa
  nevymýšľa ani potichu neopravuje ([rozhodnutie](../decisions/2026-10-15-fit-source-of-truth.md)).
- MUSÍ: všetky zapisované dáta sú v jednej SQLite databáze v dátovom adresári
  ([rozhodnutie](../decisions/2026-10-15-sqlite-single-owner.md)).
- MUSÍ: pred každým zápisom vznikne záloha ([zálohy](backups.md)).
- MUSÍ: databáza je z FIT súborov znovu postaviteľná.
- NESMIE: dáta o behoch a zdraví opustiť moje počítače okrem Garmin Connect
  ([bezpečnosť](security.md)).

### Sťahovanie

- MUSÍ: jedno spustenie stiahne iba nové aktivity a denné zdravotné dáta za posledné dni;
  opakované spustenie nič nezduplikuje.
- MUSÍ: pri chýbajúcich tokenoch skončiť s jasnou správou bez pokusu o prihlásenie heslom;
  pri 429 nastaviť cooldown a skončiť.
- MUSÍ: skratka aj plánovaná úloha volajú ten istý kód.
- NESMIE: prihlasovať sa v slučke ani častejšie než raz denne automaticky.

### Pamäť

- MUSÍ: rozhovor o tréningu začína načítaním stavu a posledných záznamov a končí zápisom
  dohodnutého ([pamäť a denník](memory-and-journal.md)).
- MUSÍ: predpis a pocit sa zapíšu hneď, keď sú dohodnuté.
- MUSÍ: načítaný kontext pre bežnú otázku ostáva rádovo v tisícoch tokenov bez ohľadu na
  dĺžku histórie.
- NESMIE: pamäť závisieť od konkrétneho asistenta alebo okna.

### Predpisy a hodnotenie

- MUSÍ: predpis dodrží [formát](../running/workout-format.md) a pravidlo pocitu
  ([hodnotenie](../running/evaluation.md)).
- MUSÍ: každé tvrdenie v hodnotení má označený zdroj (namerané / odvodené / odhad /
  odporúčanie).
- MÁ: porovnať predpis s realitou po úsekoch, keď FIT obsahuje kolá alebo sa úseky dajú
  odvodiť z času.

### Prevádzka

- MUSÍ: funguje na Windows bez globálnych zmien systému
  ([aplikácia](../application/README.md)).
- MUSÍ: funguje na počítači bez prihlásenia do Garminu v režime iba čítanie a radenie.
- MUSÍ: zlyhanie je viditeľné; žiadny stav, ktorý iba vyzerá ako úspech.

## Čo produkt nesľubuje

- Zrkadlo Garmin Connect, grafy, mapy, spánok, Body Battery.
- Oficiálne garantovaný prístup k Garminu; neoficiálna knižnica môže prestať fungovať
  ([Garmin Connect](../integrations/garmin-connect.md)).
- Lekársku alebo profesionálnu trénerskú radu.
- Okamžitú dostupnosť behu po jeho skončení: závisí od synchronizácie hodiniek do cloudu.
