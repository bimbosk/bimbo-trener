# Dokumentácia projektu

Ako je `docs/` usporiadaná a podľa akých pravidiel sa udržiava. Postup údržby vlastní
skill `maintain-project-documentation`; táto stránka vlastní štruktúru.

## Oblasti

| Oblasť | Otázka, na ktorú odpovedá |
| --- | --- |
| [`project/`](README.md) | Prečo projekt je, role, stav, dokumentácia. |
| [`running/`](../running/README.md) | Ako behám: pás, konvencie, formát predpisu, hodnotenie. |
| [`usage/`](../usage/README.md) | Ako trénera používam (návody bežnou rečou). |
| [`application/`](../application/README.md) | Čo sa inštaluje na Windows: členenie, inštalácia, aktualizácia, externé nástroje. |
| [`coach/`](../coach/README.md) | Špecifikácia trénera: dáta, sťahovanie, import, pamäť, predpisy, rozhrania, stav. |
| [`integrations/`](../integrations/README.md) | Garmin Connect, Claude Code, Codex. |
| [`decisions/`](../decisions/README.md) | Register mojich rozhodnutí a záznamy s dôvodom a dôsledkami. |
| [`evidence/`](../evidence/README.md) | Záznamy prieskumu, overení a meraní — čo sa zistilo, kedy a kde sú zdroje. |

Vstupom je [`DOCUMENTATION_MAP.md`](../DOCUMENTATION_MAP.md): tabuľka téma → jediný
rozhodujúci zdroj. Každá oblasť má `README.md` ako rozcestník s jednou vetou na stránku.
Agent číta mapu → rozcestník → jednu stránku; nečíta celú dokumentáciu.

## Typy stránok

| Typ | Čo obsahuje | Kde býva |
| --- | --- | --- |
| konvencia | čo platí v mojom behaní | `running/` |
| špecifikácia | čo má vzniknúť, MUSÍ/NESMIE, aj implementované správanie | `coach/`, `application/` |
| návod | ako niečo urobiť, krok za krokom | `usage/`, `application/`, `integrations/` |
| stav | kde to dnes je, s dátumom | `project/status.md`, `coach/implementation-status.md` |
| rozhodnutie | čo platí, prečo a s akými dôsledkami | `decisions/` |
| dôkaz | záznam prieskumu, overenia alebo merania; čísla, zdroje | `evidence/` |
| rozcestník | iba navigácia | `README.md` každej oblasti, mapa |

Jedna stránka má jeden typ a jeden logický celok. Čísla z meraní patria do dôkazov, na
ktoré špecifikácia odkazuje. História toho, ako sa k rozhodnutiu dospelo, sa nezapisuje;
zapisuje sa iba platný stav a jeho dôvod.

## Pravidlá

- **Jeden vlastník.** Každý fakt, číslo a rozhodnutie je zapísané na jednom mieste;
  ostatné stránky odkazujú. Pri rozpore sa opraví zdroj, nie kópia.
- **Žiadne monolity.** Nová téma dostane vlastnú stránku v príslušnej oblasti; stránka sa
  rozdelí, keď mieša typy alebo celky, nie kvôli dĺžke.
- **Odkazy namiesto opakovania.** Rozcestník a mapa obsahujú jednu vetu na zdroj.
- **Záväznosť.** Rozhodnutia v `decisions/` a MUSÍ/NESMIE v `coach/` sú záväzné. Pokyny
  agentov v `.rulesync/` sú chránené.
- **Súkromie.** Namerané behy, tep, FIT súbory, prihlasovacie tokeny a prepisy rozhovorov
  patria do dátového adresára, nie do Gitu. Dokumentácia smie uvádzať iba súhrnné čísla,
  ktoré som do nej sám dal ([východiskový stav](../evidence/2026-08-29-baseline.md)).
- **Názvoslovie.** Adresáre a súbory po anglicky, malými písmenami, slová spojené pomlčkou
  (`CLAUDE.md`, Jazyk); obsah po slovensky, v prvej osobe. Záznamy rozhodnutí a dôkazov
  začínajú dátumom `RRRR-MM-DD`.
- **Zmena štruktúry** sa robí spolu s úpravou mapy a rozcestníka oblasti a s kontrolou
  odkazov.

## Vzťah k ostatným zdrojom

Koreňové `README.md` je vstup pre človeka. Pokyny agentov (`CLAUDE.md`, `AGENTS.md`,
skilly) sú generované z `.rulesync/` a na dokumentáciu odkazujú cez mapu. Moje dáta
a denník nie sú dokumentácia; žijú v dátovom adresári
([dátový adresár](../coach/data-directory.md)).
