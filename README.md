# CPE one-star problem image

This repo turns CPE / UVa **one-star** problem PDFs into problems on our DMOJ judge
(**judge.gai.tw**): problem images + a DMOJ-importable `output.csv`, exact sample I/O,
test data zips, verified answers, and finally publishing.

New here? Open Claude Code (or Codex, Cursor, or any agent that reads `AGENTS.md`) in this folder and run **`/cpe-guide`**
(in other agents: ask it to use the `cpe-guide` skill). It explains the system
and tells you which stage you're at.
Not sure what to do next? Type **`/cpe-next`** (optionally describe what happened, e.g.
`/cpe-next 匯入時出現 duplicate`) and it names the skill to run.

---

## Layout

```
pdfs/new/              ← new problem PDFs go here
pdfs/old/              ← build_csv.py moves each PDF here after processing
images/<id>/           ← generated PNGs, served to DMOJ via GitHub raw URLs (main branch)
output.csv             ← the file you import into DMOJ
problem_list.md        ← the problems in the current batch (`- uva 10010`)
testing_data/          ← uDebug test cases, one uva_<id>.md per problem (see its README.md)
autofill/fill.py       ← type test cases by hand and zip them
autofill/done/uva<id>/ ← 1.in, 1.out, 2.in, … per problem
autofill/zip_files/    ← uva<id>.zip, the test-data archive you upload to DMOJ
answer/                ← verified solutions uva<id>.cpp, run_tests.py, stress_unverified.py, reports
reports/               ← one report per stage run: <date>-stage-<N>-<skill>.md
.agents/skills/        ← the skills for each stage (any agent; edit these)
.claude/skills/        ← symlinks to .agents/skills/ for Claude Code
AGENTS.md              ← rules every agent follows in this repo
CLAUDE.md              ← imports AGENTS.md + Claude-only notes
```

## Setup

Python 3.10+ and one dependency (`clang++` / `g++` for checking answers):

```bash
pip install -r requirements.txt
```

Always run scripts from the repo root. All paths are relative.

---

## The workflow

| # | Skill | What happens | Output |
|---|---|---|---|
| 1 | `/cpe-1-fetch-pdfs` | Download PDFs from cpe.mcu.edu.tw/cpelist.php, check each one is the right problem | `pdfs/new/<id>.pdf` |
| 2 | `/cpe-2-dedupe` | Drop problems already on DMOJ | trimmed `pdfs/new/`, `problem_list.md` |
| 3 | `/cpe-3-build-csv` | PDFs → PNGs + CSV rows (all hidden) | `images/<id>/`, `output.csv` |
| 4 | `/cpe-4-fill-samples` | Copy Sample Input/Output exactly into `output.csv`, then you merge to main and import | filled `output.csv` |
| 5 | `/cpe-5-testing-data` | Fetch uDebug cases, build `.in/.out` and zips | `testing_data/`, `autofill/done/`, `autofill/zip_files/` |
| 6 | `/cpe-6-verify-answers` | Get AC solutions, verify on ZeroJudge / vjudge, run them on our test data, 3 s check | `answer/`, `answer/REPORT.md` |
| 7 | `/cpe-7-upload-testdata` | Upload zips to judge.gai.tw (3 first), check YAML, submit answers | test data on DMOJ |
| 8 | `/cpe-8-publish` | Make the problems public, only when you say "公開" | public problems |

Not sure which one? `/cpe-next` checks the repo and your situation and names the skill.
Every stage starts by telling you its plan and waiting for your "ok", and ends with a report saved in `reports/`.
The agent never runs git or publishes anything unless you ask (see `AGENTS.md`).

**Your manual steps** (the agent tells you when):

- After stage 4: commit `images/` + `output.csv`, open a PR, get it **merged into `main`**, then import
  `output.csv` in DMOJ (use **Preview** first). The CSV's image links point at `main`, so importing before the
  merge shows broken images.
- Stage 5 / 6 / 7: log in to uDebug, ZeroJudge / vjudge, and judge.gai.tw yourself in the agent's browser (Synara's in-app browser for Claude).
- Stage 7: save your judge.gai.tw `sessionid` cookie:
  `read -s SID && printf %s "$SID" > ~/.dmoj_session && chmod 600 ~/.dmoj_session; unset SID`.
  Log out of judge.gai.tw afterwards to invalidate it.

---

## Scripts

### `build_csv.py`: PDF → PNG → `output.csv`

The **filename is the problem identity**: `10038.pdf` → UVa problem, `Even_or_Odd.pdf` → self-written problem.

```bash
python3 build_csv.py                # everything in pdfs/new/
python3 build_csv.py 10038 524 439  # only these
```

For each PDF: pages → `images/<name>/<name>_p1.png` … at 150 dpi (existing PNGs are skipped), PDF moved to
`pdfs/old/`, CSV row written.

| PDF name | DMOJ `code` | DMOJ `name` |
|---|---|---|
| `10038.pdf` | `uva10038` | `[NUKC]uva_10038` |
| `Even_or_Odd.pdf` | `evenorodd` | `[NUKC]Even_or_Odd` |

Defaults (設定區 at the top of the script): group `NUK`, type `CPP`, 3 s / 256 MB, 1 point, C and C++ only,
`is_public = FALSE`, authors `Feng,A1115514,Ting`. The description is the images plus **empty**
Sample Input / Sample Output blocks (stage 4 fills them).

⚠️ **`output.csv` is overwritten every run**, not appended. Back it up first.

### `autofill/fill.py`: type test cases by hand

```bash
cd autofill && python3 fill.py 10038
```

Opens `nano` for `1.in`, `1.out`, `2.in`, … and asks `繼續生成下一組？` after each `.out`
(`y` = next pair). Then it zips the cases into `autofill/<folder>.zip` and moves the folder to `autofill/done/`.
⚠️ It strips trailing blank lines from `.out`, which breaks problems whose output ends with a required
blank line (e.g. 10098, 10800, 275, 706). Stage 5 builds files without this step.

### `answer/run_tests.py` and `answer/stress_unverified.py`

```bash
python3 answer/run_tests.py            # all answers vs autofill/done, JSON: OK / WHITESPACE / WRONG / TLE
python3 answer/run_tests.py 10010 392  # only these
python3 answer/stress_unverified.py    # brute-force self-check for answers no online judge has
```

---

## Known traps

- The CPE list page can link the wrong PDF (last time `uva12289` linked to `11289.pdf`). Stage 1 checks every title.
- DMOJ's CSV import stops at the first duplicate problem code. Dedupe first, and always Preview.
- judge.gai.tw defaults the checker to `verilogchecker`. Set **`standard` on every test case row**, not just the top.
- uDebug is behind Cloudflare. Only a real logged-in browser session (e.g. Synara's in-app browser) gets through.
- vjudge blocks UVa submissions. ZeroJudge has most UVa problems. Problems neither judge has
  are checked with a brute-force stress test.
