# Bimbo tréner

Súkromný bežecký tréner, ktorý celý obsluhujú agenti (Claude Code, Codex).
Ukladá moje behy, analyzuje ich a pomáha s plánovaním tréningu. Nejde o
softvérový projekt. Kód (napr. SQLite databáza alebo Python skripty) pribudne
iba vtedy, keď ho ukladanie alebo analýza behov reálne potrebuje.

## Nový počítač

Na novom Windows počítači začnem návodom
[HOW_TO_USE — stiahnutie projektu](HOW_TO_USE.md), potom `install.cmd`
([inštalácia](docs/application/installation.md)).

## Implementácia

Postup od špecifikácie ku kódu, pripravený pre session bez kontextu:
[implementačný plán](IMPLEMENTATION_PLAN.md).

## Dokumentácia

Čo má projekt byť a ako má fungovať, je zapísané v `docs/`: vstupom je
[mapa dokumentácie](docs/DOCUMENTATION_MAP.md) (téma → jediný vlastník), potom
rozcestník oblasti, potom jedna stránka. Stav projektu a najbližšie kroky:
[stav](docs/project/status.md); rozhodnutia vlastníka:
[register](docs/decisions/README.md).

## Ako s ním pracovať

Otvor session agenta v tomto adresári a píš bežnou rečou, napríklad „ako mi to
včera išlo“, „daj mi predpis“ alebo „ulož dohodnuté“. Tréner si kontext načíta
z databázy cez MCP server `bimbo_trener` (skill `coach-session`). Nové dáta
z Garmin Connect stiahne `sync.cmd` (alebo veta „stiahni dáta“).

## Čo je v repozitári

- `bimbo-trener.json` – konfigurácia (dátový adresár, zálohy, sťahovanie);
  `bimbo-trener.local.json` je miestny prepis mimo Gitu.
- `install.cmd`, `sync.cmd`, `uninstall.cmd` – spúšťače pre Windows.
- `scripts/coach/` – databáza, import FIT, sťahovanie, CLI, MCP server, testy
  (`pytest scripts/coach/tests`).
- `scripts/*.ps1`, `scripts/common/`, `scripts/coach/setup.ps1` – inštalátor
  podľa [aplikácie](docs/application/README.md).

## Inštrukcie pre agentov

- Zdroj pravdy: `.rulesync/` (pravidlá a skilly) a `rulesync.jsonc`.
- Vygenerované súbory `CLAUDE.md`, `AGENTS.md`, `.claude/skills/` a
  `.agents/skills/` sú commitnuté. Nikdy sa neupravujú priamo.
- Repozitár nemá npm ani iný nástroj Rulesync. Pri každej zmene inštrukcií
  agent upraví zdroj v `.rulesync/` a výstupy pregeneruje ručne podľa skillu
  `maintain-agent-governance`.
- Inštrukcie agentov sa menia iba na moju výslovnú žiadosť.

## Pôvod

Vychádza zo šablóny `erion-agents-golden-template` (revízia `6133c28`),
zjednodušenej pre repozitár, ktorý nie je určený na vývoj softvéru.
