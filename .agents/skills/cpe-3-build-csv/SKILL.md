---
name: cpe-3-build-csv
description: Stage 3 of the CPE pipeline. Run build_csv.py to render the PDFs in pdfs/new/ into images/<id>/ PNGs and write the DMOJ import file output.csv (all problems hidden).
disable-model-invocation: true
---

# Stage 3: build images + output.csv

Follow `AGENTS.md`. Tell the user the plan (which ids) and wait for "ok".

## Steps

1. **Back up** `output.csv` to `/tmp/cpe/output.before_build.csv`. `build_csv.py` **overwrites** it every run.
2. **Check** `pdfs/new/` only holds this batch (compare with `problem_list.md`). If old or duplicate PDFs are
   still there, pass explicit ids instead of running on everything:
   ```bash
   python3 build_csv.py                 # all of pdfs/new/
   python3 build_csv.py 10010 10018     # only these
   ```
3. **Run** it. Per PDF: PNGs at 150 dpi in `images/<id>/<id>_p1.png…`, PDF moved to `pdfs/old/`, CSV row written.
   Needs `pip install -r requirements.txt` (pymupdf).
4. **Verify**
   - Row count = batch size; codes `uva<id>`, names `[NUKC]uva_<id>`.
   - Every row `is_public = FALSE`.
   - Every image URL in `description` exists as a local file under `images/`.
   - Parse with the `csv` module (never hand-edit; descriptions contain newlines and quotes).

## Report

- Rows written, images created, PDFs moved.
- Samples are still **empty**. Next: `/cpe-4-fill-samples`.
- Remind the user: image URLs point at `raw.githubusercontent.com/Fenghsuisme/CPE_onestar_problem_image/main/images/...`,
  so the images must be **merged into `main`** before importing into DMOJ. That's their git step, after stage 4.
