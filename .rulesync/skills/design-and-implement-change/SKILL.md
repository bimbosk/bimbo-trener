---
name: design-and-implement-change
description: >-
  Použi, keď implementácia prináša podstatné rozhodnutia o architektúre,
  závislostiach, hraniciach modulov alebo mechanizmoch. Preskoč úzke úpravy,
  ktoré iba uplatňujú zavedený návrh bez takého rozhodnutia.
---

# Návrh a implementácia zmeny

## Ohranič zmenu

- Pred úpravami identifikuj požadovaný výsledok, autoritatívnych vlastníkov,
  dotknutých konzumentov, záväzky kompatibility, vygenerované artefakty a
  relevantné kontroly.
- Zahrň každú zmenu potrebnú pre výsledok; nepoužívaj kvótu na počet súborov
  ani veľkosť diffu. Neočakávane širokú synchronizáciu najprv preskúmaj, až potom
  uprav každý nájdený výskyt; rozlišuj konzumentov od skopírovanej politiky.
- Znovu použi platný schválený plán alebo kontrakt. Plánuj iba do hĺbky, ktorú
  si vyžaduje aktuálna zložitosť, riziko a nevyriešené rozhodnutia.
- Očakávaná budúca práca môže odôvodniť čistú hranicu, ak ju preukazuje
  schválená blízka zodpovednosť. Neoprávňuje však implementovať toto budúce
  správanie teraz.

## Vyber mechanizmus

- Pred návrhom vlastnej infraštruktúry skontroluj existujúce prostriedky
  repozitára a zrelé natívne mechanizmy.
- Závislosť pridaj iba pre preukázanú potrebu. Zhodnoť jej údržbu, bezpečnosť a
  kompatibilitu. Uprednostni štandardnú knižnicu Pythonu (vrátane `sqlite3`).
  Zdôvodnenie zaznamenaj iba tam, kde to existujúci vlastník vyžaduje.
- Nevytváraj hypotetické funkcie, falošnú paritu, generické frameworky pre jeden
  prípad ani nové registre, plánovače, služby, databázy či generátory bez
  konkrétnej zodpovednosti.
- Využívaj zavedené mechanizmy konfigurácie, logovania, chýb, serializácie,
  validácie a nástrojov namiesto paralelného správania.

## Usporiadaj vlastníctvo implementácie

- Uprednostni súdržné moduly pred viacúčelovými súbormi. Oddeľ zodpovednosti s
  rôznymi dôvodmi na zmenu; súvisiace zamerané moduly zoskup v jasných
  adresároch.
- Deľ alebo spájaj podľa zodpovednosti a skutočnej väzby, nie podľa počtu
  riadkov. Jednoduchú súdržnú logiku drž spolu. Vyhni sa prázdnemu lešeniu,
  generickým odkladiskám, jednorazovej indirekcii, súborom iba pre symetriu a
  paralelným implementáciám.
- Súbor alebo adresár vytvor, keď skutočný artefakt potrebuje vlastníka.
  Nesúvisiace správanie nepridávaj len preto, aby si menil menej súborov.
- Nepodporované stavy a zlyhania nech sú viditeľné a riešiteľné. Zámerne
  špecifikované náhradné riešenie zachovaj, ale nevymýšľaj také, ktoré mení
  zlyhanie na zdanlivý úspech.
