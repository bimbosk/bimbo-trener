# Pamäť trénera mimo okna rozhovoru

**Dátum:** 15. 10. 2026 · **Stav:** platí · **Oblasť:** [Pamäť a denník](../coach/memory-and-journal.md)

## Rozhodnutie

Okno rozhovoru nie je pamäť. Všetko, čo stojí za zapamätanie, musí skončiť v dátovom
adresári (moje dáta) alebo v repozitári (pravidlá a dokumentácia). Každý rozhovor
o tréningu začína skillom „načítaj kontext“ a končí skillom „ulož dohodnuté“; predpis
a pocit sa zapisujú hneď, keď sú dohodnuté, ako poistka proti strate okna. Načítaný kontext
je vrstvený (stav → zhrnutia → posledné záznamy), aby ostal konštantný bez ohľadu na to,
koľko mesiacov dát pribudne.

## Dôvod

Keď sa kontextové okno naplní alebo zavrie, celý rozhovor zmizne pre každé iné okno a každý
počítač. Chcem konzultovať tréning pol roka a viac, denne pribúdajú dáta, a načítať do okna
celú históriu by bolo drahé a pomalé.

## Dôsledky

- Tabuľky `journal`, `summaries`, `coach_state`, `training_plan`
  ([dátový model](../coach/data-model.md)).
- Dva skilly v `.rulesync/` a inštrukcia, že rozhovor o tréningu sa bez načítania kontextu
  nezačína ([rozhrania](../coach/interfaces.md)); zmena chránených pokynov cez
  `maintain-agent-governance`.
- Z dvojhodinového rozhovoru ostanú závery, nie prepis; prepis je otvorená otázka O6.
