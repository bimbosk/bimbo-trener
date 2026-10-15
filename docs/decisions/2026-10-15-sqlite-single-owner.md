# SQLite ako jediný vlastník, zápis rovno do databázy, bez vektorovej databázy

**Dátum:** 15. 10. 2026 · **Stav:** platí · **Oblasť:** [Dátový model](../coach/data-model.md)

## Rozhodnutie

Jedna SQLite databáza v dátovom adresári je jediným miestom, kde zapisované dáta žijú:
behy, kolá, sekundové záznamy, predpisy, pocity, denník, zhrnutia, stav trénera, dlhodobý
plán a konvencie. Markdown súbory nie sú úložisko; generujú sa z databázy iba ako náhľad na
čítanie a dajú sa kedykoľvek zmazať. Predpis a závery rozhovoru sa zapisujú rovno do
databázy, nie cez medzisúbory. Vektorová databáza sa nepoužije.

## Dôvod

Jedna forma úložiska, jeden vlastník. Obavu z poškodenia jedného súboru rieši záloha pred
každým zápisom. Denník sa viaže na konkrétne behy a dni, takže patrí k nim. Medzisúbory by
chránili iba pred súčasným zápisom z dvoch počítačov, ktorý pri jednom používateľovi
nenastáva. Otázky typu „posledné diskusie“ sú zoradenie podľa dátumu, nie významové
vyhľadávanie; pri stovkách krátkych záznamov stačí dátum a fulltext SQLite.

## Dôsledky

- Schéma má oddelené tabuľky podľa životnosti dát (denník sa iba pridáva, stav sa
  prepisuje, plán sa mení zriedka) ([dátový model](../coach/data-model.md)).
- Pred každým zápisom vzniká záloha cez SQLite backup API ([zálohy](../coach/backups.md)).
- MCP server a skilly zapisujú cez nástroje projektu, nikdy priamym SQL
  ([rozhrania](../coach/interfaces.md)).
- Fulltext (FTS5) nad denníkom a zhrnutiami pre otázky do minulosti; vektorový index sa
  zváži až pri tisíckach záznamov ako samostatné rozhodnutie.
