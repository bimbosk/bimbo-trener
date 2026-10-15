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
| mcp | podľa zámku v čase implementácie | `runtime\venv`; MCP server |

Zámok `scripts/requirements.lock` s hashmi, generovaný pre `win_amd64`/cp314; inštalácia
`uv pip install --require-hashes`.

## Vonkajšie vedľajšie účinky

| Miesto | Čo zapisujeme | Obnova |
| --- | --- | --- |
| `%USERPROFILE%\.codex\config.toml` (alebo `CODEX_HOME`) | MCP položka `bimbo_trener` | záloha v `sprava\zalohy`; odinštalovanie obnoví |
| konfigurácia Claude Code (`claude mcp add --scope user`) | MCP server `bimbo_trener` | `claude mcp remove` pri odinštalovaní |
| plocha | skratka „Stiahni dáta z Garminu“ | odstránená podľa evidencie |
| Plánovač úloh | `BimboTrener-Sync` iba po komponente `sync` | odstránená pri odinštalovaní |
| `<app>\config\garmin` | token Garminu | zmazať alebo odvolať prístup v účte |

Dátový adresár nie je vedľajší účinok aplikácie; sú to moje dáta mimo nej.
