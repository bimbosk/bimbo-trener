# Role

| Rola | Kto | Čo robí a rozhoduje |
| --- | --- | --- |
| **Ja** | bežec a vlastník repozitára | Behám, synchronizujem hodinky do Garmin Connect, spúšťam sťahovanie dát, rozprávam sa s trénerom bežnou rečou, zadávam pocit a okolnosti. Rozhodujem o svojom tréningu aj o projekte: architektúra, dáta, inštrukcie agentov, dokumentácia. Moje rozhodnutia sú v [registri](../decisions/README.md). |
| **Tréner** | Claude Code alebo Codex otvorený v repozitári | Číta a zapisuje moju pamäť v dátovom adresári cez rozhrania projektu, navrhuje predpisy a plány, vyhodnocuje behy. Riadi sa `CLAUDE.md`/`AGENTS.md` a skillmi z `.rulesync/`. |

## Hranice

- Tréner nikdy nemení ani nemaže namerané dáta bez mojej žiadosti a nikdy nedopĺňa
  chýbajúce hodnoty odhadom.
- Tréner rozlišuje, čo je namerané, odvodené, odhad a všeobecné odporúčanie, a hovorí to
  v odpovedi ([hodnotenie tréningov](../running/evaluation.md)).
- Môj pocit má prednosť pred číslami: „na hrane“ znamená nepridávať, nech čísla hovoria
  čokoľvek.
- Zdravotné dáta patria do dátového adresára, nikdy do Gitu
  ([dokumentácia](documentation.md), Súkromie).
