# 2026-10-15 — overenie verzií a odporúčaná kombinácia

**Metóda:** čítanie PyPI (JSON API a stránky súborov), GitHub Releases a python.org
15. 10. 2026. Záväzné verzie pre inštalátor vlastní
[externé nástroje](../application/external-tools.md); tento záznam dokladá, prečo.

| Súčasť | Najnovšia verzia | Dátum | Zistenie |
| --- | --- | --- | --- |
| Python | 3.15.0 | 9. 10. 2026 | týždeň staré; 3.14.8 a 3.13.16 z 30. 9. 2026; rad 3.13 je od októbra 2026 iba v bezpečnostnej údržbe, 3.14 v bugfix do 10/2030 |
| garminconnect | 0.3.18 | 15. 10. 2026 | vyšla v deň overenia; bez breaking changes; prihlasovanie cez iOS klientské ID; klasifikátory 3.12, 3.13, 3.14; závislosti `curl_cffi>=0.15.0`, `requests>=2.33.0`, `ua-generator>=1.0`; `requires_python>=3.12` |
| garminconnect 0.3.17 | — | 29. 9. 2026 | predchádzajúca; rovnaký formát tokenov; záloha, ak by 0.3.18 robila problémy |
| curl_cffi | 0.16.3 | 2. 9. 2026 | wheel `cp310-abi3-win_amd64` pokrýva CPython 3.10–3.14; beta 0.16.4b1 z 20. 9. bez changelogu |
| garmin-fit-sdk | 21.218.0 | 6. 10. 2026 | čistý Python (`py3-none-any`), `requires_python>=3.6`, licencia FIT Protocol License Agreement |
| fitdecode | 0.11.0 | 6. 8. 2025 | alternatíva, rok bez vydania |
| GarminDB | 4.0.0 | 16. 9. 2026 | `requires_python>=3.12`, Windows classifier, pevne viaže `garminconnect==0.3.11`; GitHub master hlási 3.9.0 |

## Odporúčaná kombinácia

- **Python 3.14.8**: aktívna bugfix fáza, deklarovaný knižnicou, abi3 wheel curl_cffi,
  FIT SDK čistý Python. Python 3.15 je príliš čerstvý (curl_cffi preň nemá overený wheel);
  3.13 už nedostáva opravy chýb.
- **garminconnect 0.3.18** pripnutý presne; upgrade vedome po prečítaní poznámok k vydaniu.
- **curl_cffi 0.16.3** pripnutý; predvolená stratégia prihlasovania sa nevypína.
- **garmin-fit-sdk 21.218.0**.
- **GarminDB nepoužiť** ([rozhodnutie](../decisions/2026-10-15-own-sync-script.md)).

Výhrada: 0.3.18 nemá k dátumu overenia prevádzkovú skúsenosť.

## Zdroje

[garminconnect JSON](https://pypi.org/pypi/garminconnect/json), [release 0.3.18](https://github.com/cyberjunky/python-garminconnect/releases/tag/0.3.18),
[pyproject](https://raw.githubusercontent.com/cyberjunky/python-garminconnect/master/pyproject.toml),
[curl-cffi súbory 0.16.3](https://pypi.org/project/curl-cffi/0.16.3/#files), [curl_cffi releases](https://github.com/lexiforest/curl_cffi/releases),
[garmin-fit-sdk JSON](https://pypi.org/pypi/garmin-fit-sdk/json), [fitdecode JSON](https://pypi.org/pypi/fitdecode/json),
[python.org downloads](https://www.python.org/downloads/), [devguide versions](https://devguide.python.org/versions/),
[GarminDB 4.0.0 JSON](https://pypi.org/pypi/GarminDB/4.0.0/json), [GarminDB version_info](https://raw.githubusercontent.com/tcgoetz/GarminDB/master/garmindb/version_info.py)
