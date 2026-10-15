---
name: sync-garmin-data
description: >-
  Použi, keď poviem „stiahni dáta“ alebo keď dnešný beh v databáze chýba.
  Preskoč ručný import, ak som FIT súbor nevložil sám.
---

# Stiahnutie dát z Garminu

1. Zavolaj MCP `run_sync()`; ak nástroj nie je dostupný, spusti `sync.cmd`
   v koreni repozitára a prečítaj výsledok.
2. Kód 0: povedz, čo pribudlo (`message`), a pokračuj skillom
   `evaluate-run`.
3. Kód 77: na tomto počítači nie je sťahovanie nastavené alebo vypršalo
   prihlásenie; poraď `install.cmd -Component sync`. Konzultácia funguje
   ďalej.
4. Kód 75: Garmin dočasne odmieta; uveď čas ďalšieho pokusu zo správy,
   neopakuj.
5. Ak som vložil FIT súbor ručne do `fit\manual`, zavolaj `import_fit()`.
