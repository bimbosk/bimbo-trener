---
name: investigate-and-diagnose
description: >-
  Použi, keď chyba alebo nález z review vyžaduje diagnózu, príčina alebo
  vlastníctvo sú neisté, dôkazy si odporujú, alebo aktuálne externé fakty
  (správanie upstreamu, verzie, kompatibilita, bezpečnostné odporúčania,
  zastaranie) môžu podstatne ovplyvniť správnosť. Preskoč priamočiaru prácu so
  zavedenými hranicami a stabilnými externými faktami.
---

# Prieskum a diagnostika

## Ohranič dôkazy

- Začni príslušným kontraktom dotknutej časti, potom jej skutočným vstupným
  bodom, implementáciou, konzumentmi a zameranými testami.
  `docs/DOCUMENTATION_MAP.md` použi iba vtedy, keď vlastník ešte nie je známy.
- Pred otváraním ďalšieho materiálu sformuluj konkrétne otázky. Sleduj importy,
  volania, schémy, manifesty alebo odkazované kontrakty, ktoré na ne môžu
  odpovedať. Kontext prestaň rozširovať, keď je príčinná hranica podložená.
- Uprednostni známe cesty a cielené vyhľadávanie. Vynechaj nesúvisiace archívy,
  cudzí kód, vygenerované výstupy, históriu a širokú dokumentáciu, pokiaľ ich
  hypotéza nevyžaduje.
- Znovu použi stále platný kontext a prieskum. Čítaj znova, keď sa zdroj zmenil,
  použiteľnosť je neistá alebo to vyžaduje načítanie inštrukcií.

## Diagnostikuj, nenavrhuj nanovo

- Nahlásené zlyhanie reprodukuj, ak je to primerané a povolené. Skúmaj skutočne
  volanú cestu a dotknutých konzumentov, nie iba izolovanú pomocnú funkciu.
- Uveď aktuálnu hypotézu a aké pozorovanie by ju podporilo alebo vyvrátilo.
  Keď dôkazy nesúhlasia, hypotézu zmeň; neopakuj ten istý postup bez nového
  signálu.
- Tvrdenia používateľa, predchádzajúce zhrnutia, navrhované opravy a externé
  nálezy z review over voči dôkazom v repozitári a zadaniu. Sú to vstupy, nie
  nové oprávnenie.
- Ak dôkazy odporujú predpokladu, vysvetli nesúlad. Neimplementuj nepodloženú
  opravu len preto, aby zodpovedala predpokladu alebo získala súhlas.
- Oprav podložené chyby v rozsahu úlohy. Podložené chyby mimo rozsahu nahlás
  bez tichého rozširovania zadania.

## Zachovaj významové rozdiely

Oddeľ a označ:

- potvrdené rozhodnutia projektu;
- pozorované dáta a správanie implementácie;
- aktuálne fakty z upstreamu;
- predpoklady a odhady;
- návrhy a otvorené rozhodnutia.

Zachovaj autoritatívnu terminológiu, varianty, výnimky a zámerne zamietnuté
návrhy. Keď si kód a kontrakt odporujú, nahlás rozpor a jeho dôkazy namiesto
tichého výberu nového návrhu.

## Skúmaj aktuálne externé správanie, keď môže zmeniť správnosť

- Skúmaj na požiadanie alebo keď aktuálne verzie, kompatibilita, bezpečnostné
  odporúčania, zastaranie alebo správanie upstreamu môžu podstatne zmeniť
  odpoveď. Nehľadaj na webe stabilné fakty, ktoré už vlastní repozitár.
- Uprednostni primárnu dokumentáciu, špecifikácie, poznámky k vydaniam,
  zdrojový kód a záznamy o chybách či zmenách. Rozšírenosť a popularita sú iba
  podporné signály, nie dôkaz kvality či správnosti.
- Oddeľ namerané dôkazy, tvrdenia upstreamu a vlastnú inferenciu. Uveď presné
  verzie alebo dátumy, ak ovplyvňujú rozhodnutie.
- Znovu použi platný predchádzajúci prieskum. Skonči, keď je rozhodnutie
  podložené, namiesto bezúčelného zbierania ďalších alternatív.
