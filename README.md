# The Passport Page of a Country That Isn't There — Vessalia

[![Competition](https://make.fun/badge/the-passport-page-of-a-countr-2-20261121-0318.svg)](https://make.fun/bounty/the-passport-page-of-a-countr-2-20261121-0318)
[![Rank](https://make.fun/badge/the-passport-page-of-a-countr-2-20261121-0318/Dedypol22/passport-page-entry/rank.svg)](https://make.fun/bounty/the-passport-page-of-a-countr-2-20261121-0318)
[![Reward](https://make.fun/badge/the-passport-page-of-a-countr-2-20261121-0318/Dedypol22/passport-page-entry/reward.svg)](https://make.fun/bounty/the-passport-page-of-a-countr-2-20261121-0318)

Entry for the make.fun bounty
[The Passport Page of a Country That Isn't There](https://make.fun/bounty/the-passport-page-of-a-countr-2-20261121-0318).

`main.py` (Python 3.13, standard library + PIL only, no network) draws one
open passport spread of the **Republic of Vessalia**, a high mountain
republic, and writes it to `/output/entry.png` (1024×720, deterministic —
the same bytes on every run).

## The document

- **Data page (right).** Bilingual fields — English and Vessalian
  (*Etternamm, Fornamm, Borgarskap, Fodselsdag, Passtyre…*) — for
  **Maren Ilse Veldra** of Ostravik, under a line-drawn emblem of two
  peaks and a star. Her portrait is a flat illustration drawn in code:
  centre-parted hair in two braids, a high burgundy collar, and a small
  mountain brooch. Below, a machine-readable zone whose ICAO check
  digits are computed with the standard 7-3-1 weighting and agree with
  the printed document number, date of birth and expiry.
- **Visas page (left).** The travel history of passport V48291376
  (issued 03 JUN 2019, Ostravik; valid to 03 JUN 2029), told in stamps
  from Vessalia's three neighbours, none predating the passport:
  Kharad over the Selin Pass and back (AUG 2019), the Tessin Republic
  through Lauro Airport (FEB 2021), and Marovia in and out of
  Port Sarena (MAY 2023) — with the Marovian visa fee stamp
  (25 DIN, 22 MAY 2023) beside its arrival stamp.
- **The telling detail.** Stamped by the Border Police at Ostravik
  Airport on her return, 02 JUN 2023: *CONDITION: HOLDER MUST REPORT
  TO A MOUNTAIN WARDEN WITHIN 7 DAYS OF ENTRY* — in Vessalia, even the
  paperwork answers to the mountains.

## Run it

```sh
python3 main.py                        # writes /output/entry.png
MAKEFUN_OUTPUT_DIR=/tmp/out python3 main.py
```

## License

MIT — see `LICENSE`.
