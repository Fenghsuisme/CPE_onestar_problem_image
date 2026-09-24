---
name: cpe-6-verify-answers
description: Stage 6 of the CPE pipeline. Collect accepted C++ solutions into answer/uva<id>.cpp, prove them AC on ZeroJudge or vjudge (or a brute-force stress test when no judge has the problem), use them to validate the local test data in autofill/done, check the 3-second limit, and write answer/REPORT.md.
disable-model-invocation: true
---

# Stage 6: verify answers and test data

Follow `AGENTS.md`. Tell the user the plan and wait for "開始".

User's workflow: **script → send code to an online judge → get AC → run that code on `autofill/done` →
report which test cases are wrong.** Don't use judge.gai.tw here (that's stage 7).

## Steps

1. **Collect answers.** Fetch public solutions marked Accepted (mainly GitHub `morris821028/UVa`, others as needed)
   into `answer/uva<id>.cpp`. First line: `// Source: <URL>`. Mark every edit with `// modified: <why>`.
   Make them compile on modern judges: `gets` → `fgets` (check newline handling), `main` → `int main`, strip BOMs.
2. **Read each problem** (`images/<id>/`) against its answer: EOF/termination condition, blank lines between cases,
   spacing, edge cases, overflow. Test cases passing isn't enough.
3. **Online judge AC** (user logs in first in the agent's browser; never type their password):
   - **ZeroJudge** (zerojudge.tw): most UVa problems exist. Map UVa id → ZJ id with its search API
     (10018 → c015). Submit C++17 with the page's CSRF token, **≥ 11 s apart** (rate limit).
   - **vjudge**: only works until its Cloudflare Turnstile appears, and it now refuses UVa submissions.
     Don't bypass CAPTCHAs.
   - A WA can be the judge's data: ZJ 275 has no blank line between cases, ZJ 10098 is missing a case
     (forum #26846). Confirm before changing code; keep the UVa/CPE format.
   - Not on any judge (last time 880, 10730, 10920, 10943, 11356): compare against an independent brute force
     on random + edge inputs. Extend `answer/stress_unverified.py`.
4. **Run on local test data**, strict byte comparison (CPE standard: one extra/missing space or newline = wrong):
   ```bash
   python3 answer/run_tests.py            # JSON: OK / WHITESPACE / WRONG / TLE per case
   python3 answer/stress_unverified.py
   ```
   `run_tests.py` compiles with `g++ -std=c++11`, but the user compiles with **clang++ `-std=c++17 -O2`**, so also
   compile and run the cases with clang++ (plus once with `-fsanitize=address,undefined`), and say which compiler each result used.
5. **Triage every failure**: wrong answer or wrong test data? Show a per-case table and let the user choose
   fix vs delete. Don't edit test data on your own.
6. **3-second check.** DMOJ's limit is per case. Time every case; flag anything near 3 s. Use fast I/O if needed
   (11743 went from TLE to 0.4 s with `ios::sync_with_stdio(false); cin.tie(0);`).
7. Also cover older `autofill/done/` folders with no answer file (10004, 280, 439, 524 last time) if the user agrees.

## Report: `answer/REPORT.md` (繁中)

Summary table first, then per problem: source URL, judge + verdict (or "stress only"), local cases passed,
time. Then modifications, test-data problems found (and what the user decided), and limits: be clear it's
not a 100% guarantee (one compiler, limited cases, stress ≠ official AC). Update it after every round of fixes.
Next: `/cpe-7-upload-testdata`.
