# Účel a rozsah

## Čo projekt je

Bimbo tréner je môj osobný bežecký tréner, ktorého celý obsluhujú AI asistenti. Behám
takmer každý deň, prevažne na bežiacom páse doma, a pripravujem sa na polmaratón 21,1 km
a neskôr maratón ([bežec a cieľ](../running/runner-and-goal.md)).

Dáva mi dve veci, ktoré Garmin Connect nemá:

1. **AI asistenta ako kouča**, ktorý pozná môj pás, môj formát predpisov, moje pocity
   a okolnosti a vie navrhnúť ďalší tréning aj dlhodobý plán.
2. **Trvalú pamäť**, ktorá prežije každé okno rozhovoru a je rovnaká na všetkých mojich
   počítačoch ([pamäť a denník](../coach/memory-and-journal.md)).

## Čo projekt nerobí

- **Neduplikuje Garmin Connect.** Grafy, mapy, kroky, spánok a Body Battery zobrazuje
  Garmin dobre; tréner ich nekreslí nanovo. Webová stránka ani GUI sa nerobia
  ([rozhodnutie](../decisions/2026-10-15-no-gui-no-web.md)).
- **Nevymýšľa dáta.** Hodnoty z hodiniek sa zapisujú tak, ako sú; chýbajúca hodnota je
  chýbajúca. Rozlišuje sa namerané, odvodené, odhad a všeobecné odporúčanie
  (`CLAUDE.md`, oddiel Dáta o behoch).
- **Neposiela dáta von.** Jedinou externou službou je Garmin Connect, ktorú už používam;
  zdravotné dáta neopúšťajú moje počítače ([bezpečnosť](../coach/security.md)).
- **Nenahrádza lekára ani licencovaného trénera.** Odporúčania sú všeobecné tréningové
  zásady aplikované na moje dáta; rozhodujem ja.

## Čo mi tréner dáva navyše

| Oblasť | Možnosť |
| --- | --- |
| Pamäť | rozhovory, pocity, okolnosti (horúčavy, práca v záhrade, bolesť) ako dáta; stav trénera a zhrnutia období |
| Predpisy | presne v mojom formáte pre pás; rotácia typov tréningov; porovnanie predpisu s realitou po úsekoch |
| Plán | fázy k polmaratónu a maratónu, míľniky odvodené z dát, prepočet po výpadku |
| Analýzy | tempo pri rovnakom tepe v čase, tepový drift v dlhých behoch, ekvivalentná rýchlosť so sklonom, mesačný report slovami |
| Prevencia | varovania pri zvýšenom tepe, skoku objemu alebo opakovanej bolesti; označenie zdroja každej rady |
| Praktické | predpis ako text na telefón, denník čitateľný pre mňa aj lekára, plán tempa na preteky |

Jadro je pamäť, predpisy v mojom formáte a porovnanie predpisu s realitou. Ostatné sa
zaraďuje podľa [backlogu](../coach/backlog.md).
