# Guide

This repo turns CPE / UVa one-star problem PDFs into a **DMOJ-importable CSV**, and hosts the
problem images so DMOJ can display them. It also has a small helper for typing test cases.

Two independent tools:

| Tool | What it does |
|---|---|
| `build_csv.py` | PDF → PNG → `output.csv` (DMOJ problem import file) |
| `autofill/fill.py` | Interactively type `1.in` / `1.out` / `2.in` … and zip them into a DMOJ test-data archive |

---

## Layout

```
pdfs/new/      ← drop new problem PDFs here
pdfs/old/      ← build_csv.py moves each PDF here after processing
images/<name>/ ← generated PNGs, served to DMOJ via GitHub raw URLs
output.csv     ← the file you import into DMOJ
autofill/      ← fill.py, done/ (finished cases), zip_files/ (finished zips)
```

---

## Setup

Python 3.10+ and one dependency:

```bash
pip install -r requirements.txt
```

Always run the scripts from the repo root — all paths are relative.

---

## 1. Making problems: `build_csv.py`

Put the problem PDFs in `pdfs/new/`. The **filename becomes the problem identity**, so name it carefully:

- `10038.pdf` → digits only → treated as a UVa problem
- `Even_or_Odd.pdf` → treated as a self-written problem

Then run:

```bash
python3 build_csv.py                # everything in pdfs/new/
python3 build_csv.py 10038          # one problem
python3 build_csv.py 10038 524 439  # several
```

What happens for each PDF:

1. Every page is rendered to PNG at 150 dpi → `images/<name>/<name>_p1.png`, `_p2.png`, …
   (a PNG that already exists is skipped, so re-running is safe)
2. The PDF is moved to `pdfs/old/`
3. A CSV row is built and written to `output.csv`

Naming rules it applies:

| PDF name | DMOJ `code` | DMOJ `name` |
|---|---|---|
| `10038.pdf` | `uva10038` | `[NUKC]uva_10038` |
| `Even_or_Odd.pdf` | `evenorodd` | `[NUKC]Even_or_Odd` |

Defaults baked into each row: group `NUK`, type `CPP`, 3 s / 256 MB, 1 point, C and C++ only,
`is_public = FALSE`, authors `Feng,A1115514,Ting`. Change them in the 設定區 block at the top of
`build_csv.py` if you need different values.

The generated description is the problem images plus **empty** `### Sample Input` /
`### Sample Output` code blocks — fill those in by hand in DMOJ (or in the CSV) after importing.

### ⚠️ Two things that will bite you

- **`output.csv` is overwritten every run**, not appended. If you need the previous batch, copy it
  somewhere before running again.
- **Push the images to GitHub *before* importing the CSV.** The descriptions point at
  `raw.githubusercontent.com/Fenghsuisme/CPE_onestar_problem_image/main/images/...`, so DMOJ shows
  broken images until the PNGs are on `main`:

  ```bash
  git add images output.csv
  git commit -m "add problem images"
  git push
  ```

Then in DMOJ: import `output.csv`.

---

## 2. Making test data: `autofill/fill.py`

```bash
cd autofill
python3 fill.py Even_or_Odd
```

It loops, opening `nano` for `1.in`, then `1.out`, then `2.in`, `2.out`, … Type the case, save with
`Ctrl+O` `Enter`, exit with `Ctrl+X`. Trailing blank lines are stripped automatically (DMOJ is picky
about those).

After each `.out` it asks `繼續生成下一組？`:

- `y` → next pair
- anything else → stops, zips the cases into `autofill/<folder>.zip`, and moves the working folder
  to `autofill/done/<folder>`

The zip lands directly in `autofill/`; finished ones are kept in `autofill/zip_files/`, so move it
there yourself when you're done.

Upload the zip as the problem's test data in DMOJ, then set the input/output file patterns
(`*.in` / `*.out`) there.

---

## Typical end-to-end run

1. `cp ~/Downloads/10038.pdf pdfs/new/`
2. `python3 build_csv.py 10038` → PNGs in `images/10038/`, row in `output.csv`
3. `git add . && git commit -m "add 10038" && git push`
4. DMOJ → import `output.csv`
5. `cd autofill && python3 fill.py 10038` → type cases → `10038.zip`
6. DMOJ → problem `uva10038` → upload `10038.zip` as test data
7. Paste the sample input/output into the description, set the problem public
