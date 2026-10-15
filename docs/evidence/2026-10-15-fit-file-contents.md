# 2026-10-15 — obsah FIT súboru z Venu 4 a porovnanie exportov

**Zdroj:** jeden môj beh na páse exportovaný z Garmin Connect vo všetkých dostupných
formátoch (FIT originál, TCX, GPX, CSV aktivity) a export zoznamu aktivít `Activities.csv`.
FIT dekódovaný Garmin FIT SDK 21.218.0 bez chýb. Súbory ležia v `beh/` mimo Gitu; tu je iba
štruktúra, nie hodnoty.

## Porovnanie formátov

| Formát | Obsah | Záver |
| --- | --- | --- |
| FIT originál | 30 typov správ, sekundové záznamy, kolá, zóny, splity, profil, nastavenia | **jediný potrebný zdroj** |
| TCX | body po sekundách (čas, vzdialenosť, tep, rýchlosť, kadencia, výkon), kolá so súhrnmi | podmnožina FIT bez dynamiky behu a zón, 8× väčší |
| CSV aktivity | kolá a zhrnutie, 28 stĺpcov vrátane dynamiky | iba súhrny kôl |
| GPX | prázdna stopa (pás nemá GPS) | bezcenné |
| `Activities.csv` | jeden riadok na aktivitu, 39 stĺpcov (typ, dátum, vzdialenosť, čas, tep, TE, kadencia, tempo, dynamika, výkon, NP, TSS, kroky, kolá, časy) | rýchly prehľad histórie bez identifikátora aktivity, kôl a priebehu; plnú históriu dá stiahnutie FIT podľa dátumu |

## Správy vo FIT (Venu 4, firmvér 18.32)

| Správa | Počet | Čo obsahuje |
| --- | --- | --- |
| `file_id`, `file_creator`, `device_info` | 1, 1, 8 | zariadenie, sériové číslo, firmvér, senzory (barometer, akcelerometer, optický tep) |
| `sport` | 1 | `running` / `treadmill`, názov profilu |
| `session` | 1 | súhrn: časy (elapsed, timer), vzdialenosť, rýchlosť priem./max, tep priem./max, kadencia, výkon priem./max, `normalized_power`, `total_work`, `total_strides`, `training_load_peak`, Training Effect aeróbny/anaeróbny, kalórie, dynamika behu (oscilácia mm, kontakt ms, pomer %, dĺžka kroku mm) |
| `lap` | 1 na km | rovnaké polia ako session; `lap_trigger = distance` — hodinky robia kolo každý kilometer, **nie moje úseky** |
| `record` | 1 za sekundu, bez medzier | vzdialenosť, rýchlosť, tep, kadencia, výkon, kumulovaný výkon, oscilácia, pomer, dĺžka kroku, kontakt (dynamika v ~99 % záznamov) |
| `event` | 2 | manuálny štart a stop; zmeny rýchlosti pásu sa prejavia iba v `record` |
| `time_in_zone` | session + každé kolo | čas v 7 tepových a 8 výkonových zónach, hranice zón, max/pokojový/prahový tep, FTP |
| `split`, `split_summary` | 6 + 4 | Garminovo rozpoznanie beh / chôdza / státie s časmi |
| `user_profile` | 1 | meno, hmotnosť, výška, pokojový tep, nastavenia jednotiek — **osobné údaje**, dôvod držať FIT mimo Gitu |
| `zones_target`, `training_settings`, `device_settings`, `battery` | 1, 1, 1, každých 5 min | nastavenia zón a FTP, cieľ, nastavenia hodiniek, stav batérie |
| 12 nepomenovaných typov (číselné ID) | 1 až ~3 000 | Garminove interné polia; uchovať surovo |

## Zistenia pre dátový model a import

- FIT ukladá dynamiku v milimetroch a milisekundách; web zobrazuje centimetre. Prevody
  robí vrstva analýz, databáza drží jednotky FIT.
- Čas v zónach a hranice zón sú vo FIT; Garmin ich prepočítava, preto sa k behu ukladá
  snímka zón a prahov platná v deň behu.
- Rýchlosť z hodiniek na páse kolíše okolo nastavenej hodnoty (hodinky odhadujú z kroku);
  histogram rýchlosti po sekundách ukazuje, kedy bola nastavená ktorá rýchlosť.
- Porovnanie s predpisom (10 rovnakých úsekov) ide zo sekundových záznamov delených podľa
  času, nie z kilometrových kôl.
- Export z webu Garmin Connect obsahuje FIT v ZIP; knižnica `download_activity(ORIGINAL)`
  dáva ten istý súbor.
