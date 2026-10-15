# Mapa dokumentácie

Začni pri najužšom vlastníkovi relevantnom pre úlohu a hlbšie odkazy otváraj iba podľa
potreby: mapa → rozcestník oblasti → jedna stránka. Dokumentáciu nečítaj rekurzívne celú.
Záznam pridaj v tej istej zmene, ktorá vytvára, presúva alebo ruší trvalého vlastníka;
uvádzaj iba existujúcich vlastníkov. Členenie a pravidlá vlastní
[Dokumentácia](project/documentation.md).

## Oblasti

| Oblasť | Rozcestník |
| --- | --- |
| Prečo projekt je, role, stav, dokumentácia | [Projekt](project/README.md) |
| Ako behám (konvencie) | [Beh](running/README.md) |
| Návody bežnou rečou | [Používanie](usage/README.md) |
| Lokálna aplikácia a inštalátor na Windows | [Aplikácia](application/README.md) |
| Tréner: dáta, sťahovanie, import, pamäť, predpisy, rozhrania | [Tréner](coach/README.md) |
| Garmin Connect, Claude Code, Codex | [Integrácie](integrations/README.md) |
| Moje rozhodnutia | [Rozhodnutia](decisions/README.md) |
| Záznamy prieskumu, overení a meraní | [Dôkazy](evidence/README.md) |

## Témy

| Potreba | Kanonický vlastník |
| --- | --- |
| Účel, používanie a pôvod repozitára (pre človeka) | [`README.md`](../README.md) |
| Etapy E0–E7, moduly, kritériá prijatia (plán implementácie) | [`IMPLEMENTATION_PLAN.md`](../IMPLEMENTATION_PLAN.md) |
| Stiahnutie repozitára na nový Windows (PowerShell blok) | [`HOW_TO_USE.md`](../HOW_TO_USE.md) |
| Pravidlá a skilly agentov | [`.rulesync/`](../.rulesync/) |
| Ručné pregenerovanie výstupov pre agentov | [`maintain-agent-governance`](../.rulesync/skills/maintain-agent-governance/SKILL.md) |
| Čo tréner robí, nerobí a ponúka navyše oproti Garminu | [Účel a rozsah](project/purpose.md) |
| Role: ja a asistenti | [Role](project/roles.md) |
| Aktuálny stav projektu a najbližšie kroky (stav) | [Stav projektu](project/status.md) |
| Kto behá, kde, cieľ polmaratón a maratón | [Bežec a cieľ](running/runner-and-goal.md) |
| Rýchlosti, 1 % sklonu = 0,4 km/h, 6 km/h nie je beh, záhrada, horúčavy | [Pás a konvencie](running/treadmill-conventions.md) |
| Presne 10 úsekov, riadok úsek–čas–rýchlosť–sklon, typy tréningov | [Formát predpisu](running/workout-format.md) |
| Čo sa po behu sleduje, prednosť pocitu, namerané/odvodené/odhad | [Hodnotenie tréningov](running/evaluation.md) |
| Nový počítač krok za krokom (návrh) | [Nový počítač](usage/new-computer.md) |
| Beh → skratka → rozhovor → predpis; keď skratka nefunguje | [Bežný deň](usage/daily-flow.md) |
| Čo trénerovi povedať a čo čakať | [Ako sa pýtať trénera](usage/asking-the-coach.md) |
| Dva susedné adresáre, `runtime/config/logs/sprava`, komponenty | [Členenie](application/layout.md) |
| `install.cmd`: predpoklady, poradie, výstupy, kódy | [Inštalácia](application/installation.md) |
| Aktualizácia, `reset-runtime`, odinštalovanie, iný počítač | [Aktualizácia a odinštalovanie](application/update-and-uninstall.md) |
| uv, Python, pripnuté balíky, MCP registrácie, skratka, plánovaná úloha | [Externé nástroje](application/external-tools.md) |
| Produkt jednou vetou, príklady rozhovorov, MUSÍ/NESMIE | [Cieľ a požiadavky](coach/goal-and-requirements.md) |
| Tok dát, vrstvy nad SQLite, čo beží kde | [Architektúra](coach/architecture.md) |
| Zdieľaný dátový adresár, marker, `init`/`attach`, konfigurácia `bimbo-trener.json`, sync | [Dátový adresár](coach/data-directory.md) |
| Tabuľky SQLite, životnosť, fulltext | [Dátový model](coach/data-model.md) |
| Skript sťahovania, cooldown, kódy, skratka a plánovaná úloha, záložné cesty | [Sťahovanie z Garminu](coach/garmin-sync.md) |
| FIT → tabuľky cez FIT SDK, párovanie s predpisom | [Import FIT](coach/fit-import.md) |
| Záloha zviazaná so sťahovaním, posledných 5, export denníka, obnova | [Zálohy](coach/backups.md) |
| Vrstvy pamäte, čo sa zapisuje kedy, rozpočet kontextu, skill „ulož dohodnuté“ | [Pamäť a denník](coach/memory-and-journal.md) |
| Výber ďalšieho predpisu, rotácia, progresia, porovnanie s realitou, dlhodobý plán | [Predpisy](coach/prescriptions.md) |
| Tempo pri tepe, drift, ekvivalentná rýchlosť, reporty, varovania | [Analýzy](coach/analyses.md) |
| CLI príkazy, MCP nástroje a anotácie, skilly | [Rozhrania](coach/interfaces.md) |
| Token, hranice ciest, čo MCP nesmie, Git | [Bezpečnosť](coach/security.md) |
| Etapy E0–E7 a čo je hotové (stav) | [Stav implementácie](coach/implementation-status.md) |
| Možnosti navyše B1–B12 a kedy ich zaradiť | [Backlog](coach/backlog.md) |
| Účet Garmin, prihlásenie knižnicou, limity 429/403, podmienky | [Garmin Connect](integrations/garmin-connect.md) |
| Registrácia MCP v Codexe a Claude Code, spoločné správanie trénera | [Asistenti](integrations/assistants.md) |
| Register rozhodnutí a otvorené rozhodnutia O1–O6 | [Rozhodnutia](decisions/README.md) |
| Môj text z 29. 8. 2026 (čo dokladá) | [Východiskový stav](evidence/2026-08-29-baseline.md) |
| Štruktúra FIT z Venu 4, porovnanie exportov | [Obsah FIT súboru](evidence/2026-10-15-fit-file-contents.md) |
| Úplný zoznam polí FIT a stĺpcov exportov | [Inventár polí FIT](evidence/2026-10-15-fit-field-inventory.md) |
| Polia Garmin Connect pre beh na páse | [Polia Garmin Connect](evidence/2026-10-15-garmin-screenshot-fields.md) |
| Štyri cesty FIT do počítača, API, riziká, zdroje | [Prieskum Garmin](evidence/2026-10-15-garmin-research.md) |
| Venu 4, Index S2, Edge 1040: čo zapisujú, volania knižnice | [Zariadenia a zdravotné dáta](evidence/2026-10-15-devices-and-health-data.md) |
| Aktuálne verzie a odporúčaná kombinácia | [Overenie verzií](evidence/2026-10-15-version-check.md) |
