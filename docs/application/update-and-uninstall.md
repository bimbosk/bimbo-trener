# Aktualizácia a odinštalovanie

## Aktualizácia

V repozitári `git pull`, potom `install.cmd`. Inštalácia pri chýbajúcom runtime vytvorí
prostredie nanovo, zachová `config`, kópiu `scripts` vymení cez pripravený adresár a starú
generáciu nechá v `sprava\scripts-previous-*`. Dátový adresár sa nikdy nemení okrem
migrácie schémy databázy, ktorá pred zmenou urobí zálohu
([zálohy](../coach/backups.md)) a výsledok overí. Po zmene MCP registrácie reštartovať
asistenta.

Upgrade pripnutých balíkov (najmä `garminconnect`) je vedomá zmena: najprv prečítať
poznámky k vydaniu, zmeniť zámok v repozitári, skúsiť `cli.py login` a `sync` v konzole, až
potom nasadiť na ostatné počítače. V plánovanej úlohe sa nikdy nepoužíva `--upgrade`.

## `reset-runtime`

Zavrieť asistentov a všetko, čo používa venv. `install.cmd -Action reset-runtime` vypne
vlastnú MCP registráciu a odstráni iba `runtime`; `config`, `logs`, `sprava` ostanú.
Následné `install.cmd` runtime obnoví.

## Odinštalovanie

`uninstall.cmd` odpojí MCP registrácie (obnoví zálohu `config.toml`), odstráni skratku
a plánovanú úlohu podľa evidencie a presunie celú app do susedného adresára na obnovu
(`.bimbo-trener-app-uninstalled-<id>`); nič nemaže rekurzívne. **Dátový adresár sa
nedotkne**; mám ho na ostatných počítačoch a v zálohách. Token Garminu je v presunutej
app; po kontrole ho zmazať alebo odvolať prístup v účte Garmin.

## Prechod na iný počítač

Nainštalovať app, v dialógu ukázať na už synchronizovaný dátový adresár (`attach`);
nič sa neimportuje znova. Prihlásenie do Garminu iba ak má aj tento počítač sťahovať.
