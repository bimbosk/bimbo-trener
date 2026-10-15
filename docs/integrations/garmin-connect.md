# Garmin Connect

Cloud Garminu, do ktorého sa moje hodinky synchronizujú cez telefón. Pre projekt je to
zdroj FIT súborov a jediná externá služba. Ako skript sťahuje, vlastní
[sťahovanie](../coach/garmin-sync.md); prečo neoficiálnou cestou,
[prieskum](../evidence/2026-10-15-garmin-research.md).

## Účet a synchronizácia

- Používam vlastný účet Garmin Connect; hodinky nahrávajú aktivity cez aplikáciu
  v telefóne. Typicky do minút, pri úspore batérie aj neskôr; potiahnutie nadol
  v aplikácii synchronizáciu vynúti.
- Hodinky Venu 4, 45 mm; váha Index S2; cyklopočítač Edge 1040
  ([zariadenia](../evidence/2026-10-15-devices-and-health-data.md)).

## Prihlásenie knižnicou `python-garminconnect`

- Neoficiálny klient webových služieb Garminu. Prihlásenie mobilným SSO s e-mailom, heslom
  a MFA kódom; výsledkom sú OAuth tokeny, ktoré knižnica obnovuje sama (prístupový token
  asi 18 h, obnovovací asi 30 dní; po dlhšej nečinnosti nové prihlásenie).
- Token umožňuje aj zápisové operácie na účte; chráni sa ako heslo
  ([bezpečnosť](../coach/security.md)). Ostáva v configu aplikácie na každom PC, kde sa
  sťahuje.
- Predvolená stratégia prihlasovania používa `curl_cffi` na napodobnenie prehliadača;
  nevypína sa.

## Limity a blokácie (stav k 15. 10. 2026)

| Jav | Čo to znamená | Reakcia projektu |
| --- | --- | --- |
| 429 pri prihlásení | Garmin limituje podľa odtlačku klienta a účtu, nie iba IP; môže trvať hodiny až 2 dni | cooldown, žiadne opakovanie, ručný export medzitým |
| 403 pri platnom tokene | Cloudflare blokuje klienta alebo sieť (VPN, datacentrá) | zalogovať, skončiť 75, neobchádzať |
| zmena prihlasovania Garminom | knižnica prestane fungovať do vydania opravy | ručný export; upgrade knižnice vedome |
| `privacyProtected` pri profile | knižnica to hlási ako chybu prihlásenia | skontrolovať nastavenia súkromia účtu |

## Čo sa z Garmin Connect berie

Všetky aktivity s originálnym FIT súborom a denné zdravotné dáta z Venu 4 a Index S2
([rozhodnutie](../decisions/2026-10-15-collect-everything.md), [zariadenia](../evidence/2026-10-15-devices-and-health-data.md)).

## Ručné cesty

Export jednej aktivity z webu, kopírovanie z hodiniek káblom a hromadný export účtu sú
opísané v [sťahovaní](../coach/garmin-sync.md), Záložné cesty. Mobilná aplikácia export
nevie.

## Podmienky používania

Knižnica používa súkromné rozhranie Garminu; projekt ho používa iba pre môj vlastný
účet, iba na čítanie, s nízkou frekvenciou a bez obchádzania ochrán. Garmin môže prístup
kedykoľvek zmeniť; projekt to nepovažuje za chybu, ale za riziko s pripravenou záložnou
cestou.
