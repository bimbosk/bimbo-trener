# Bimbo tréner

Súkromný bežecký tréner, ktorý celý obsluhujú agenti (Claude Code, Codex).
Ukladá moje behy, analyzuje ich a pomáha s plánovaním tréningu. Nejde o
softvérový projekt. Kód (napr. SQLite databáza alebo Python skripty) pribudne
iba vtedy, keď ho ukladanie alebo analýza behov reálne potrebuje.

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
