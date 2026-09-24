---
name: cpe-2-dedupe
description: Stage 2 of the CPE pipeline. Find problems in the new batch that already exist on the DMOJ judge (judge.gai.tw) or in pdfs/old, remove them from the batch, and write problem_list.md.
disable-model-invocation: true
---

# Stage 2: remove problems already on DMOJ

Follow `AGENTS.md`. Tell the user the plan and wait for "ok". Never touch git here.

Why: DMOJ's CSV import aborts on the **first duplicate code** (last time `uva272`), so duplicates must go
before stage 3 / import.

## Steps

1. **Get the existing list.** Ask the user for it: screenshots of the DMOJ problem group page(s)
   ("包含的題目"), or let them log in to judge.gai.tw in the agent's browser so you can read the list.
   Also check `pdfs/old/` and `images/` for ids from earlier batches.
2. **Match two ways**, by number and by title (read the PDF title with pymupdf). DMOJ labels can be wrong:
   "[UVa 10050] Vito's family" is really 10041.
3. **Show the duplicate list and wait for approval.**
4. **Remove.** Before stage 3: `trash` the duplicate PDFs from `pdfs/new/` (approved paths only).
   After stage 3: remove the rows from `output.csv` with Python's `csv` module (back it up to `/tmp/cpe/` first),
   then re-read the file and confirm the row count and that every other row is unchanged.
   Leave `images/<id>/` and `pdfs/old/<id>.pdf` alone unless asked.
5. **Write `problem_list.md`**: one bullet per remaining problem, `- uva 10010`, in batch order.

## Report

- Existing problems checked (how many, which groups; say that groups you couldn't see weren't checked).
- Duplicates found and removed; remaining count.
- Reminder: use DMOJ import **Preview** later to catch anything outside the checked groups.
- Next: `/cpe-3-build-csv` (or `/cpe-4-fill-samples` if the CSV already exists).
