# Externé nástroje a vonkajšie stopy

Zásada: závislosti sa neinštalujú globálne; existujúce aplikácie (Claude Code,
ChatGPT/Codex, sync nástroj, Git) sa nepresúvajú ani neodinštalujú. Verzie sú pripnuté
a menia sa vedome ([aktualizácia](update-and-uninstall.md)); prečo práve tieto, dokladá
[overenie verzií](../evidence/2026-10-15-version-check.md).

## Nástroje pod koreňom aplikácie

| Nástroj | Verzia | Umiestnenie a spôsob |
| --- | --- | --- |
| uv | pripnutá verzia v čase implementácie | `runtime\bin` cez `UV_UNMANAGED_INSTALL`, bez úprav PATH |
| Python | 3.14.x (spravovaný uv) | `runtime\python`; neregistruje sa vo Windows |
| garminconnect | 0.3.18 | `runtime\venv`; prihlásenie a sťahovanie FIT |
| curl_cffi | 0.16.3 | `runtime\venv`; TLS odtlačok prehliadača pre prihlásenie; wheel `cp310-abi3-win_amd64` |
| garmin-fit-sdk | 21.218.0 | `runtime\venv`; parsovanie FIT; čistý Python |
| mcp | 2.3.0 | `runtime\venv`; MCP server (API `mcp.server.mcpserver.MCPServer`) |
| tomlkit | 0.13.3 | `runtime\venv`; úprava `config.toml` Codexu so zachovaním cudzích položiek |

Zámok `scripts/requirements.lock` s hashmi (37 balíkov vrátane tranzitívnych), generovaný
`scripts/tools/make_lock.py` zo stiahnutých wheelov pre `win_amd64`/CPython 3.14; inštalácia
`uv pip install --require-hashes --no-deps -r scripts/requirements.lock`.

## Vonkajšie vedľajšie účinky

| Miesto | Čo zapisujeme | Obnova |
| --- | --- | --- |
| `%USERPROFILE%\.codex\config.toml` (alebo `CODEX_HOME`) | MCP položka `bimbo_trener` | záloha v `sprava\zalohy`; odinštalovanie obnoví |
| konfigurácia Claude Code (`claude mcp add --scope user`) | MCP server `bimbo_trener` | `claude mcp remove` pri odinštalovaní |
| plocha | skratka „Stiahni dáta z Garminu“ | odstránená podľa evidencie |
| Plánovač úloh | `BimboTrener-Sync` iba po komponente `sync` | odstránená pri odinštalovaní |
| `<app>\config\garmin` | token Garminu | zmazať alebo odvolať prístup v účte |

Dátový adresár nie je vedľajší účinok aplikácie; sú to moje dáta mimo nej.
