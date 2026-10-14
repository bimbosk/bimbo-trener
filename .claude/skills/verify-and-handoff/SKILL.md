---
name: verify-and-handoff
description: >-
  Použi, keď overenie vyžaduje netriviálny výber kontrol alebo posúdenie
  dôkazov: zlyhania treba klasifikovať, výsledky môžu byť zastarané, tvrdenia o
  úplnosti vygenerovaných výstupov či refaktoringu treba dokázať, alebo
  recenzent nemá prístup k repozitáru. Preskoč bežné dokončenie úlohy, rutinné
  reportovanie a priamočiare povinné kontroly.
---
# Overenie a odovzdanie

## Prispôsob kontroly tvrdeniu

- Dodrž kontroly a ich načasovanie, ktoré vyžaduje zadanie, úloha alebo
  vlastník.
- Počas iterácie zvoľ najmenšiu kontrolu syntaxe, jednotky, kontraktu alebo
  cielenej integrácie, ktorá otestuje zmenené správanie alebo aktuálnu
  hypotézu. Rozšír ju podľa dotknutých hraníc, rizika, povinných kontraktov a
  finálneho tvrdenia; široké sady nespúšťaj zo zvyku.
- Rešpektuj samostatne zadané fázy review či validácie bez ich duplikovania.
  Neskoršia fáza nenahrádza povinné lokálne kontroly ani dôkazy o dopade na
  repozitár, ktoré sama získať nevie.
- Výsledok znovu použi iba dovtedy, kým ho testovaný kód, relevantné vstupy,
  závislosti, konfigurácia a prostredie stále podporujú. Spusti znova, keď
  relevantné zmeny dôkaz zneplatnia alebo je potrebné nezávislé zopakovanie.

## Testuj zmysluplné správanie

- Ak je to vhodné, pridaj regresný test, ktorý na pôvodnej chybe zlyhá. Testuj
  správanie, zlyhania a invarianty, nie náhodný text, pravopis zdrojov či čísla
  fáz. Presný text je vhodný pre strojovo spracúvané alebo bezpečnostné
  kontrakty.
- Očakávania drž nezávislé od potenciálne chybnej implementácie. Testuj
  skutočné vstupné body iba s ich dostupnými závislosťami.
- Pri vygenerovaných artefaktoch kontroluj zhodu aj úplnosť. Pri refaktoringu
  kontroluj zachovanie obmedzení a negatívne prípady, nielen úspešné
  spracovanie či beh.
- Testy nikdy nemeň len preto, aby zakryli regresiu.

## Klasifikuj zlyhania podľa dôkazov

Každú zlyhanú povinnú kontrolu klasifikuj ako:

1. **spôsobená zmenou** — oprav v rámci povoleného rozsahu;
2. **potvrdene existujúca predtým** — uveď dôkaz, ktorý tento stav preukazuje;
3. **blokovaná prostredím** — uveď nedostupné prostredie a tvrdenie, ktoré
   zostáva neoverené;
4. **nevyriešená** — uveď, čo sa pozorovalo a čo sa vylúčilo.

Zlyhanie neoznačuj za predtým existujúce bez dôkazu a zadanie nerozširuj len
kvôli zelenému výsledku.

Pri tvrdeniach o lokalite zmien vyskúšaj, ak je to užitočné, reprezentatívnu
zmenu na jednorazovej kópii; inak výsledok označ ako odhad. Zdroje, testy,
vygenerované výstupy, presuny a históriu počítaj zvlášť, nie ako hrubý objem
diffu.

## Referuj a odovzdaj

- Povolenými metódami skontroluj finálne zmeny úlohy na neúmyselné rozšírenie
  rozsahu, dočasnú diagnostiku a nechcené artefakty.
- Uveď skutočné výsledky, kontroly a ich výsledky, obmedzenia, blokery,
  otvorené rozhodnutia, zámerné zmeny kompatibility a čakajúcu prácu
  vlastníka.
- Nikdy netvrď, že niečo funguje alebo je overené, ak sa presne táto vlastnosť
  neoverila. Pri analýzach uveď, aké dáta pokrývajú a čo chýba.
- Uveď vynechané kontroly; nesplnené povinné kontroly znamenajú neúplné alebo
  blokované overenie, nie úspech.

Keď recenzent nemá prístup k repozitáru, poskytni dohodnutým kanálom kompaktný
balík na review: úlohu a kritériá prijatia; stav úlohy; zmenené miesta;
relevantné výňatky diffu, kódu a testov; potrebný kontext kontraktov;
posúdený dopad; presné kontroly a výsledky; a výslovné vynechania, hranice
vyhľadávania, inferencie a chýbajúce dôkazy. Samotné cesty alebo sebavedomé
zhrnutie nestačia, ale neposielaj celý repozitár. Samostatný report vytvor
iba na požiadanie alebo keď je povinný.
