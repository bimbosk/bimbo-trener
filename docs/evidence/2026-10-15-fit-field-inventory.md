# 2026-10-15 — inventár polí FIT súboru z Venu 4 a stĺpcov exportov

**Zdroj:** jeden beh na páse (FIT originál, firmvér 18.32) dekódovaný Garmin FIT SDK 21.218.0;
exporty `Activities.csv` a CSV aktivity z Garmin Connect. Iba názvy polí a počet správ, v ktorých
má pole hodnotu; žiadne hodnoty. Slúži ako úplný zoznam toho, čo import zapisuje
([dátový model](../coach/data-model.md), [obsah FIT](2026-10-15-fit-file-contents.md)).

## Správy FIT a ich polia

Formát: `pole (počet správ s hodnotou / počet správ)`. Číselné názvy sú polia, ktoré profil SDK
nepozná; ukladajú sa surovo do `fit_raw`.

### `record` — 3005 správ

`135` (3005/3005), `136` (3005/3005), `143` (3005/3005), `activity_type` (3005/3005), `cadence` (3005/3005), `distance` (3005/3005), `enhanced_speed` (3005/3005), `fractional_cadence` (3005/3005), `heart_rate` (3005/3005), `power` (3005/3005), `timestamp` (3005/3005), `accumulated_power` (2995/3005), `vertical_oscillation` (2973/3005), `step_length` (2963/3005), `vertical_ratio` (2963/3005), `stance_time` (2962/3005)

### `time_in_zone` — 14 správ

`reference_index` (14/14), `reference_mesg` (14/14), `time_in_hr_zone` (14/14), `functional_threshold_power` (8/14), `hr_calc_type` (8/14), `hr_zone_high_boundary` (8/14), `max_heart_rate` (8/14), `power_zone_high_boundary` (8/14), `pwr_calc_type` (8/14), `resting_heart_rate` (8/14), `threshold_heart_rate` (8/14), `time_in_power_zone` (8/14), `timestamp` (8/14)

### `battery` — 10 správ

`0` (10/10), `3` (10/10), `4` (10/10), `capacity` (10/10), `timestamp` (10/10)

### `device_info` — 8 správ

`device_index` (8/8), `source_type` (8/8), `timestamp` (8/8), `device_type` (6/8), `local_device_type` (6/8), `software_version` (6/8), `garmin_product` (4/8), `manufacturer` (4/8), `product` (4/8), `serial_number` (2/8)

### `lap` — 7 správ

`145` (7/7), `avg_cadence` (7/7), `avg_fractional_cadence` (7/7), `avg_heart_rate` (7/7), `avg_power` (7/7), `avg_running_cadence` (7/7), `avg_stance_time` (7/7), `avg_step_length` (7/7), `avg_vertical_oscillation` (7/7), `avg_vertical_ratio` (7/7), `enhanced_avg_speed` (7/7), `enhanced_max_speed` (7/7), `event` (7/7), `event_type` (7/7), `intensity` (7/7), `lap_trigger` (7/7), `max_cadence` (7/7), `max_fractional_cadence` (7/7), `max_heart_rate` (7/7), `max_power` (7/7), `max_running_cadence` (7/7), `message_index` (7/7), `metabolic_calories` (7/7), `normalized_power` (7/7), `sport` (7/7), `start_time` (7/7), `sub_sport` (7/7), `timestamp` (7/7), `total_calories` (7/7), `total_cycles` (7/7), `total_distance` (7/7), `total_elapsed_time` (7/7), `total_strides` (7/7), `total_timer_time` (7/7), `total_work` (7/7)

### `split` — 6 správ

`7` (6/6), `end_time` (6/6), `message_index` (6/6), `split_type` (6/6), `sport` (6/6), `start_time` (6/6), `sub_sport` (6/6), `timestamp` (6/6), `total_elapsed_time` (6/6), `total_timer_time` (6/6), `135` (5/6), `136` (5/6), `avg_cadence` (5/6), `avg_heart_rate` (5/6), `avg_power` (5/6), `avg_running_cadence` (5/6), `avg_speed` (5/6), `max_cadence` (5/6), `max_heart_rate` (5/6), `max_power` (5/6), `max_running_cadence` (5/6), `max_speed` (5/6), `metabolic_calories` (5/6), `total_calories` (5/6), `total_distance` (5/6), `normalized_power` (4/6), `avg_stance_time` (2/6), `avg_step_length` (2/6), `avg_vertical_oscillation` (2/6), `avg_vertical_ratio` (2/6)

### `split_summary` — 4 správ

`85` (4/4), `86` (4/4), `88` (4/4), `avg_cadence` (4/4), `avg_heart_rate` (4/4), `avg_power` (4/4), `avg_speed` (4/4), `max_cadence` (4/4), `max_distance` (4/4), `max_heart_rate` (4/4), `max_power` (4/4), `max_speed` (4/4), `message_index` (4/4), `metabolic_calories` (4/4), `normalized_power` (4/4), `num_splits` (4/4), `split_type` (4/4), `start_time` (4/4), `timestamp` (4/4), `total_calories` (4/4), `total_distance` (4/4), `total_timer_time` (4/4), `avg_stance_time` (2/4), `avg_step_length` (2/4), `avg_vertical_oscillation` (2/4), `avg_vertical_ratio` (2/4)

### `event` — 2 správ

`data` (2/2), `event` (2/2), `event_group` (2/2), `event_type` (2/2), `timer_trigger` (2/2), `timestamp` (2/2)

### `activity` — 1 správ

`event` (1/1), `event_type` (1/1), `local_timestamp` (1/1), `num_sessions` (1/1), `timestamp` (1/1), `total_timer_time` (1/1), `type` (1/1)

### `device_settings` — 1 správ

`10` (1/1), `101` (1/1), `104` (1/1), `107` (1/1), `108` (1/1), `109` (1/1), `11` (1/1), `110` (1/1), `111` (1/1), `112` (1/1), `113` (1/1), `124` (1/1), `125` (1/1), `126` (1/1), `127` (1/1), `128` (1/1), `13` (1/1), `133` (1/1), `138` (1/1), `139` (1/1), `14` (1/1), `141` (1/1), `142` (1/1), `143` (1/1), `144` (1/1), `145` (1/1), `149` (1/1), `15` (1/1), `151` (1/1), `159` (1/1), `160` (1/1), `161` (1/1), `163` (1/1), `164` (1/1), `165` (1/1), `171` (1/1), `176` (1/1), `178` (1/1), `179` (1/1), `180` (1/1), `181` (1/1), `186` (1/1), `187` (1/1), `188` (1/1), `189` (1/1), `190` (1/1), `191` (1/1), `195` (1/1), `196` (1/1), `198` (1/1), `200` (1/1), `206` (1/1), `207` (1/1), `208` (1/1), `209` (1/1), `210` (1/1), `211` (1/1), `217` (1/1), `218` (1/1), `219` (1/1), `22` (1/1), `237` (1/1), `239` (1/1), `243` (1/1), `244` (1/1), `26` (1/1), `3` (1/1), `35` (1/1), `38` (1/1), `41` (1/1), `42` (1/1), `43` (1/1), `45` (1/1), `48` (1/1), `52` (1/1), `53` (1/1), `63` (1/1), `64` (1/1), `65` (1/1), `67` (1/1), `68` (1/1), `75` (1/1), `81` (1/1), `82` (1/1), `83` (1/1), `84` (1/1), `85` (1/1), `87` (1/1), `98` (1/1), `active_time_zone` (1/1), `activity_tracker_enabled` (1/1), `auto_activity_detect` (1/1), `autosync_min_steps` (1/1), `autosync_min_time` (1/1), `backlight_mode` (1/1), `date_mode` (1/1), `lactate_threshold_autodetect_enabled` (1/1), `mounting_side` (1/1), `move_alert_enabled` (1/1), `time_mode` (1/1), `time_offset` (1/1), `time_zone_offset` (1/1), `utc_offset` (1/1)

### `file_creator` — 1 správ

`software_version` (1/1)

### `file_id` — 1 správ

`garmin_product` (1/1), `manufacturer` (1/1), `product` (1/1), `serial_number` (1/1), `time_created` (1/1), `type` (1/1)

### `session` — 1 správ

`109` (1/1), `138` (1/1), `151` (1/1), `152` (1/1), `178` (1/1), `184` (1/1), `188` (1/1), `212` (1/1), `215` (1/1), `216` (1/1), `81` (1/1), `avg_cadence` (1/1), `avg_fractional_cadence` (1/1), `avg_heart_rate` (1/1), `avg_power` (1/1), `avg_running_cadence` (1/1), `avg_stance_time` (1/1), `avg_step_length` (1/1), `avg_vertical_oscillation` (1/1), `avg_vertical_ratio` (1/1), `enhanced_avg_speed` (1/1), `enhanced_max_speed` (1/1), `event` (1/1), `event_type` (1/1), `first_lap_index` (1/1), `max_cadence` (1/1), `max_fractional_cadence` (1/1), `max_heart_rate` (1/1), `max_power` (1/1), `max_running_cadence` (1/1), `message_index` (1/1), `metabolic_calories` (1/1), `normalized_power` (1/1), `num_laps` (1/1), `sport` (1/1), `sport_profile_name` (1/1), `start_time` (1/1), `sub_sport` (1/1), `timestamp` (1/1), `total_anaerobic_training_effect` (1/1), `total_calories` (1/1), `total_cycles` (1/1), `total_distance` (1/1), `total_elapsed_time` (1/1), `total_strides` (1/1), `total_timer_time` (1/1), `total_training_effect` (1/1), `total_work` (1/1), `training_load_peak` (1/1), `trigger` (1/1)

### `sport` — 1 správ

`10` (1/1), `13` (1/1), `15` (1/1), `5` (1/1), `6` (1/1), `9` (1/1), `name` (1/1), `sport` (1/1), `sub_sport` (1/1)

### `timestamp_correlation` — 1 správ

`local_timestamp` (1/1), `system_timestamp` (1/1), `timestamp` (1/1)

### `training_settings` — 1 správ

`1` (1/1), `106` (1/1), `109` (1/1), `11` (1/1), `110` (1/1), `12` (1/1), `121` (1/1), `124` (1/1), `127` (1/1), `128` (1/1), `129` (1/1), `13` (1/1), `130` (1/1), `14` (1/1), `15` (1/1), `155` (1/1), `156` (1/1), `157` (1/1), `158` (1/1), `160` (1/1), `168` (1/1), `2` (1/1), `24` (1/1), `254` (1/1), `27` (1/1), `3` (1/1), `30` (1/1), `34` (1/1), `4` (1/1), `41` (1/1), `42` (1/1), `46` (1/1), `55` (1/1), `60` (1/1), `62` (1/1), `64` (1/1), `65` (1/1), `7` (1/1), `76` (1/1), `78` (1/1), `8` (1/1), `86` (1/1), `87` (1/1), `93` (1/1), `target_distance` (1/1), `target_speed` (1/1)

### `user_profile` — 1 správ

`24` (1/1), `36` (1/1), `37` (1/1), `41` (1/1), `43` (1/1), `44` (1/1), `45` (1/1), `52` (1/1), `53` (1/1), `54` (1/1), `57` (1/1), `60` (1/1), `61` (1/1), `62` (1/1), `65` (1/1), `66` (1/1), `67` (1/1), `69` (1/1), `70` (1/1), `activity_class` (1/1), `dist_setting` (1/1), `elev_setting` (1/1), `gender` (1/1), `height` (1/1), `height_setting` (1/1), `hr_setting` (1/1), `language` (1/1), `position_setting` (1/1), `resting_heart_rate` (1/1), `sleep_time` (1/1), `speed_setting` (1/1), `temperature_setting` (1/1), `wake_time` (1/1), `weight` (1/1), `weight_setting` (1/1)

### `zones_target` — 1 správ

`10` (1/1), `12` (1/1), `13` (1/1), `254` (1/1), `9` (1/1), `functional_threshold_power` (1/1), `hr_calc_type` (1/1), `pwr_calc_type` (1/1), `threshold_heart_rate` (1/1)

### Nepomenované správy (číselné ID)

| ID správy | Počet | ID polí |
| --- | --- | --- |
| 233 | 3011 | 2 |
| 534 | 3005 | 0, 1, 253 |
| 288 | 3 | 0, 1, 253 |
| 327 | 3 | 0, 1, 2, 3, 4, 5, 6, 253 |
| 394 | 2 | 0, 1, 2, 253 |
| 140 | 1 | 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 43, 44, 45, 46, 48, 51, 52, 53, 54, 55, 56, 57, 58, 59, 62, 63, 64, 65, 66, 67, 82, 83, 84, 85, 253 |
| 432 | 1 | 0, 1, 253 |
| 326 | 1 | 0, 1, 253 |
| 22 | 1 | 0, 1, 2, 4, 5, 6, 16, 253 |
| 141 | 1 | 0, 253 |
| 79 | 1 | 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 25, 26, 33, 34, 35, 36, 37, 38, 39, 40, 44, 47, 253 |
| 545 | 1 | 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 253 |

## `Activities.csv` (zoznam aktivít) — stĺpce

1. Typ aktivity
2. Dátum
3. Obľúbená položka
4. Názov
5. Vzdialenosť
6. Kalórie
7. Čas
8. Priemerný tep
9. Maximálny Srdcový Tep
10. Aeróbny TE
11. Priemerná kadencia behu
12. Maximálna kadencia behu
13. Priemerné tempo
14. Najlepšie tempo
15. Celkové stúpanie
16. Celkové klesanie
17. Priemerná dĺžka kroku
18. Priem. vertikálny pomer
19. Priemerná zvislá oscilácia
20. Priemerná doba kontaktu so zemou
21. Priem. GAP
22. Normalized Power® (NP®)
23. Training Stress Score®
24. Priemerný výkon
25. Maximálny výkon
26. Celkový počet záberov
27. Priemerné skóre Swolf
28. Priemerná frekvencia záberov
29. Kroky
30. Zníženie energetickej rezervy
31. Minimálna teplota
32. Dekompresia
33. Najlepší čas okruhu
34. Počet okruhov
35. Maximálna teplota
36. Čas jazdy
37. Uplynutý čas
38. Min. nadmorská výška
39. Max. nadmorská výška

## CSV jednej aktivity (kolá) — stĺpce

1. Okruhy
2. Čas
3. Kumulatívny čas
4. Vzdialenosť km
5. Priemerné tempo min./km
6. Priem. GAP min./km
7. Priemerný tep údery/min.
8. Maximálny Srdcový Tep údery/min.
9. Celkové stúpanie m
10. Celkové klesanie m
11. Priemerný výkon W
12. Priemerné W/kg
13. Maximálny výkon W
14. Maximálne W/kg
15. Priemerná kadencia behu kroky/min
16. Priemerná doba kontaktu so zemou ms
17. Priem. pomer GCT %
18. Priemerná dĺžka kroku m
19. Priemerná zvislá oscilácia cm
20. Priem. vertikálny pomer %
21. Kalórie Cal
22. Priemerná teplota
23. Najlepšie tempo min./km
24. Maximálna kadencia behu kroky/min
25. Čas jazdy
26. Priemerné tempo pohybu min./km
27. Priemerná strata rýchlosti krokov cm/s
28. Priem. percento straty rýchlosti krokov %
