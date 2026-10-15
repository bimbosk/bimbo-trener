# Tréner na novom počítači

**Návrh návodu; postup ešte nebol odskúšaný.**

## Čo potrebujem

- Počítač s Windows 11 a internet.
- Prihlásený Claude Code alebo aplikáciu ChatGPT s Codexom.
- Priečinok, ktorý sa mi synchronizuje medzi počítačmi (tam bude dátový adresár).

Git, Python ani iné programátorské nástroje nepripravujem.

## 1. Stiahnem projekt

V PowerShelli v priečinku, kde má projekt byť, vložím blok z návodu
[`HOW_TO_USE.md`](../../HOW_TO_USE.md) v koreni repozitára. Nainštaluje Git, GitHub CLI
a GitHub Desktop, prihlási ma do GitHubu a stiahne priečinok `bimbo-trener`. Projekt sa
tým ešte neinštaluje.

## 2. Spustím nastavenie

Dvojklik na `install.cmd` v priečinku `bimbo-trener` (bežne, nie ako správca). Inštalátor:

- pripraví vedľa repozitára priečinok `bimbo-trener-app`,
- opýta sa, **kde majú byť dáta** — vyberiem priečinok v synchronizovanom umiestnení,
  napríklad `D:\Sync\Bimbo-data`. Ak tam už dáta z iného počítača sú, iba ich pripojí,
- vytvorí na ploche skratku **Stiahni dáta z Garminu**,
- napojí trénera na Claude Code a Codex.

Trvá to niekoľko minút. Pri chybe je celé hlásenie v `bimbo-trener-app\logs`.

## 3. Prihlásenie do Garminu (iba na počítači, kde budem sťahovať)

Raz spustím prihlásenie v konzole: e-mail, heslo a kód z telefónu. Heslo sa nikam
neukladá. Na ostatných počítačoch sa neprihlasujem; tam sa tréner iba radí.

## 4. Otvorím projekt v asistentovi

V Claude Code alebo v Codexe otvorím priečinok `bimbo-trener` a napíšem:

> Načítaj kontext a povedz mi, kde som.

Tréner prečíta môj stav a posledné dni. Ak je databáza prázdna, povie to a navrhne prvý
krok (napríklad ručný export posledného behu z Garmin Connect).

## Ak už projekt na inom počítači mám

Kroky 1 a 2 sú rovnaké; v kroku 2 ukážem na ten istý synchronizovaný priečinok. Krok 3
preskočím, pokiaľ nechcem sťahovať aj tu.
