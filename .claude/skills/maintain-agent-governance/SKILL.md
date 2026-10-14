---
name: maintain-agent-governance
description: >-
  Povinný pri vytváraní, zmene, review, reorganizácii alebo odstraňovaní
  pravidiel, skillov či subagentov Rulesync alebo `rulesync.jsonc`. Preskoč
  bežnú prácu a rutinné používanie existujúcich inštrukcií.
---
# Údržba governance agentov

Tento skill použi vždy, keď na výslovnú žiadosť vlastníka meníš governance
agentov.

Skill neudeľuje oprávnenie. Jeho cieľom je spoľahlivé správanie agentov pri
najnižších opodstatnených opakovaných nákladoch na inštrukcie, kontext a
používanie.

## Vychádzaj z požadovaného správania

Pred vytvorením alebo zmenou inštrukcie urči:

1. Aké konkrétne správanie je požadované?
2. Vyžaduje inštrukciu?
3. Zavádza ho už existujúci vlastník?
4. Je univerzálne alebo situačné?
5. Kto je jeho najužší prirodzený vlastník?
6. Môže duplicitný obsah nahradiť odkaz?
7. Ktoré existujúce znenie sa stane nadbytočným?

Nepridávaj inštrukcie len preto, že informácia je užitočná, vysvetľujúca,
zvyčajná alebo by sa raz mohla hodiť.

## Jeden prirodzený vlastník

Každé normatívne správanie alebo postup má jedného kanonického vlastníka.

Ak je to možné, rozšír správneho existujúceho vlastníka. Ostatné miesta naň
majú odkazovať, odvodzovať z neho alebo z neho generovať, nie udržiavať
duplicitnú politiku.

Odstráň duplicitu, ktorú zmena urobila nadbytočnou.

## Najužšia postačujúca vrstva

- **Koreňové pravidlá:** správanie potrebné všade alebo ešte pred postupným
  odhaľovaním.
- **Ohraničené pravidlá:** opakujúce sa invarianty obmedzené na časť
  repozitára.
- **Skilly:** situačné postupy.
- **Dokumentácia:** trvalé detaily, zdôvodnenia, protokoly a návody.
- **Kód/konfigurácia:** presné spustiteľné správanie a strojovo vlastnené
  hodnoty.

Stále aktívne pravidlá majú najvyššie opakované náklady na kontext a vyžadujú
najsilnejšie odôvodnenie.

Uprednostni postupné odhaľovanie pred trvalým kontextom.

## Minimalizuj náklady na inštrukcie

Požadované správanie vyjadri čo najmenším počtom slov, ktoré zostanú jasné a
jednoznačné.

Uprednostni:

- priame požiadavky pred vysvetľovaním;
- jeden všeobecný invariant pred ekvivalentnými výpočtami;
- odkazy pred kopírovanými detailmi;
- existujúcu terminológiu a vlastníkov pred novými abstrakciami;
- postupné odhaľovanie pred univerzálnym kontextom.

Odstráň:

- duplicitnú alebo implicitnú politiku;
- nadbytočné vysvetlenia;
- zdôvodnenia či históriu, ktoré neovplyvňujú správanie;
- príklady, ktoré neriešia skutočnú nejednoznačnosť;
- implementačné detaily, ktoré vlastní niekto iný;
- špekulatívne budúce požiadavky.

Nevymenúvaj synonymá, dôsledky ani implikácie, ktoré už pokrýva širšia
jednoznačná inštrukcia.

Cieľom je **minimálna postačujúca inštrukcia**, nie minimálny možný text.
Nikdy neobetuj správnosť, oprávnenie, bezpečnosť, dohľadateľnosť ani
spoľahlivú aktiváciu kvôli stručnosti.

## Pred prijatím skracuj

Behaviorálne správny návrh nie je hotový.

Po napísaní akéhokoľvek pravidla alebo metadát skillu urob záverečné skrátenie.

Odstráň každú vetu, klauzulu, príklad, výpočet alebo spresnenie, ktorých
odstránenie podstatne neoslabí požadované správanie.

Uprednostni jednu širšiu jednoznačnú inštrukciu pred zoznamami ekvivalentných
alebo implicitných krokov.

Pri stále aktívnych pravidlách pokračuj, kým žiadna podstatne kratšia
formulácia nezachová rovnaké správanie, oprávnenie, bezpečnosť a
dohľadateľnosť.

## Navrhuj skilly na spoľahlivú aktiváciu

Popis skillu je smerovacie metadáta, nie zhrnutie jeho postupu.

Má byť len taký podrobný, aby spoľahlivo identifikoval zamýšľaný typ úloh.
Situačný postup drž v skille, nepresúvaj ho do koreňových pravidiel.

Samotný skill môže byť podrobný, ak to podstatne zlepší vykonanie, lebo jeho
plnú cenu platíš iba pri aktivácii.

## Vyhni sa špekulatívnej governance

Nevytváraj pravidlá, skilly, režimy, smerovanie, abstrakcie ani mechanizmy
kompatibility pre hypotetické budúce potreby.

Vyžaduj konkrétnu zodpovednosť, preukázaný problém, hranicu oprávnení alebo
podstatný prínos pre správanie.

## Pred zmenou zachovaj

Preskúmaj dosť existujúcej governance na pochopenie jej vlastníctva a
správania.

Zachovaj platné správanie a uprednostni najmenšiu súdržnú zmenu, ktorá rieši
požiadavku.

Platnú governance neprepisuj len preto, že je možné iné usporiadanie.

## Codex a Claude sú rovnocenné

Codex a Claude ber ako rovnocenné prvotriedne ciele.

Uprednostni prenositeľné kanonické inštrukcie. Správanie špecifické pre cieľ
pridaj iba pre overené rozdiely v schopnostiach, ktoré si ho vyžadujú.

## Upravuj iba kanonické zdroje

`.rulesync/` je kanonický zdroj inštrukcií.

Vygenerované výstupy pre Codex alebo Claude nikdy neupravuj priamo. Zmeny
inštrukcií rob v kanonických zdrojoch Rulesync a prenes ich generovaním.

## Ručné pregenerovanie a overenie

Repozitár nemá nástroje Rulesync. V tej istej zmene ako každú kanonickú zmenu
ručne pregeneruj dotknuté výstupy presne tak, ako by to urobil
`rulesync generate` s `rulesync.jsonc`, a commitni ich spolu so zdrojmi:

- **Koreňové pravidlá** (`root: true`): `CLAUDE.md` (cieľ `claudecode`) aj
  `AGENTS.md` (cieľ `codexcli`) sú telá koreňových pravidiel daného cieľa v
  poradí názvov súborov, každé bez frontmatteru a okolitých prázdnych riadkov,
  spojené jedným prázdnym riadkom a ukončené novým riadkom. Cieľ `agentsmd`
  nepoužívaj: pred pravidlá vkladá všeobecný anglický úvod.
- **Skilly:** `.rulesync/skills/<name>/` sa skopíruje do `.claude/skills/<name>/`
  a `.agents/skills/<name>/`; v `SKILL.md` sa odstráni prázdny riadok hneď za
  frontmatterom a všetko ostatné zostane. Rulesync frontmatter znova serializuje
  ako YAML a zloženú hodnotu `>-` zalamuje na 80 znakov (vrátane odsadenia),
  preto zdroj píš už v tomto tvare.
- **Subagenti** (keď cieľ uvádza `subagents`): `.claude/agents/<name>.md`
  zachová `name`, `description` a sploštené kľúče `claudecode` (zoznamy v
  blokovom štýle), vynechá `targets` a telo nasleduje hneď za frontmatterom.
  `.codex/agents/<name>.toml` obsahuje `name`, `description`, kľúče `codexcli`
  a telo ako `developer_instructions = '''…'''`.
- **Odstránenie:** zmaž výstupy zrušeného alebo pretargetovaného zdroja a
  uprav `.gitignore`, ak niektorý výstup ignoruje.

Vygenerované súbory nemajú žiadnu značku. Keď si nie si istý presným formátom
výstupu, over ho v dokumentácii Rulesync namiesto hádania. Bežiaca session si
môže ponechať skôr načítané inštrukcie; pred spoliehaním sa na zmenené
inštrukcie použi novú session.

Over, že:

- každý výstup zodpovedá tomu, čo by vygenerovali kanonické zdroje, a nezostal
  žiadny zastaraný výstup;
- pravidlá a skilly majú zamýšľaný rozsah a aktiváciu;
- nevznikol duplicitný normatívny vlastník;
- bežný kontext agenta neobsahuje zbytočné inštrukcie.

Prezri výsledný kontext agenta a ak zmena pridala stále aktívny obsah, znova
uplatni test skracovania.

Uvádzaj iba overenie, ktoré sa skutočne vykonalo.

## Uplatni túto politiku aj na seba

Tieto princípy uplatni aj pri zmene tohto skillu.

Môže si ponechať detaily, ktoré podstatne zlepšujú prácu s governance, ale
odstráň pokyny, ktoré sa stanú nadbytočnými, zastaranými, duplicitnými alebo
ich prirodzene vlastní niekto iný.
