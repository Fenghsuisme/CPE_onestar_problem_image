---
name: cpe-1-fetch-pdfs
description: Stage 1 of the CPE pipeline. Download the one-star problem PDFs listed on https://cpe.mcu.edu.tw/cpelist.php into pdfs/new/ and verify each PDF is the problem the list claims.
disable-model-invocation: true
---

# Stage 1: fetch PDFs

Follow the rules in `AGENTS.md`. First tell the user the plan (how many problems the list shows,
where files go) and wait for "ok".

## Steps

1. **Read the list.** Fetch `https://cpe.mcu.edu.tw/cpelist.php`. Parse the table rows: `uva<id>`, title, link.
   Hrefs are **unquoted** (`<a href=https://...>`), so a quoted-href regex finds nothing.
2. **Download.** PDFs are hosted on onlinejudge.org at `/external/<id // 100>/<id>.pdf`
   (e.g. `https://onlinejudge.org/external/122/12289.pdf`).
   `curl -sSL --retry 2 -o pdfs/new/<id>.pdf <url>`, sequentially, named `<id>.pdf` (digits only).
3. **Shallow check.** Every file is `application/pdf` (`file --mime-type`) and > 2 KB; count matches the list.
4. **Deep check (required).** For each PDF, read page-1 text with pymupdf (`import fitz`) and confirm the
   problem number/title matches the list row. The list itself can be wrong: last time the `uva12289`
   row ("One-Two-Three") linked to `11289.pdf` ("Friend or Foe?"). Fix by downloading the correct
   `<id>.pdf` directly, and ask before `trash`-ing the wrong file.
5. **Stop.** Don't dedupe or build anything. That's stage 2 / 3.

Only do what was asked. If the user said "just download", leave existing files in `pdfs/new/` alone.

## Weekly practice sets

When the batch is one weekly practice (problems fixed in `presentations/practice/practice_picks_<date>.md`),
**do not read cpelist**:

- Download only the UVa problems whose PDF is not yet in `pdfs/old/` or `pdfs/new/`, straight from
  `https://onlinejudge.org/external/<id // 100>/<id>.pdf`. Run the shallow and deep checks above.
- A non-UVa problem has no official PDF. Write the statement **in English only, in our own words** (no Chinese
  anywhere, not copied from the source), say what differs from the source problem, and end with a source line
  such as `Adapted from the CSES Problem Set, task 1755.` Build `pdfs/new/<Problem_Name>.pdf` with the previous
  week's `build_statement.py` (`presentations/practice/practice<MMDD>/<problem>/`). Check: one page, fonts
  embedded, no CJK characters, sample equals the reference solution's output. Show the statement to the user;
  it is final only after they agree.
- Problems already on DMOJ keep their existing PDF and are skipped; list them in the report.

## Report

- Count on the list vs downloaded vs verified.
- Any list/link mismatches and how they were resolved (flag them for the PR description too).
- Files removed (with `trash`, approved paths only).
- Next: `/cpe-2-dedupe`.
