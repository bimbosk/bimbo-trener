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

Otvor session agenta v tomto adresári a píš bežnou rečou, napríklad
„zapíš dnešný beh…“ alebo „vyhodnoť posledný týždeň“. Bežná práca nepotrebuje
žiadny režim ani prepínač.

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
