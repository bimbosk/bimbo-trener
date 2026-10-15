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
| 15. 10. 2026 | Predpis a závery rozhovoru sa zapisujú **rovno do databázy**, nie cez medzisúbory. | [Pamäť a denník](../coach/memory-and-journal.md) | platí | [záznam](2026-10-15-sqlite-single-owner.md) |
| 15. 10. 2026 | **Záloha databázy pred každým zápisom**, rotácia posledných 10, plus denná záloha držaná 30 dní a mesačná držaná rok; všetko v dátovom adresári. | [Zálohy](../coach/backups.md) | platí | — |
| 15. 10. 2026 | **Pamäť mimo okna rozhovoru**: skill „načítaj kontext“ na začiatku, skill „ulož dohodnuté“ na konci, priebežný zápis predpisu a pocitu; vrstvy stav → zhrnutia → záznamy držia načítaný kontext konštantný. | [Pamäť a denník](../coach/memory-and-journal.md) | platí | [záznam](2026-10-15-memory-outside-session.md) |
| 15. 10. 2026 | Asistenti (Claude Code aj Codex) sa k databáze pripájajú cez **MCP server** projektu; čítanie voľne, zápis so schválením. | [Rozhrania](../coach/interfaces.md) | platí | — |
| 15. 10. 2026 | Verzie: **Python 3.14, garminconnect 0.3.18, curl_cffi 0.16.3, garmin-fit-sdk 21.218.0**, pripnuté. | [Externé nástroje](../application/external-tools.md) | platí | [dôkaz](../evidence/2026-10-15-version-check.md) |
| 15. 10. 2026 | Token Garminu ostáva v lokálnom configu každého PC, nesynchronizuje sa; prihlásenie raz na každom PC, kde sa sťahuje. | [Garmin Connect](../integrations/garmin-connect.md) | platí | — |
| 15. 10. 2026 | Dokumentácia v `docs/` je členená na oblasti s rozcestníkmi; každá informácia má jedného vlastníka; píše sa v prvej osobe bez histórie rozhodovania. | [Dokumentácia](../project/documentation.md) | platí | — |

## Otvorené rozhodnutia

| # | Otázka | Súvislosť | Kam patrí odpoveď |
| --- | --- | --- | --- |
| O1 | Model mojich Garmin hodiniek (rozhoduje o kopírovaní cez USB a o poliach dynamiky behu). | [Sťahovanie](../coach/garmin-sync.md) | [Bežec a cieľ](../running/runner-and-goal.md) |
| O2 | Doplniť štyri behy z textu z 29. 8. 2026 (bez dátumov) do databázy, alebo začať až importom z Garmin Connect / hromadným exportom. | [Východiskový stav](../evidence/2026-08-29-baseline.md) | [Import FIT](../coach/fit-import.md) |
| O3 | Má tréner plánovať týždeň dopredu, alebo vždy iba ďalší beh podľa pocitu z posledného? | [Predpisy](../coach/prescriptions.md) | tamže |
| O4 | Je repozitár na GitHube súkromný? Rozhoduje, či smú byť v dokumentácii súhrnné zdravotné čísla. | [Dokumentácia](../project/documentation.md) | tamže |
| O5 | Má Python inštalovať inštalátor cez uv, alebo stačí winget? | [Inštalácia](../application/installation.md) | tamže |
| O6 | Má sa ukladať aj skrátený prepis rozhovoru, alebo iba závery? | [Pamäť a denník](../coach/memory-and-journal.md) | tamže |
