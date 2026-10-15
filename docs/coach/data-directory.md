# Dátový adresár

Jediné miesto, kde žijú moje dáta. Vyberám si ho sám, leží na lokálnom SSD a môj sync
nástroj ho roznáša na všetky jeho počítače
([rozhodnutie](../decisions/2026-10-15-synced-data-directory.md)).

## Štruktúra (návrh)

```text
<data_dir>\
  bimbo-data.json          marker: {"format":"bimbo-trener/data/v1","data_id":"<uuid>",
                           "created_at":"…","schema":…,"app_version":"…"}
  runs.sqlite3             databáza (jediný vlastník zapisovaných dát)
  fit\<activity_id>.fit    originálne FIT súbory, jeden na beh, nikdy sa neprepisujú
  fit\manual\              FIT súbory vložené ručne (export z webu, kopírovanie z hodiniek)
  backups\                 zálohy databázy ([zálohy](backups.md))
  preview\                 generovaný Markdown náhľad denníka a stavu (mazateľné)
  logs\                    logy sťahovania a importu (bez zdravotných dát)
```

## Pravidlá

- MUSÍ byť na lokálnom disku, nie UNC ani mapovaný sieťový disk; synchronizácia medzi
  počítačmi je vec sync nástroja, nie aplikácie.
- NESMIE byť v repozitári ani v `runtime` aplikácie; reset ani odinštalovanie aplikácie ho
  nemažú.
- Databáza sa otvára bez WAL (journal mode `DELETE`), aby na disku bol jeden súbor a sync
  nikdy nevidel `-wal`/`-shm`.
- Každý zápis do databázy ide cez dočasný súbor a atomické premenovanie alebo cez SQLite
  transakciu s následnou zálohou; sync nesmie zachytiť rozpísaný súbor.
- FIT súbory sa iba pridávajú. Z nich a zo záloh je databáza obnoviteľná.
- Prihlasovací token Garminu do dátového adresára **nepatrí**
  (  [Garmin Connect](../integrations/garmin-connect.md)).

## Výber a pripojenie

- Pri inštalácii alebo v nastaveniach vyberiem priečinok (dialóg výberu).
- `init`: prázdny alebo neexistujúci priečinok → vytvorí sa marker, databáza a podpriečinky.
  Neprázdny cudzí priečinok sa odmietne.
- `attach`: priečinok s platným markerom (napr. už synchronizovaný z iného PC) → pripojí
  sa, nič sa nevytvára ani neprepisuje. Toto je bežný prípad na druhom až desiatom počítači.
- Cesta sa uloží do lokálneho configu aplikácie na tomto PC.

## Lokálny config (viazaný na počítač, mimo sync)

```json
{
  "schema_version": 1,
  "data_dir": "D:\\Sync\\Bimbo-data",
  "garmin_sync_enabled": false,
  "token_dir": "<app>\\config\\garmin"
}
```

`garmin_sync_enabled` je `true` iba na počítači, kde som prešiel prihlásením do Garminu.
Inde skratka „Stiahni dáta“ oznámi, že sťahovanie tu nie je nastavené.

## Čo cestuje kde

| Druh | Kde | Prečo |
| --- | --- | --- |
| behy, predpisy, denník, stav, plán, konvencie | databáza v dátovom adresári | musí byť na každom PC |
| FIT súbory, zálohy | dátový adresár | zdroj pravdy a obnova |
| cesta k dátovému adresáru, token Garminu, logy inštalácie | app na danom PC | viazané na stroj alebo citlivé |
| kód, pravidlá, dokumentácia | repozitár (Git) | verzované, bez dát |
