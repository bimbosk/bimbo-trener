# 2026-10-15 — moje zariadenia Garmin a aké dáta dávajú

**Zdroj:** zoznam zariadení v mojom Garmin Connect (fotka obrazovky) a webový prieskum
manuálov Garmin a zdrojového kódu knižnice `python-garminconnect`. Rozhodnutie zbierať
všetko: [záznam](../decisions/2026-10-15-collect-everything.md).

## Zariadenia v účte

| Zariadenie | Rola v Garmin Connect | Pre projekt |
| --- | --- | --- |
| Venu 4, 45 mm | primárne nositeľné zariadenie | zdroj behov a celodenných zdravotných dát |
| Index S2 | váha, Wi-Fi | hmotnosť a zloženie tela |
| Edge 1040 | primárne tréningové zariadenie (cyklopočítač), naposledy synchronizovaný 29. 5. 2026 | jazdy; sťahovanie ich ukladá ako aktivity iného typu |

## Venu 4: čo zapisuje

- **Pri behu zo zápästia** (manuál Garmin, Running Dynamics): kadencia, dĺžka kroku (m),
  vertikálna oscilácia (cm), vertikálny pomer (%), doba kontaktu so zemou (ms). Ľavo-pravá
  rovnováha kontaktu iba s hrudným pásom. Vo FIT sú v správach session, lap a record
  (`avg_vertical_oscillation`, `avg_stance_time`, `avg_step_length`, …); FIT ukladá
  milimetre, web zobrazuje centimetre — škálovanie overiť pri prvom importe.
- **Celodenne:** optický tep (Elevate Gen 5), pulzný oxymeter, teplota kože; z toho Garmin
  počíta pokojový tep, HRV status, spánok so skóre, stres, Body Battery, Training
  Readiness, Training Status, dýchanie, SpO2, kroky a intenzívne minúty.
- **Kábel:** MTP zariadenie; v Prieskumníku bez písmena disku, priečinok
  `Primary\GARMIN\Activity`; režim mass storage nie je k dispozícii.

## Index S2: čo zapisuje

Hmotnosť, BMI, percento tuku, kostrová svalová hmota, hmotnosť kostí, percento vody.
Nahráva cez Wi-Fi do Garmin Connect automaticky. Z webu sa dá exportovať iba CSV bez filtra
podľa dátumu.

## Volania knižnice (overené v zdrojovom kóde `garminconnect/__init__.py`)

| Dáta | Metóda | Argumenty |
| --- | --- | --- |
| zloženie tela | `get_body_composition` | `startdate, enddate=None` |
| váženia | `get_weigh_ins` / `get_daily_weigh_ins` | rozsah / `cdate` |
| denný súhrn (kroky, kalórie, minúty, tep) | `get_user_summary` | `cdate` |
| tep po minútach | `get_heart_rates` | `cdate` |
| pokojový tep | `get_rhr_day` | `cdate` |
| spánok | `get_sleep_data` | `cdate` (odpoveď na noc ~150 kB) |
| HRV | `get_hrv_data` | `cdate` |
| stres | `get_stress_data` | `cdate` |
| Body Battery | `get_body_battery` | `startdate, enddate=None` |
| Training Readiness | `get_training_readiness` | `cdate` |
| Training Status | `get_training_status` | `cdate` |
| dýchanie | `get_respiration_data` | `cdate` |
| SpO2 | `get_spo2_data` | `cdate` |

Dátumy vo formáte `YYYY-MM-DD`. Garmin denné hodnoty dopočítava spätne (spánok, HRV,
readiness), preto sa sťahujú znova za posledné dni.

## Zdroje

[Venu 4 manuál — Running Dynamics](https://www8.garmin.com/manuals/webhelp/GUID-2CF5620C-E585-4E0A-9CC3-9565533EEE4D/EN-US/GUID-62A09512-518A-424A-8491-FE2B80CD2091.html),
[Venu 4 manuál PDF](https://www8.garmin.com/manuals/webhelp/GUID-2CF5620C-E585-4E0A-9CC3-9565533EEE4D/EN-US/Venu_4_OM_EN-US.pdf),
[the5krunner — Venu 4](https://the5krunner.com/2025/09/25/garmin-venu-4-review-buyers-guide/),
[Index S2 manuál](https://www8.garmin.com/manuals/webhelp/GUID-0BADEBCF-960D-4961-856C-86B9204BC169/EN-US/GUID-F52A17EE-9B41-49BF-B9FF-3814BAC776CB.html),
[Index S2 oznámenie](https://www.businesswire.com/news/home/20201014005003/en/Measure-more-with-the-Index-S2-smart-scale-from-Garmin),
[Garmin fórum — export váhy CSV](https://forums.garmin.com/sports-fitness/healthandwellness/f/index-s2-smart-scale/247596/exporting-data-to-google-sheets),
[garminconnect zdrojový kód](https://raw.githubusercontent.com/cyberjunky/python-garminconnect/master/garminconnect/__init__.py),
[DC Rainmaker — MTP priečinok](https://www.dcrainmaker.com/2020/07/how-to-upload-your-garmin-workout-during-the-outage.html),
[Garmin fórum — Venu cez MTP](https://forums.garmin.com/sports-fitness/sports-fitness/f/venu-sq/358108/recovery-of-fit-files-using-mtp-device-connection),
[intervals.icu — polia dynamiky vo FIT](https://forum.intervals.icu/t/solved-garmin-running-dynamics-streams-gct-vertical-oscillation-vertical-ratio-gct-balance-not-populated-despite-being-present-in-the-fit-file/130560)
