# Bežný deň

**Návrh; aplikácia ešte neexistuje.**

1. **Beh** na páse podľa predpisu. Hodinky uložia aktivitu a telefón ju pošle do Garmin
   Connect (ak to trvá, potiahnem v aplikácii Garmin nadol).
2. **Stiahnutie dát:** na počítači s prihlásením dvojklik na skratku **Stiahni dáta
   z Garminu**. Objaví sa správa: „1 nový beh: 15. 10., 5,90 km“ alebo „nič nové“. Ak
   Garmin odmietne, správa povie, kedy skúsiť znova; nič neopakujem hneď. Raz denne to
   prebehne aj samo, ak som pri počítači.
3. **Rozhovor s trénerom** v Claude Code alebo Codexe, na ktoromkoľvek počítači:

   > Včera som bežal, bolo to v pohode, ale ľavé koleno trochu ťahalo.

   Tréner si načíta môj stav, pozrie beh, porovná ho s predpisom, zapíše pocit a koleno
   a navrhne predpis na zajtra. Predpis má vždy 10 rovnakých úsekov.

4. **Koniec rozhovoru:** poviem „ulož dohodnuté“ alebo to tréner urobí sám. Ukáže mi, čo
   zapísal. Od tej chvíle to vidí každý počítač a každé nové okno.

## Keď nebežím

Poviem to trénerovi s dôvodom („horúčava“, „kopal som v záhrade“, „bolí koleno“). Zapíše
to a zohľadní; niekoľko dní bez behu nie je problém.

## Keď skratka nefunguje

Beh si stiahnem ručne: na webe Garmin Connect otvorím aktivitu, kliknem na ozubené koliesko
a **Export Original**. Stiahnutý súbor presuniem do priečinka `fit\manual` v dátovom
adresári a poviem trénerovi „importuj“. Pri opakovaných problémoch je príčina v priečinku
`logs` v `bimbo-trener-app`.
