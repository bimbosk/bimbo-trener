---
name: maintain-project-documentation
description: >-
  Použi pri vytváraní, organizovaní, delení, zlučovaní, presúvaní alebo rušení
  trvalej projektovej dokumentácie alebo pri zmene jej navigácie či vlastníctva.
  Preskoč bežné úpravy v rámci zavedeného dokumentu.
---
# Údržba projektovej dokumentácie

## Čítaj dokumentáciu postupne

- Ak je vlastník známy, začni tam. Inak použi `docs/DOCUMENTATION_MAP.md` na
  výber najužšieho relevantného vlastníka.
- Mapu a iné indexy ber ako navigáciu, nie ako zoznamy na čítanie. Hlbšie
  odkazy sleduj iba dovtedy, kým odpovedajú na konkrétnu potrebu úlohy.
- Rozlišuj autoritatívnych vlastníkov od indexov, vysvetlení, príkladov,
  dôkazov a histórie.

## Vyber prirodzeného vlastníka

- Trvalú dokumentáciu vytvor, keď poznatok musí prežiť úlohu a nemá lepšieho
  vlastníka v kóde, konfigurácii, schémach, testoch ani v existujúcom súdržnom
  dokumente.
- Existujúci dokument rozšír, keď poznatok zdieľa jeho zodpovednosť,
  autoritu, životný cyklus, publikum a lokalitu zmien.
- Nového vlastníka vytvor alebo dokument rozdeľ, keď sa niektorá z týchto
  hraníc podstatne líši. Nedeľ iba preto, že je dokument dlhý, nevytváraj
  zástupné stromy a nehromaď nesúvisiace poznatky v jednom monolite.
- Ak je to relevantné, oddeľ zamýšľaný návrh, aktuálny stav, kontrakty,
  prevádzkové pokyny, prieskum či dôkazy, historické rozhodnutia a príklady.
  Ide o rozdiely vo vlastníctve, nie o povinné adresáre.

## Udržuj navigačnú mapu

- Keď sa vlastník vytvorí, presunie, premenuje, rozdelí, zlúči alebo zruší,
  aktualizuj `docs/DOCUMENTATION_MAP.md` v tej istej súdržnej zmene.
- Témy smeruj na existujúcich kanonických vlastníkov bez kopírovania ich obsahu.
  Neuvádzaj hypotetických vlastníkov, neplatné odkazy ani zavádzajúce tvrdenia
  o autorite.
- Mapu drž kompaktnú aj pri raste dokumentácie. Neautoritatívne indexy,
  príklady, dôkazy, stav a historický materiál označ podľa ich skutočnej úlohy.
- Over dotknuté odkazy a potvrď, že po zmene má každý trvalý fakt jedného
  prirodzeného vlastníka.
