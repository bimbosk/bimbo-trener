# Asistenti: Claude Code a Codex

Tréner je ktorýkoľvek z dvoch asistentov otvorený v repozitári `bimbo-trener`. Obaja čítajú
tie isté pokyny generované z `.rulesync/` (Claude `CLAUDE.md` a `.claude/skills/`, Codex
`AGENTS.md` a `.agents/skills/`) a k dátam pristupujú cez ten istý MCP server
([rozhrania](../coach/interfaces.md)).

## Napojenie na databázu

| Asistent | Registrácia MCP | Kto ju robí |
| --- | --- | --- |
| Codex (aplikácia ChatGPT, Windows native) | položka `bimbo_trener` v `config.toml` (STDIO: python z venv, `server.py`, `--data-dir`), so zálohou | inštalátor, komponent `coach` |
| Claude Code | `claude mcp add --scope user bimbo_trener <python> <server.py> --data-dir <cesta>` | inštalátor, komponent `coach` |

Po registrácii alebo zmene treba asistenta zatvoriť a znova otvoriť. Nástroje na čítanie
majú `readOnlyHint` a nevyžadujú schválenie; zápisy áno.

Claude Code vie databázu čítať aj priamo cez Python, lebo má repozitár otvorený; MCP je
napriek tomu jediná podporovaná cesta, aby obaja asistenti videli to isté a aby zápis šiel
vždy cez zálohu.

## Správanie trénera (spoločné)

- Rozhovor o tréningu začína skillom „načítaj kontext“ a končí skillom „ulož dohodnuté“
  ([pamäť](../coach/memory-and-journal.md)).
- Predpis dodrží môj formát; pocit má prednosť pred číslami
  ([Beh](../running/README.md)).
- Každé tvrdenie označí ako namerané, odvodené, odhad alebo odporúčanie.
- Nič nevymýšľa, nemaže ani neopravuje bez žiadosti; dáta neposiela von.
- Na počítači bez Garmin prihlásenia funguje rovnako okrem sťahovania.

## Vývoj projektu

Repozitár vyvíjam prevažne cez Claude Code na Linuxe; inštalácia a prevádzka sú na Windows.
Zmeny pokynov agentov iba cez `maintain-agent-governance` na môj pokyn
(`CLAUDE.md`).
