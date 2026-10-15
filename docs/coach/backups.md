# Zálohy

Záloha databázy je zviazaná so sťahovaním nových dát, nie s kalendárom ani s každým
zápisom. Sync nástroj tak prenáša denne najviac jeden nový súbor a jedno zmazanie.

## Mechanizmus

1. `sync.cmd` (alebo skill „stiahni dáta“) zistí z `meta.last_sync`, kedy bolo posledné
   sťahovanie, a od Garminu si vypýta iba to, čo je novšie ([sťahovanie](garmin-sync.md)).
2. **Ak nič nové nepribudlo**, skončí správou „nič nové“ a zálohu nerobí.
3. **Ak pribudlo**, pred prvým zápisom urobí zálohu živej databázy cez SQLite online backup
   API, skomprimuje ju a uloží ako `backups\runs-<RRRR-MM-DD>.sqlite3.gz` v dátovom
   adresári. Potom zmaže najstaršie zálohy nad limit.
4. Až potom stiahne, importuje a zapíše nový `meta.last_sync`.
5. Pred migráciou schémy alebo hromadnou zmenou dát vznikne záloha navyše
   `runs-<RRRR-MM-DD>-pre-migration.sqlite3.gz`, mimo rotácie, a výsledok migrácie sa overí
   voči nej (`CLAUDE.md`, Dáta o behoch).

Limit drží `backups.keep` v `bimbo-trener.json`, predvolene **5**
([konfigurácia](data-directory.md)). Záloha musí vzniknúť pred zápisom; ak zlyhá, zápis sa
nevykoná a chyba je viditeľná. Druhé spustenie v ten istý deň, keď už záloha s dnešným
dátumom existuje, novú nerobí.

## Živá databáza

`runs.sqlite3` v dátovom adresári má pevný názov, nikdy sa nepremenúva ani nekopíruje
inam; je jediným zdrojom na všetkých počítačoch.

## Export denníka

Všetko, čo zapíše tréner alebo ja (denník, pocity, predpisy, stav, zhrnutia), sa po každom
zápise doplní jedným riadkom do `journal-export.jsonl` v dátovom adresári, iba pridávaním.
Súbor je malý, synchronizuje sa a konflikt sync nástroja v ňom nič neprepíše. Je to poistka
pre nenahraditeľné dáta medzi dvoma zálohami.

## Obnova

| Situácia | Postup |
| --- | --- |
| poškodená alebo nechcene zmenená databáza | zavrieť všetko, čo ju používa; `cli.py restore --from <záloha>` rozbalí zálohu na miesto databázy (pôvodná sa odloží s príponou `.broken-<čas>`); záznamy z `journal-export.jsonl` novšie než záloha sa doplnia |
| konfliktná kópia zo sync nástroja | porovnať `meta` oboch súborov; ponechať novšiu, z druhej doimportovať FIT súbory a doplniť záznamy z exportu denníka |
| strata databázy úplne | `cli.py rebuild`: nová databáza, import všetkých FIT súborov a surového JSON, denník, predpisy a stav z `journal-export.jsonl` |

FIT súbory, surový JSON a export denníka sa nikdy neprepisujú; sú poslednou istotou bez
ohľadu na zálohy.
