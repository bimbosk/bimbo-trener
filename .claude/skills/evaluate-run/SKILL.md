---
name: evaluate-run
description: >-
  Použi, keď hodnotím odbehnutý beh („ako to dnes šlo“, „pozri na včerajší
  beh“) alebo keď po importe pribudol nový beh. Preskoč tvorbu predpisu.
---
# Hodnotenie behu

1. `recent_runs(1)`; ak má beh `plan_id`, `compare_plan_run(activity_id)`.
   Bez spárovaného predpisu porovnaj iba s predchádzajúcimi behmi.
2. Uveď namerané: vzdialenosť, čas pohybu, tep priem./max, kadencia,
   Training Effect. Odvodené označ (`source=derived`): úseky z času, nie
   z kilometrových kôl; rýchlosť hodiniek na páse kolíše okolo nastavenej.
3. Spýtaj sa na pocit, ak chýba, a zapíš `add_feeling`; okolnosti
   `add_journal` `circumstance`.
4. `analysis("warnings")`: varovania pomenuj, rozhodnutie nechaj mne.
5. Odchýlky od predpisu nie sú chyba; pás sa nastavuje ručne. Zapíš iba to,
   čo ovplyvní ďalší predpis (`add_journal` `note`).
