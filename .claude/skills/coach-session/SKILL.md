---
name: coach-session
description: >-
  Použi pri každom rozhovore o mojich behoch, pocitoch, predpisoch alebo
  tréningovom pláne, vrátane otázok „ako mi to išlo“ a „kde som“. Preskoč
  prácu na kóde a dokumentácii repozitára.
---
# Rozhovor s trénerom

## Na začiatku: načítaj kontext

Cez MCP `bimbo_trener` zavolaj `get_state`, `recent_journal(7)`,
`recent_runs(3)` a `recent_health(3)`. Nič viac, kým sa nepýtam na staršie
veci; vtedy `search_journal` alebo `analysis`. Ak chýba dnešný beh, ponúkni
skill `sync-garmin-data`.

## Počas rozhovoru: zapisuj hneď

- Pocit po behu (`easy`/`ok`/`hard`) → `add_feeling` s dátumom behu.
- Bolesť, teplo, spánok, práca v záhrade, výpadok → `add_journal`
  `circumstance` s dátumom udalosti.
- Dohodnutý predpis → skill `prescribe-workout` (zapíše `save_plan`).
- Zmena plánu alebo pravidla a dôvod → `add_journal` `decision`.

Namerané hodnoty nikdy nemeň ani nedopĺňaj; chýbajúce pomenuj. Každé
tvrdenie označ: namerané, odvodené (`source=derived`), odhad, odporúčanie.
Môj pocit má prednosť pred číslami („na hrane“ = nepridávať).

## Na konci: ulož dohodnuté

Keď rozhovor smeruje k záveru alebo poviem „ulož dohodnuté“:

1. Porovnaj závery rozhovoru so zápismi a doplň chýbajúce.
2. `add_journal` `conversation_summary` (3–10 viet, nie prepis).
3. `update_state`: kde som, čo je na rade, posledné rozhodnutia, otvorené
   veci.
4. Nový týždeň alebo mesiac → `add_summary`.
5. Ukáž mi, čo si zapísal.
