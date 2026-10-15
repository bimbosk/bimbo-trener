# Zálohy

Pred každým zápisom do databázy vzniká
záloha, drží sa posledných 10 a najstaršia sa maže. Zálohy sú v dátovom adresári, takže sa
synchronizujú spolu s databázou.

## Pravidlá

- MUSÍ: záloha cez SQLite online backup API (`Connection.backup`), nie kopírovanie súboru;
  kopírovanie otvorenej databázy môže dať nekonzistentný súbor.
- MUSÍ: názov `backups\runs-<RRRRMMDD-HHMMSS>.sqlite3`; po úspešnom zápise rotácia na 10.
- MUSÍ: záloha pred zápisom, nie po ňom; ak záloha zlyhá, zápis sa nevykoná a chyba je
  viditeľná.
- MUSÍ: okrem rotujúcich 10 aj jedna denná záloha držaná 30 dní
  (`backups\daily\`) a jedna mesačná držaná rok (`backups\monthly\`), aby chyba zistená po
  mesiaci neprepadla.
- Zálohy sa nikdy nemažú ručne skriptom mimo rotácie; môžem ich kopírovať kam chcem.

## Obnova

| Situácia | Postup |
| --- | --- |
| poškodená alebo nechcene zmenená databáza | zavrieť všetko, čo ju používa; `cli.py restore --from <záloha>` skopíruje zálohu na miesto databázy (pôvodná sa odloží s príponou `.broken-<čas>`) |
| konfliktná kópia zo sync nástroja | porovnať `meta` oboch súborov; ponechať novšiu, z druhej doimportovať FIT súbory a ručne preniesť záznamy denníka, ktoré v novšej chýbajú |
| strata databázy úplne | `cli.py rebuild`: nová databáza, import všetkých FIT súborov; denník, predpisy a stav sa vrátia z najnovšej zálohy |

FIT súbory a zálohy sú dve nezávislé cesty späť; preto sa FIT nikdy neprepisujú
([dátový adresár](data-directory.md)).
