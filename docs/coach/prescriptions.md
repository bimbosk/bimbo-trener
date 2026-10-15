# Predpisy

Ako tréner vytvára, ukladá a vyhodnocuje predpisy. Formát, ktorý vyžadujem, vlastní
[formát predpisu](../running/workout-format.md); pravidlo pocitu
[hodnotenie](../running/evaluation.md).

## Predpis ako záznam

`plans` + 10 riadkov `plan_segments` ([dátový model](data-model.md)). Predpis má dátum, pre
ktorý platí, typ tréningu, celkový čas, stav a po odbehnutí odkaz na beh. Tréner ho zapíše
hneď, keď je dohodnutý, a zobrazí mi ho v textovom tvare.

## Ako tréner volí ďalší predpis

1. Načíta stav, posledné behy, pocity a predpisy ([pamäť](memory-and-journal.md)).
2. **Pocit z posledného behu**: „na hrane“ → ľahký alebo regeneračný; „ľahké“ → smie
   pridať; „v pohode“ → drží úroveň, mení typ.
3. **Rotácia typov**: nevyberie typ, ktorý bol v posledných dvoch dňoch; po dlhom behu
   nie intervaly; po intervaloch alebo kopcoch ľahký deň.
4. **Fáza plánu** (`training_plan`): v základe prevažujú ľahké a dlhé behy, v objeme rastie
   dlhý beh, neskôr pribúda tempo a intervaly.
5. **Progresia s brzdou** (všeobecné odporúčania, označené ako také): týždenný objem
   najviac o 10–15 %, dlhý beh najviac raz týždenne a najviac o 10 % dlhší než minulý,
   po výpadku dlhšom než týždeň návrat na nižší objem.
6. **Okolnosti** z denníka: bolesť, teplo, práca v záhrade znižujú náročnosť.
7. Zostaví 10 úsekov podľa formátu, desatiny prepočíta na sklon podľa
   [konvencie](../running/treadmill-conventions.md).

Či plánuje týždeň dopredu alebo vždy iba ďalší beh, je otvorené rozhodnutie O3.

## Porovnanie predpisu s realitou

Po importe behu, ktorý predpis splnil:

- úseky sa odvodia z `records` podľa času (10 rovnakých intervalov od začiatku pohybu),
  lebo hodinky robia kolá každý kilometer, nie podľa mojich úsekov; hodnoty úsekov sú
  odvodené;
- výsledok: tabuľka úsek → predpis → skutočnosť → tep, plus slovné zhodnotenie („v úseku 7
  pri 9 km/h a 1 % išiel tep na 135, pri rovnakom úseku pred týždňom 128“).

Odchýlky sa nehodnotia ako moja chyba; pás sa nastavuje ručne a pauzy sú bežné. Zapíšu sa
do `journal(note)` iba ak sú podstatné pre ďalší predpis.

## Dlhodobý plán

`training_plan` drží cieľ, fázy a míľniky (12 → 15 → 17 → 19 → 21,1 km). Míľnik sa
plánuje z dát (najdlhší beh, týždenný objem, pocit), nie z kalendára; dátum je odhad
a tak sa aj označí. Pri výpadku sa plán prepočíta a zapíše nová verzia s dôvodom.
