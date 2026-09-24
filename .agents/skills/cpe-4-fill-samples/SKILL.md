---
name: cpe-4-fill-samples
description: Stage 4 of the CPE pipeline. Fill the empty Sample Input / Sample Output blocks in output.csv with an exact copy of each problem's samples (whitespace, blank lines, trailing spaces included), then hand off the merge-to-main and DMOJ import to the user.
disable-model-invocation: true
---

# Stage 4: fill Sample Input / Output exactly

Follow `AGENTS.md`. The user's requirement: samples must be **一模一樣**, identical to the problem statement,
**不能有任何差錯**. Students see these on DMOJ. Before starting, list your understanding and wait for "ok".

## Steps

1. **Back up** `output.csv` to `/tmp/cpe/`.
2. **Extract** from the PDF in `pdfs/old/<id>.pdf` (exact characters, no 0/O or 1/l misreads), and
   cross-check against `images/<id>/*.png` for layout. Plain `get_text()` is **not** enough:
   - it drops blank lines between sample cases (10010, 10098, 10258);
   - it loses samples that continue onto the next page (10010);
   - two-column layouts can interleave Input and Output.
   Rebuild lines from pymupdf word coordinates (`page.get_text("words")`): group by y, a gap of about
   two line pitches (~13.5 pt pitch) = one blank line, and use the page's own left margin for indentation.
3. **Keep what the problem requires**: trailing spaces (706), blank lines between cases (275, 10098),
   and the exact end-of-output shape. If the PDF's sample conflicts with the statement's output rules, reason out the
   correct output from the statement and flag it to the user.
4. **Pilot 5 problems first.** Show them (input/output as code blocks) and wait for "ok".
5. **Do the rest** with the same extractor once it reproduces the 5 approved pilots exactly (last time 46/52
   came out clean; 6 needed hand inspection). Then separate verifier agents compare each result against the images,
   focusing on flagged rows (multi-page, two-column, blank lines). Loop check → fix until clean.
   After 3 failed attempts on a problem, stop and list it.
6. **Write** only via Python's `csv` module; replace just the two empty ```` ```text ```` blocks per row.
   Re-parse afterwards: same row count, same columns, every other field byte-identical.

## Report

- Problems filled, problems needing manual review (why), pilot corrections.
- Then tell the user their manual steps (don't run them):
  1. Commit `images/` + `output.csv`, open a PR to `main` (they open it), get it merged. Mention any PDF-link
     judgment calls from stage 1 in the PR description.
  2. After the merge (raw.githubusercontent.com may take a few minutes), import `output.csv` in DMOJ admin.
     **Preview first**; the import stops at the first duplicate code.
- Next: `/cpe-5-testing-data`.
