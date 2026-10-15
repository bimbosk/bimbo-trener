# Analýzy

Odvodené ukazovatele, ktoré tréner počíta z nameraných dát na vyžiadanie. Každý výstup
nesie označenie zdroja ([hodnotenie](../running/evaluation.md)). Počítajú sa vo vrstve
analýz, nie pri importe ([import FIT](fit-import.md)).

## Ukazovatele

| Ukazovateľ | Výpočet | Zdroj | Načo |
| --- | --- | --- | --- |
| tempo pri rovnakom tepe | pre behy na páse priemerné tempo v minútach, kde bol tep v pásme ±3 od referenčného (napr. 115); trend v čase | odvodené | hlavný ukazovateľ pokroku pri nízkom a stabilnom tepe; Garmin VO2max je na páse bez GPS nespoľahlivý |
| tepový drift | rozdiel priemerného tepu medzi 10.–20. a poslednými 10 minútami pri rovnakom tempe, v dlhých behoch | odvodené | klesajúci drift = rastúca vytrvalosť |
| ekvivalentná rýchlosť | rýchlosť + 0,4 × sklon % podľa mojej konvencie | odvodené z konvencie | porovnať behy so sklonom a bez |
| týždenný a mesačný objem | súčet vzdialenosti a času pohybu, počet behov, najdlhší beh | odvodené (súčet) | progresia, varovania |
| podiel typov tréningu | z `plans.type` za obdobie | odvodené | pestrosť |
| pripravenosť na míľnik | z najdlhšieho behu, objemu a driftu | **odhad** | plánovanie; nikdy nie ako fakt |

## Reporty slovami

Týždenný a mesačný report sú text, nie graf: „tento mesiac 14 behov, 98 km, najdlhší 12 km,
tempo pri tepe 115 sa zlepšilo z 7:45 na 7:20“. Ukladajú sa ako `summaries`
([pamäť](memory-and-journal.md)).

## Varovania

Tréner pomenuje, rozhodnutie nechá mne:

- tep vyšší o 10 a viac pri rovnakom tempe tri behy po sebe,
- skok týždenného objemu nad 15 %,
- opakovaná zmienka bolesti v denníku (dva a viac záznamov za dva týždne),
- viac než 7 dní bez behu bez zapísaného dôvodu.

## Čo sa neanalyzuje

Spánok, stres, Body Battery, kroky: Garmin ich zobrazuje; tréner si ich vypýta odo mňa
vetou, ak ich potrebuje ([účel](../project/purpose.md)).
