# 2026-10-15 — prieskum: ako dostať dáta z Garmin hodiniek do lokálnej databázy

**Metóda:** webový prieskum agenta 15. 10. 2026 (vyhľadávanie, čítanie GitHub issues
a zdrojových kódov, PyPI, Garmin fóra, dokumentácia). Závery prevzaté do špecifikácie:
[sťahovanie z Garminu](../coach/garmin-sync.md), [Garmin Connect](../integrations/garmin-connect.md).
Rozhodnutie: [vlastný sťahovač](../decisions/2026-10-15-own-sync-script.md).

## Zistenie 1: vlastníkom dát je FIT súbor

Hodinky zapisujú každú aktivitu do binárneho súboru FIT so súhrnom (session), kolami
(lap), sekundovými záznamami (record: tep, tempo, kadencia, výkon, dynamika) a udalosťami
(pauzy, zmeny). Garmin Connect ho iba zobrazuje. Oficiálne Garmin FIT SDK pre Python ho
parsuje; alternatívy fitdecode a fitparse. Všetky cesty nižšie končia FIT súborom.

## Zistenie 2: štyri cesty FIT súboru do počítača

| Cesta | Ako | Spoľahlivosť | Poznámka |
| --- | --- | --- | --- |
| Ručný export z webu | connect.garmin.com → aktivita → ozubené koliesko → „Export Original“ / „Export File“ → ZIP s FIT | 100 % | mobilná aplikácia export nevie; web funguje aj v prehliadači telefónu |
| Kopírovanie z hodiniek káblom | priečinok `GARMIN/Activity`; novšie hodinky cez MTP, ktoré Windows má zabudované (bez písmena disku) | závisí od modelu | plne offline; na Linuxe treba gvfs-mtp |
| Neoficiálna knižnica `python-garminconnect` | prihlásenie účtom s MFA, token, `get_activities_by_date`, `download_activity(..., ORIGINAL)` | funguje, ale krehká | súkromné rozhranie Garminu; viď riziká |
| Hromadný export účtu | garmin.com → Account → Data Management → Export Your Data → ZIP (vnorené ZIPy, `DI_CONNECT`) | spoľahlivá, pomalá | hodiny až dni, odkaz rýchlo expiruje, bez výberu obdobia; na jednorazové doplnenie histórie |

## Zistenie 3: oficiálne API pre jednotlivca neexistuje

Garmin Connect Developer Program (Health/Activity API) je pre firmy a inštitúcie. Od jari
2026 Garmin nové žiadosti neprijíma; bez termínu obnovenia. Garmin Express pre Linux
neexistuje (pre Windows áno, ale lokálne FIT nedáva). Prepojenie cez Stravu alebo
intervals.icu by posielalo zdravotné dáta tretej strane a Garmin z partnerského API od
septembra 2026 filtruje vlastné metriky (Training Effect, Stamina, Recovery Time, VO2max);
vlastný „Export Original“ je úplný (porovnanie 719 kB vs. 601 kB na fóre intervals.icu).

## Zistenie 4: riziká neoficiálnej knižnice (stav k 15. 10. 2026)

- Garmin používa Cloudflare s TLS fingerprintingom; knižnica musí napodobňovať prehliadač
  cez `curl_cffi` (issue #444: platný token dostáva 403 cez obyčajné `requests`).
- Prihlasovanie dostáva 429 aj podľa odtlačku klienta, nie iba podľa frekvencie či IP
  (PR #449, zlúčený 29. 9. 2026). Issue #453 zo 7. 10. 2026: verzia 0.3.17, jediný pokus
  o prihlásenie po vyše 24 h dostal 429 hneď na prvý request; správca 15. 10. odpovedal, že
  používateľ vypol predvolenú stratégiu s curl_cffi. Issue je otvorené.
- Garmin fórum: účet blokovaný pre API prihlásenie vyše 48 h po pár neúspešných pokusoch;
  web a mobil fungovali.
- Predchádzajúca knižnica `garth` bola ukončená, lebo Garmin zmenil prihlasovanie
  (garminconnect 0.3.0 z apríla 2026 ju nahradil vlastným overovaním; staré tokeny
  nefungujú).
- Hotové projekty nad knižnicou: GarminDB (tcgoetz) a garmin-health-data (diegoscarabelli);
  obidva sťahujú celý zdravotný profil do vlastnej SQLite schémy. GarminDB 4.0.0 pevne viaže
  garminconnect 0.3.11, po neúspešnom prihlásení končí kódom 0, archív aktivít nestránkuje
  a bezpečné heslo podporuje iba cez macOS Keychain (overené v zdrojovom kóde).

## Záver prieskumu

Vstupom importu je vždy FIT súbor v priečinku, nech prišiel akoukoľvek cestou. Ručný export
z webu funguje od prvého dňa a ostáva zálohou; automatizácia cez knižnicu je pohodlná, ale
musí mať cooldown a nikdy sa neprihlasovať v slučke; hromadný export doplní históriu.

## Zdroje

- python-garminconnect: [repozitár](https://github.com/cyberjunky/python-garminconnect),
  [PyPI](https://pypi.org/project/garminconnect), [issue #444](https://github.com/cyberjunky/python-garminconnect/issues/444),
  [issue #453](https://github.com/cyberjunky/python-garminconnect/issues/453),
  [PR #449](https://github.com/cyberjunky/python-garminconnect/pull/449),
  [issue #344](https://github.com/cyberjunky/python-garminconnect/issues/344)
- [garth — ukončenie](https://github.com/matin/garth/discussions/222)
- [GarminDB](https://github.com/tcgoetz/GarminDB), [offline diskusia](https://github.com/tcgoetz/GarminDB/discussions/156),
  [garmin-health-data](https://github.com/diegoscarabelli/garmin-health-data)
- [garmin-fit-sdk na PyPI](https://pypi.org/project/garmin-fit-sdk/), [FIT SDK](https://developer.garmin.com/fit/overview/),
  [fitdecode](https://github.com/polyvertex/fitdecode)
- Export: [FitMesh](https://www.fitmesh.fit/en/blog/export-garmin-data), [takeoutday](https://takeoutday.org/guides/how-to-export-garmin-connect-data),
  [Garmin fórum — export ZIP s FIT](https://forums.garmin.com/apps-software/mobile-apps-web/f/garmin-connect-web/421060/exporting-individual-activity-raw-data),
  [Garmin fórum — hromadný export](https://forums.garmin.com/outdoor-recreation/outdoor-recreation/f/fenix-7-series/421977/i-need-a-way-to-export-all-my-activities-from-garmin-connect-into-separate-fit-files-so-i-can-put-them-in-my-other-device-i-am-finished-with-garmin-at-this-point)
- MTP: [Arch wiki](https://wiki.archlinux.org/title/Mtp), [Garmin fórum MTP na Linuxe](https://forums.garmin.com/outdoor-recreation/outdoor-recreation/f/enduro-2/411940/mtp-with-linux)
- Developer Program: [the5krunner](https://the5krunner.com/2026/09/14/garmin-developer-api-access-paused/),
  [Terra](https://tryterra.co/blog/garmin-connect-developer-program-pause), [ghurt](https://ghurt.org/garmin-api-for-personal-use)
- [Garmin fórum — TLS fingerprinting](https://forums.garmin.com/apps-software/mobile-apps-web/f/garmin-connect-web/433892/tls-fingerprinting-blocks-third-party-clients),
  [Garmin fórum — 429 48 h](https://forums.garmin.com/developer/fit-sdk/f/discussion/435087/persistent-429-on-api-login-account-blocked-for-48-hours),
  [intervals.icu — filtrovanie FIT](https://forum.intervals.icu/t/garmin-fit-fields-not-coming-in-possible-garmin-is-filtering-data-prior-to-sending-to-intervals-icu/124287/69)
