# Rozhodnutia — register

Jediné miesto, kde sú evidované moje rozhodnutia o projekte. Ostatné stránky na ne
odkazujú, neopakujú ich. Rozhodnutie platí, kým ho nezmením; zmena sa zapíše ako nové
rozhodnutie s dátumom. Podstatné rozhodnutia majú vlastný záznam s dôvodom a dôsledkami.

Stav: **platí** · **otvorené** (zatiaľ nerozhodnuté).

## Register

| Dátum | Rozhodnutie | Kde platí | Stav | Záznam |
| --- | --- | --- | --- | --- |
| 15. 10. 2026 | Tréner mi dáva **AI asistenta a trvalú pamäť**; neduplikuje Garmin Connect. Webová stránka s prehľadom behov sa nerobí; GUI nie je potrebné. | [Účel](../project/purpose.md) | platí | [záznam](2026-10-15-no-gui-no-web.md) |
| 15. 10. 2026 | Celý tréner beží na **Windows**: repozitár + susedná app, uv a spravovaný Python bez globálnych zmien, `install.cmd`, návod bežnou rečou. | [Aplikácia](../application/README.md) | platí | — |
| 15. 10. 2026 | Workflow: beh → hodinky → Garmin Connect → skript na PC stiahne nové FIT → import do databázy → asistent napojený na databázu. Spúšťanie **na klik a cez plánovanú úlohu** raz denne, ten istý skript. | [Sťahovanie](../coach/garmin-sync.md) | platí | [záznam](2026-10-15-own-sync-script.md) |
| 15. 10. 2026 | **FIT súbor je zdroj pravdy** pre namerané dáta; parsuje sa oficiálnym Garmin FIT SDK; screenshoty sú iba kontrola. | [Import FIT](../coach/fit-import.md) | platí | [záznam](2026-10-15-fit-source-of-truth.md) |
| 15. 10. 2026 | **Vlastný sťahovač nad garminconnect**, nie GarminDB; ručný export z webu ostáva zálohou; hromadný export účtu na históriu. | [Sťahovanie](../coach/garmin-sync.md) | platí | [záznam](2026-10-15-own-sync-script.md) |
| 15. 10. 2026 | **Jeden zdieľaný dátový adresár**, ktorý si vyberiem v nastaveniach; leží na lokálnom SSD a sync nástroj ho roznáša na všetky moje počítače. Lokálne nastavenia (cesta, token Garminu) ostávajú na každom PC. | [Dátový adresár](../coach/data-directory.md) | platí | [záznam](2026-10-15-synced-data-directory.md) |
| 15. 10. 2026 | **SQLite je jediný vlastník** všetkých zapisovaných dát vrátane denníka, stavu a plánu; Markdown iba ako generovaný náhľad. Bez vektorovej databázy. | [Dátový model](../coach/data-model.md) | platí | [záznam](2026-10-15-sqlite-single-owner.md) |
| 15. 10. 2026 | Predpis a závery rozhovoru sa zapisujú **rovno do databázy**, nie cez medzisúbory; každý záznam má dátum udalosti a čas zápisu. | [Pamäť a denník](../coach/memory-and-journal.md) | platí | [záznam](2026-10-15-sqlite-single-owner.md) |
| 15. 10. 2026 | **Záloha zviazaná so sťahovaním:** `sync.cmd` zistí z `meta.last_sync`, či pribudli nové dáta; ak áno, pred zápisom urobí komprimovanú zálohu do `backups\` v dátovom adresári a drží posledných 5; ak nie, nerobí nič. Živá databáza má pevný názov. Zápisy trénera sa navyše pridávajú do `journal-export.jsonl`. | [Zálohy](../coach/backups.md) | platí | — |
| 15. 10. 2026 | **Pamäť mimo okna rozhovoru**: skill „načítaj kontext“ na začiatku, skill „ulož dohodnuté“ na konci, priebežný zápis predpisu a pocitu; vrstvy stav → zhrnutia → záznamy držia načítaný kontext konštantný. | [Pamäť a denník](../coach/memory-and-journal.md) | platí | [záznam](2026-10-15-memory-outside-session.md) |
| 15. 10. 2026 | Asistenti (Claude Code aj Codex) sa k databáze pripájajú cez **MCP server** projektu; čítanie voľne, zápis so schválením. | [Rozhrania](../coach/interfaces.md) | platí | — |
| 15. 10. 2026 | Verzie: **Python 3.14, garminconnect 0.3.18, curl_cffi 0.16.3, garmin-fit-sdk 21.218.0**, pripnuté. | [Externé nástroje](../application/external-tools.md) | platí | [dôkaz](../evidence/2026-10-15-version-check.md) |
| 15. 10. 2026 | Token Garminu ostáva v lokálnom configu každého PC, nesynchronizuje sa; prihlásenie raz na každom PC, kde sa sťahuje. | [Garmin Connect](../integrations/garmin-connect.md) | platí | — |
| 15. 10. 2026 | **Zbierať všetko, čo Garmin dáva**: všetky aktivity s FIT a denné zdravotné dáta z Venu 4 a Index S2, so surovým JSON; čo je užitočné, sa zistí priebežne. | [Dátový model](../coach/data-model.md) | platí | [záznam](2026-10-15-collect-everything.md) |
| 15. 10. 2026 | **Citlivé dáta iba v externej databáze.** Repozitár je súkromný, napriek tomu neobsahuje žiadne namerané hodnoty, FIT súbory ani exporty; podklady ležia v priečinku `beh/`, ktorý Git ignoruje. | [Dokumentácia](../project/documentation.md) | platí | — |
| 15. 10. 2026 | **Sťahuje sa iba originál FIT**; TCX, GPX a CSV exporty nič nepridávajú. Dátový model zachytáva aj zóny, splity a snímku zón a prahov z FIT. | [Import FIT](../coach/fit-import.md) | platí | [dôkaz](../evidence/2026-10-15-fit-file-contents.md) |
| 15. 10. 2026 | **Sťahovanie spúšťa `sync.cmd`** v koreni repozitára; skratka na ploche, skill „stiahni dáta“ v `.rulesync` aj plánovaná úloha volajú ten istý súbor. | [Sťahovanie](../coach/garmin-sync.md) | platí | — |
| 15. 10. 2026 | **Konfigurácia v `bimbo-trener.json` v koreni repozitára** (JSON, commitnutý): cesta aplikácie, dátový adresár, databáza, zálohy, sťahovanie. Miestny prepis `bimbo-trener.local.json` mimo Gitu pre odlišnú cestu a zapnuté sťahovanie. | [Dátový adresár](../coach/data-directory.md) | platí | — |
| 15. 10. 2026 | Závislosť **tomlkit** navyše: inštalátor upravuje `config.toml` Codexu so zachovaním cudzích položiek a komentárov; `tomllib` iba číta. | [Externé nástroje](../application/external-tools.md) | platí | — |
| 15. 10. 2026 | Dokumentácia v `docs/` je členená na oblasti s rozcestníkmi; každá informácia má jedného vlastníka; píše sa v prvej osobe bez histórie rozhodovania. | [Dokumentácia](../project/documentation.md) | platí | — |

## Otvorené rozhodnutia

| # | Otázka | Súvislosť | Kam patrí odpoveď |
| --- | --- | --- | --- |
| O1 | ~~Model hodiniek~~ — uzavreté 15. 10. 2026: Venu 4, 45 mm; váha Index S2; cyklopočítač Edge 1040 ([zariadenia](../evidence/2026-10-15-devices-and-health-data.md)). | — | [Bežec a cieľ](../running/runner-and-goal.md) |
| O2 | ~~Štyri behy z textu z 29. 8. 2026~~ — uzavreté 15. 10. 2026: nezapisujú sa; história príde ako FIT z Garmin Connect. | — | — |
| O3 | Ako konkrétne vyzerá plán a debata o tréningu (týždeň dopredu vs. ďalší beh, podoba rozhovoru) — preberie sa neskôr, po prvých dátach. | [Predpisy](../coach/prescriptions.md) | tamže |
| O4 | ~~Súkromnosť repozitára~~ — uzavreté 15. 10. 2026: repozitár je súkromný, ale citlivé dáta (behy, tep, hmotnosť) patria iba do externej databázy; dokumentácia ich neuvádza. | — | [Dokumentácia](../project/documentation.md) |
| O5 | ~~Python cez uv alebo winget~~ — uzavreté 15. 10. 2026: uv a spravovaný Python v priečinku aplikácie, identicky ako v `projektant-tzb`. | — | [Externé nástroje](../application/external-tools.md) |
| O6 | ~~Prepis rozhovoru~~ — uzavreté 15. 10. 2026: ukladajú sa iba závery mechanizmom „ulož dohodnuté“. | — | [Pamäť a denník](../coach/memory-and-journal.md) |
