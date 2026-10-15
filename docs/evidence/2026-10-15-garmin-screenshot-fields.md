# 2026-10-15 — polia, ktoré Garmin Connect zobrazuje pre beh na páse

**Zdroj:** dva screenshoty z webu Garmin Connect (karta Štatistiky a graf Tempo + Srdcový
tep) jedného môjho behu na páse. Slúži iba na určenie rozsahu polí pre
[dátový model](../coach/data-model.md); hodnoty sa do dokumentácie nezapisujú.

## Karta Štatistiky

| Skupina | Polia |
| --- | --- |
| Vzdialenosť | vzdialenosť |
| Načasovanie | čas; čas jazdy (pohybu); uplynutý čas |
| Tempo / rýchlosť | priemerné tempo; priemerné tempo pohybu; najlepšie tempo |
| Srdcový tep | priemer; maximum (prepínač údery/min, % z max., zóny) |
| Účinok tréningu | hlavná výhoda (napr. Základ); aeróbny TE a prínos; anaeróbny TE a prínos; záťaž cvičenia |
| Výkon | priemer; maximum; údaje o vetre |
| Dynamika behu | kadencia priemer / max; dĺžka kroku; vertikálny pomer; zvislá oscilácia; doba kontaktu so zemou |
| Rozpoznanie behu/chôdze | čas behu; čas chôdze; čas nečinnosti |
| Výživa a hydratácia | pokojové, aktívne a celkové kalórie; odhad potu; prijaté tekutiny; výsledné množstvo |
| Minúty intenzívneho cvičenia | mierna; vysoká (×2); celkovo |
| Body Battery | čistý vplyv |

## Graf Tempo + Srdcový tep

Tempo a tep po sekundách; na páse je tempo takmer konštantné a tep postupne stúpa. Krátke
prerušenia tempa zodpovedajú zmenám rýchlosti alebo zastaveniam. Prvé minúty môžu mať
artefakt senzora. Zo screenshotu sa priebeh nedá zapísať číselne; číselný priebeh dáva FIT
súbor ([obsah FIT](2026-10-15-fit-file-contents.md)).

## Čo z toho plynie

- Garmin dáva výrazne viac polí, než obsahuje môj text z 29. 8.; dátový model má mať
  všetky, s prázdnou hodnotou, keď chýbajú.
- Tri rôzne časy (celkový, pohybu, uplynutý) a tri tempá sa musia rozlišovať; pre
  porovnanie s predpisom je kľúčový čas pohybu.
- Screenshot neobsahuje dátum, predpis ani pocit; tie dodám ja alebo import.
