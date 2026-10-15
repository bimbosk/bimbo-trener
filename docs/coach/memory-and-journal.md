# Pamäť a denník

Ako tréner drží kontext naprieč oknami, dňami a počítačmi
([rozhodnutie](../decisions/2026-10-15-memory-outside-session.md)). Tabuľky vlastní
[dátový model](data-model.md); skilly a nástroje [rozhrania](interfaces.md).

## Tri vrstvy pamäte

| Vrstva | Kde | Čo | Životnosť |
| --- | --- | --- | --- |
| pamäť projektu | repozitár (Git) | kód, pravidlá agentov, dokumentácia, rozhodnutia | verzovaná |
| moja pamäť | databáza v dátovom adresári | behy, predpisy, pocity, denník, zhrnutia, stav, plán | trvalá, synchronizovaná |
| okno rozhovoru | Claude Code / Codex | pracovná plocha | zmizne so zatvorením alebo naplnením |

Nič dôležité nesmie existovať iba v tretej vrstve.

## Čo sa zapisuje a kedy

| Udalosť | Zápis | Kedy |
| --- | --- | --- |
| poviem pocit | `feelings` + `journal(feeling)` | hneď |
| spomeniem okolnosť (bolesť, teplo, záhrada, spánok, výpadok) | `journal(circumstance)` | hneď |
| dohodne sa predpis | `plans` + `plan_segments` + `journal(decision)` | hneď |
| zmení sa plán alebo pravidlo a prečo | `journal(decision)`, `training_plan`, `conventions` | hneď |
| koniec rozhovoru | `journal(conversation_summary)` 3–10 viet; aktualizácia `coach_state` | skill „ulož dohodnuté“ |
| prvý rozhovor nového týždňa alebo nedeľa | `summaries(week)` | skill „ulož dohodnuté“ alebo na vyžiadanie |
| prvý rozhovor nového mesiaca | `summaries(month)` | to isté |

Priebežný zápis je poistka: ak okno zomrie uprostred, stratí sa najviac posledná veta.

## Čo sa načítava a koľko

Skill „načítaj kontext“ na začiatku každého rozhovoru o tréningu číta od najhrubšieho
k najjemnejšiemu a zastaví sa, keď je odpoveď jasná:

| Krok | Zdroj | Približne tokenov |
| --- | --- | --- |
| 1 | `coach_state` (1 strana) | 500–1 000 |
| 2 | posledné `summaries(week)` | 300 |
| 3 | `journal` za posledných 7 dní | 1 000–2 000 |
| 4 | posledné 2–3 `runs` ako súhrnné čísla | 300 |

Spolu rádovo 3 000 tokenov bez ohľadu na dĺžku histórie. Sekundové záznamy, staré rozhovory
a celé mesiace sa nečítajú, pokiaľ sa nepýtam výslovne; vtedy sa pridá príslušné
`summaries(month)` a fulltextom nájdené záznamy.

## Obsah `coach_state`

Jedna strana textu, prepisuje sa:

- kde som (fáza plánu, najdlhší beh, aktuálne pohodlné rýchlosti),
- čo je na rade (typ ďalšieho tréningu, najbližší míľnik),
- posledné rozhodnutia a ich dôvody (3–5 bodov),
- otvorené veci (bolesť, čo treba sledovať, otázky na mňa),
- dátum aktualizácie.

Je to automaticky udržiavaná obdoba môjho textu z 29. 8. 2026.

## Zhrnutia

Týždenné: počet behov, objem, najdlhší beh, typy, pocit, čo sa zmenilo, čo ďalej.
Mesačné: trend tempa pri rovnakom tepe, míľniky, rozhodnutia, výpadky a dôvody.
Nová verzia zhrnutia toho istého obdobia nahrádza staršiu; staršia ostáva v zálohe.

## Skill „ulož dohodnuté“

Spúšťam ho ja alebo tréner sám, keď rozhovor smeruje k záveru. Skill:

1. prejde rozhovor a vytiahne pocity, okolnosti, predpisy, rozhodnutia a zmeny plánu,
2. porovná s tým, čo už je zapísané priebežne, a doplní chýbajúce,
3. zapíše zhrnutie rozhovoru a aktualizuje `coach_state`,
4. ak je nový týždeň alebo mesiac, napíše zhrnutie obdobia,
5. ukáže mi, čo zapísal.

Závery, nie prepis. Prepis je otvorená otázka O6.

## Náhľad na čítanie

`render.py` generuje z databázy do `preview\` Markdown: `STAV.md`, `dennik\RRRR-MM.md`,
`zhrnutia\…`. Iba na čítanie; nikto doň nepíše; dá sa zmazať a vygenerovať znova.
