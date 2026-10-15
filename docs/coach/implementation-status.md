# Stav implementácie

**K 15. 10. 2026 je implementovaný kód etáp E0–E6 na Linuxe; nič ešte nebežalo na Windowse.** Testy
(pytest, 36) prechádzajú na Linuxe so syntetickými FIT súbormi; inštalátor, `sync.cmd`, plánovaná úloha,
registrácia v Codexe a Claude Code a skutočné prihlásenie do Garminu čakajú na prvé kolo vo VM.

## Etapy

Podrobné zadanie každej etapy vlastní [implementačný plán](../../IMPLEMENTATION_PLAN.md);
táto stránka drží stav.

| Etapa | Obsah | Kritérium prijatia | Stav |
| --- | --- | --- | --- |
| E0 | schéma `db.py`, `init`/`attach`, záloha pri nových dátach, export denníka | testy na dočasnej databáze | hotové na Linuxe |
| E1 | `fit_import.py` nad FIT súborom | syntetické FIT v testoch prechádzajú; porovnanie so skutočným behom a Garmin Connect čaká na VM | kód hotový; overenie na reálnom FIT otvorené |
| E2 | pamäť, CLI, `render`, `rebuild`, analýzy | denný tok cez CLI v teste; `rebuild` vráti vlastné dáta | hotové na Linuxe |
| E3 | MCP server `bimbo_trener` (mcp 2.x) | handshake cez stdio a round-trip zápis/čítanie v testoch | hotové na Linuxe; registrácia v asistentoch neoverená |
| E4 | skilly `coach-session`, `prescribe-workout`, `evaluate-run`, `sync-garmin-data` a pravidlo Tréner v `.rulesync/` s projekciami | nový rozhovor začne načítaním, skončí zápisom | zapísané; správanie v novej session neoverené |
| E5 | `garmin_sync.py`, `sync.cmd`, `scripts\sync.ps1`, `task.py` | s falošným klientom v testoch: stiahnutie, import, denné dáta, 429 → 75 + cooldown, bez tokenov → 77 | kód hotový; skutočný Garmin a Windows neoverené |
| E6 | `install.cmd`, `scripts\setup.ps1`, `common\setup.ps1`, `coach\setup.ps1`, `lifecycle.py`, `coach\setup.py`, `requirements.lock` s hashmi | čistý Windows → funkčná app jedným `install.cmd` | napísané; nespustené |
| E7 | prvý týždeň reálnej prevádzky; dôkaz | týždeň prevádzky bez ručného zásahu | nezačaté |

## Čo treba overiť vo VM (ešte neprebehlo)

1. `HOW_TO_USE.md` blok na čistom Windows 11.
2. `install.cmd`: uv, Python 3.14, venv zo zámku, dialóg dátového adresára, skúšky CLI a MCP, skratka, registrácia v Codexe (`config.toml`) a Claude Code (`claude mcp add`).
3. `install.cmd -Component sync`: prihlásenie s MFA, zapnutie `garmin_sync_enabled`, plánovaná úloha.
4. `sync.cmd`: okno s priebehom, HOTOVO a zavretie po 3 s; druhé spustenie „nič nové“; kódy 75/77.
5. Import skutočného FIT z Venu 4 a porovnanie s Garmin Connect (dôkaz bez hodnôt).
6. Nová session Claude Code / Codex: skill `coach-session` načíta kontext a zapíše pocit.
7. `uninstall.cmd` a `-Action reset-runtime`.

Poradie dáva prednosť pamäti pred automatickým sťahovaním: ručný export FIT stačí na E1–E4.

## Známe otvorené body

Viď [otvorené rozhodnutia](../decisions/README.md#otvorené-rozhodnutia) a
[backlog](backlog.md).
