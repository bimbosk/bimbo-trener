---
name: prescribe-workout
description: >-
  Použi, keď žiadam predpis alebo plán tréningu na pás („daj mi predpis“,
  „čo mám zajtra bežať“). Preskoč hodnotenie odbehnutého behu.
---

# Predpis na pás

Formát je záväzný ([docs/running/workout-format.md](../../docs/running/workout-format.md)):

- presne 10 rovnako dlhých úsekov; riadok `úsek – čas – rýchlosť – sklon`;
  celkový čas;
- iba celé rýchlosti v km/h, desatiny cez sklon (1 % ≈ 0,4 km/h); nikdy
  6 km/h;
- typ a dĺžku striedaj; nie stále 50 min pri 8 km/h.

Postup: z `get_state`, `recent_runs(3)` a `list_plans(5)` zisti posledný
pocit, typy posledných dní a fázu plánu. „Na hrane“ → ľahký alebo
regeneračný; „ľahké“ → smieš pridať; po dlhom behu nie intervaly; po
intervaloch alebo kopcoch ľahký deň; objem najviac o 10–15 % za týždeň
(odporúčanie, označ ho tak). Zohľadni okolnosti z denníka.

Predpis ukáž v textovom tvare a hneď zapíš `save_plan` s dátumom, pre
ktorý platí; server formát overí a odmietne chybný.
