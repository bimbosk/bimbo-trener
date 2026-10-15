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

## Konfigurácia: `bimbo-trener.json` v koreni repozitára

Jediný konfiguračný súbor, commitnutý v Gite, formát JSON (štandardná knižnica, bez
závislostí). Drží všetko, čo je spoločné pre všetky moje počítače:

```json
{
  "schema_version": 1,
  "install_root": "../bimbo-trener-app",
  "data_dir": "D:\\Sync\\Bimbo-data",
  "database": "runs.sqlite3",
  "fit_dir": "fit",
  "backups": { "rotate": 10, "daily_days": 30, "monthly_months": 12 },
  "sync": { "health_days": 4, "cooldown_minutes": 90, "daily_task_time": "07:30" },
  "garmin": { "token_dir": "<app>/config/garmin" }
}
```

- `install_root` je cieľ aplikácie vedľa repozitára ([členenie](../application/layout.md)).
- `data_dir` je cesta k dátovému adresáru; `database` a `fit_dir` sú relatívne k nemu.
- `<app>` sa nahrádza skutočnou cestou aplikácie na danom počítači.

**Miestny prepis `bimbo-trener.local.json`** v koreni repozitára, ignorovaný Gitom, má
rovnaký tvar a prepíše iba uvedené kľúče. Použije sa na počítači, kde je dátový adresár
na inej ceste alebo kde je zapnuté sťahovanie:

```json
{ "data_dir": "E:\\Sync\\Bimbo-data", "garmin_sync_enabled": true }
```

`garmin_sync_enabled` je `true` iba na počítači, kde som prešiel prihlásením do Garminu;
nikdy nie je v commitnutom súbore. Inde skratka „Stiahni dáta“ oznámi, že sťahovanie tu
nie je nastavené. Inštalátor pri výbere dátového adresára zapíše cestu do miestneho
prepisu, ak sa líši od commitnutej; commitnutú hodnotu mením ja ručne, keď má platiť
všade. Poradie čítania: `bimbo-trener.json` → `bimbo-trener.local.json` → parametre
príkazu.

## Čo cestuje kde

| Druh | Kde | Prečo |
| --- | --- | --- |
| behy, predpisy, denník, stav, plán, konvencie | databáza v dátovom adresári | musí byť na každom PC |
| FIT súbory, zálohy | dátový adresár | zdroj pravdy a obnova |
| spoločná konfigurácia (`bimbo-trener.json`) | repozitár (Git) | rovnaká na všetkých PC |
| miestny prepis (`bimbo-trener.local.json`), token Garminu, logy | repozitár mimo Gitu / app na danom PC | viazané na stroj alebo citlivé |
| kód, pravidlá, dokumentácia | repozitár (Git) | verzované, bez dát |
