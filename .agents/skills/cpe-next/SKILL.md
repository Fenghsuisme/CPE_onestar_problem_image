---
name: cpe-next
description: Tells the user which CPE pipeline skill to run next, based on the repo state and their own description of the situation (e.g. /cpe-next 匯入時出現 duplicate). Read-only.
disable-model-invocation: true
argument-hint: "[describe your situation, optional]"
---

# Which skill should I use?

Read-only: never change files, git, or websites. Reply in 繁中 (see `AGENTS.md`).

The user's situation: whatever they wrote along with the request (may be empty).

## 1. Check the repo

```bash
ls pdfs/new | wc -l                         # PDFs waiting to be processed
cat problem_list.md                         # the current batch
python3 - <<'EOF'
import csv
rows = list(csv.DictReader(open("output.csv")))
empty = [r["code"] for r in rows if "### Sample Input\n```text\n\n```" in r["description"]]
print(len(rows), "rows;", len(empty), "with empty samples:", empty[:10])
EOF
ls testing_data/uva_*.md | wc -l; ls autofill/zip_files | wc -l; ls answer
ls reports/                                  # which stages already ran (latest report = latest stage)
git status --short | head -20               # read-only
```

The repo can't show DMOJ state (imported? test data uploaded? public?). If it matters, ask.

## 2. Match the situation

| Situation | Run |
|---|---|
| Starting a new batch; new problems on cpe.mcu.edu.tw/cpelist.php | `/cpe-1-fetch-pdfs` |
| PDFs in `pdfs/new/`, not yet checked against DMOJ | `/cpe-2-dedupe` |
| DMOJ import fails with a duplicate code | `/cpe-2-dedupe` (remove the row), then re-import with Preview |
| PDFs checked, no `images/<id>/` or CSV rows yet | `/cpe-3-build-csv` |
| `output.csv` rows have empty Sample Input/Output, or samples look wrong on DMOJ | `/cpe-4-fill-samples` |
| Samples filled, images not on `main` / not imported | manual: commit → PR → merge to `main` → DMOJ import (Preview first) |
| DMOJ shows broken images | manual: images aren't merged into `main` yet (or wait a few minutes for the raw.githubusercontent.com cache) |
| Batch problems missing from `testing_data/`, `autofill/done/` or `autofill/zip_files/` | `/cpe-5-testing-data` |
| A test case looks wrong / a problem's `.out` misses a blank line | `/cpe-6-verify-answers` (triage), then `/cpe-5-testing-data` to rebuild the zip |
| Missing `answer/uva<id>.cpp`, no current `answer/REPORT.md`, worried about the 3 s limit | `/cpe-6-verify-answers` |
| Zips ready and verified, problems imported, no test data on judge.gai.tw | `/cpe-7-upload-testdata` |
| YAML shows `verilogchecker`, or a submission fails on judge.gai.tw | `/cpe-7-upload-testdata` |
| Everything uploaded and AC, want students to see it | `/cpe-8-publish` (say "公開") |
| New to the repo / "what is this?" | `/cpe-guide` |

If the repo state and the user's description disagree, trust neither blindly: say what you see and ask.

## 3. Answer

Short: where they are (1–2 lines of evidence), **the one skill to run next**, and anything they must do by hand
first (log in, merge, save the cookie). If two stages are both unfinished, name the earlier one.
