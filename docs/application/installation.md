# Inštalácia

Jeden vstup `install.cmd` z koreňa repozitára. Jednoduchý je
[návod na nový počítač](../usage/new-computer.md); táto stránka je technický popis
a návrh.

## Predpoklady

- 64-bitový Windows 11, bežný používateľský účet, **nie správca**; internet.
- Nainštalovaný a prihlásený Claude Code alebo Codex (aplikácia ChatGPT); inštalátor ich
  neinštaluje.
- Sync nástroj už synchronizuje priečinok, kde bude dátový adresár.
- Git, Python ani uv netreba; inštalátor ich pripraví lokálne (alternatívne winget pre
  Python je otvorené O5).

## Spustenie

Dvojklik na `install.cmd` alebo z PowerShellu v koreni repozitára. Spúšťač použije 64-bitový
Windows PowerShell 5.1 s `ExecutionPolicy Bypass` iba pre tento proces. Parametre:

| Parameter | Význam |
| --- | --- |
| `-Component common\|coach\|sync` | iba jeden komponent |
| `-InstallDirectory 'D:\…\bimbo-trener-app'` | iný cieľ pre tento beh |
| `-DataDirectory 'D:\Sync\Bimbo-data'` | dátový adresár bez dialógu |
| `-Action reset-runtime\|uninstall` | správa namiesto inštalácie |

## Čo inštalátor urobí (návrh)

1. **Kontroly a zámok.** Natívny Windows, 64-bit, nie správca; zámok proti súbehu;
   odmietnutie cudzieho neprázdneho cieľa, junctions a symlinkov; značka vlastníka.
2. **Spoločné prostredie.** Do `runtime` stiahne uv pripnutej verzie, ním spravovaný
   Python 3.14, vytvorí venv a nainštaluje pripnuté balíky zo zámku s hashmi
   ([externé nástroje](external-tools.md)); skopíruje `scripts`. PATH ani registre sa
   nemenia.
3. **Dátový adresár.** Ak je zadaný alebo uložený v `config\local.json`, použije ho; inak
   otvorí dialóg výberu priečinka. Priečinok s markerom pripojí (`attach`), prázdny
   inicializuje (`init`), neprázdny cudzí odmietne.
4. **Skúška.** Import vzorového FIT súboru z repozitára (syntetický, bez mojich dát) do
   dočasnej databázy; `status` z nainštalovanej kópie.
5. **Skratka.** „Stiahni dáta z Garminu“ na ploche → `cli.py sync` s oknom so správou.
6. **MCP registrácia.** `bimbo_trener` (STDIO, absolútne cesty do venv a dátového adresára)
   do `config.toml` Codexu so zálohou a do Claude Code cez `claude mcp add`; evidencia
   v `sprava`.
7. **Komponent `sync`** (iba na požiadanie): `cli.py login` v konzole s MFA; po úspechu
   plánovaná úloha raz denne, Interactive, `StartWhenAvailable`, bez súbežných inštancií.
8. **Záver.** Výzva na reštart asistenta; cesta k logu.

Zlyhanie kroku zastaví nasledujúce; dokončené ostávajú. Kód 0 potvrdzuje prejdené skúšky,
nie prvé reálne stiahnutie z Garminu.

## Výstupy

Transcript `logs\instalacia-<čas>.log`, `sprava\sprava.json` s evidenciou vonkajších
zápisov, kód 0/1.
