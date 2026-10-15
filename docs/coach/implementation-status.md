# Stav implementácie

**K 15. 10. 2026 nie je implementované nič.** Existuje iba táto špecifikácia.

## Navrhované etapy

| Etapa | Obsah | Kritérium prijatia | Stav |
| --- | --- | --- | --- |
| E0 | schéma `db.py`, `init`/`attach`, záloha pred zápisom | testy na dočasnej databáze; záloha vznikne pred zápisom a rotuje | nezačaté |
| E1 | `fit_import.py` nad jedným FIT súborom exportovaným z webu | hodnoty `runs` sa zhodujú s Garmin Connect pre ten istý beh; dôkaz zapísaný | nezačaté |
| E2 | pamäť: `journal`, `summaries`, `coach_state`, `conventions`; CLI príkazy; `render` | zápis a čítanie cez CLI; náhľad v `preview\` | nezačaté |
| E3 | MCP server s nástrojmi na čítanie a zápis; registrácia v Claude Code | asistent načíta stav a zapíše pocit bez priameho SQL | nezačaté |
| E4 | skilly `load-coach-context`, `save-agreed`, `prescribe-workout` v `.rulesync/`  | nový rozhovor začne načítaním, skončí zápisom | nezačaté |
| E5 | `garmin_sync.py` s cooldownom a kódmi; skratka; plánovaná úloha | jeden klik stiahne nový beh a importuje ho; 429 skončí 75 bez opakovania | nezačaté |
| E6 | inštalátor pre Windows podľa [aplikácie](../application/README.md); registrácia MCP v Codexe | čistý Windows → funkčná app jedným `install.cmd` | nezačaté |
| E7 | prvý týždeň reálnej prevádzky; dôkaz | týždeň prevádzky bez ručného zásahu | nezačaté |

Poradie dáva prednosť pamäti pred automatickým sťahovaním: ručný export FIT stačí na E1–E4.

## Známe otvorené body

Viď [otvorené rozhodnutia](../decisions/README.md#otvorené-rozhodnutia) a
[backlog](backlog.md).
