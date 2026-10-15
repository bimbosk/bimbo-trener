# Jeden zdieľaný dátový adresár synchronizovaný medzi počítačmi

**Dátum:** 15. 10. 2026 · **Stav:** platí · **Oblasť:** [Dátový adresár](../coach/data-directory.md)

## Rozhodnutie

Všetky dáta trénera (FIT súbory, databáza, zálohy, generované náhľady) sú v jednom dátovom
adresári, ktorý si vyberiem v nastaveniach. Adresár leží na lokálnom SSD a môj
synchronizačný nástroj z neho robí identickú kópiu na všetkých mojich počítačoch.
Nastavenia viazané na počítač (cesta k adresáru, prihlasovací token Garminu) ostávajú mimo
neho.

## Dôvod

Chcem konzultovať tréning na ktoromkoľvek počítači. Nejde o sieťový disk: vždy lokálny
priečinok, iba synchronizovaný. Sťahovanie z Garminu spúšťam len na počítači, kde som
prihlásený; na ostatných sa iba číta a radí. Nesedím pri dvoch počítačoch naraz, takže
súčasný zápis z dvoch strojov pri bežnom používaní nenastane.

## Dôsledky

- Repozitár drží predvolenú cestu a dialóg výberu; aplikácia rozpozná existujúci dátový
  adresár podľa markera a pripojí ho bez vytvárania nového
  ([dátový adresár](../coach/data-directory.md)).
- Zápis do databázy je atomický a bez WAL režimu, aby sync nezachytil rozpísaný súbor a na
  disku bol jeden súbor.
- Okrajový prípad (zápis na PC A offline, potom zápis na PC B skôr, než dorazí verzia z A)
  môže vytvoriť konfliktnú kópiu; FIT súbory sa nikdy neprepisujú a databáza sa z nich
  a zo záloh dá obnoviť ([zálohy](../coach/backups.md)).
- Trvalé nastavenia trénera (konvencie, cieľ) cestujú v databáze; lokálne v configu
  aplikácie na každom PC.
