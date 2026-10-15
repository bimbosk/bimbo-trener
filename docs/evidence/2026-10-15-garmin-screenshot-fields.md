# 2026-10-15 — polia, ktoré Garmin Connect zobrazuje pre beh na páse

**Zdroj:** dva screenshoty z webu Garmin Connect (karta Štatistiky a graf Tempo + Srdcový
tep) jedného môjho behu na páse, bez dátumu. Slúži iba na určenie rozsahu polí pre
[dátový model](../coach/data-model.md); hodnoty sú prečítané zo screenshotu, nie z FIT
súboru.

## Karta Štatistiky

| Skupina | Polia a hodnoty v ukážke |
| --- | --- |
| Vzdialenosť | 5,90 km |
| Načasovanie | čas 41:36; čas jazdy (pohybu) 40:48; uplynutý čas 41:36 |
| Tempo / rýchlosť | priemerné tempo 7:03 /km; priemerné tempo pohybu 6:55 /km; najlepšie tempo 5:18 /km |
| Srdcový tep | priemer 117; maximum 131 (prepínač údery/min, % z max., zóny) |
| Účinok tréningu | Základ (mierne aeróbne); aeróbny 2,3 udržiavanie; anaeróbny 0,0 žiaden prínos; záťaž cvičenia 30 |
| Výkon | priemer 305 W; maximum 436 W; údaje o vetre vypnuté |
| Dynamika behu | kadencia priemer 156 / max 165 krokov/min; dĺžka kroku 0,92 m; vertikálny pomer 9,3 %; zvislá oscilácia 8,6 cm; doba kontaktu so zemou 300 ms |
| Rozpoznanie behu/chôdze | čas behu 41:16; čas chôdze 0:03; čas nečinnosti 0:17 |
| Výživa a hydratácia | pokojové kalórie 62; aktívne 306; celkom 368; odhad potu 693 ml; prijaté tekutiny –; výsledné množstvo –693 ml |
| Minúty intenzívneho cvičenia | mierna 24 min; vysoká 17 min (×2); celkovo 58 min |
| Body Battery | čistý vplyv –7 |

## Graf Tempo + Srdcový tep

Trvanie asi 41 min. Tempo stabilne okolo 7:30 /km (zodpovedá 8 km/h). Tep stúpa postupne
zo ~105 na ~128. Tri krátke prerušenia tempa okolo 9:30, 14:40 a 27:40 (pravdepodobne zmeny
rýchlosti alebo zastavenia). Prvé dve minúty: rozbeh a krátky skok tepu na ~130, zrejme
artefakt senzora. Tento priebeh sa zo screenshotu nedá zapísať číselne, iba slovne; číselný
priebeh dáva FIT súbor.

## Čo z toho plynie

- Garmin dáva výrazne viac polí, než obsahuje môj text z 29. 8.; dátový model má mať
  všetky, s prázdnou hodnotou, keď chýbajú.
- Tri rôzne časy (celkový, pohybu, uplynutý) a tri tempá sa musia rozlišovať; pre
  porovnanie s predpisom je kľúčový čas pohybu.
- Screenshot neobsahuje dátum, predpis ani pocit; tie dodám ja alebo import.
- FIT súbor obsahuje kolá a sekundové záznamy, z ktorých sa zóny aj úseky dajú vypočítať.
- Porovnanie s 10 km behom z augusta (116 tepov pri 7:47 /km vs. 117 pri 7:03 /km) naznačuje
  lepšie tempo pri rovnakom tepe, ale bez dátumu a podmienok je to iba náznak.
