---
name: cpe-7-upload-testdata
description: Stage 7 of the CPE pipeline. Upload autofill/zip_files/uva<id>.zip as test data to each problem on judge.gai.tw (DMOJ), set every case to the standard checker, verify via View YAML, then submit the verified answers to confirm AC. Pilots 3 problems first.
disable-model-invocation: true
---

# Stage 7: upload test data to judge.gai.tw

Follow `AGENTS.md`. This writes to an external site. Needs the user's explicit
**"授權，先測 3 題"** before any upload. Problems stay **hidden** (`is_public = FALSE`) throughout.

## Prerequisites (user does these)

- Problems already imported (stage 4 hand-off). Zips exist in `autofill/zip_files/`.
- Session cookie saved without echoing (DevTools → Application → Cookies → `sessionid`):
  `read -s SID && printf %s "$SID" > ~/.dmoj_session && chmod 600 ~/.dmoj_session; unset SID`
  (`pbpaste >` failed last time: the clipboard held the command). Never commit or print it.

## Manual form (what the script must reproduce)

`https://judge.gai.tw/problem/uva<id>/test_data`: upload zip → Submit → **Fill testcases** (自動填入測資)
pairs `i.in` → `i.out` → each row: type **Case**, **Points 1**, Pretest off →
**Checker: `standard`** on **every row**. Blank = `verilogchecker` (this site's default), and the per-case checker
overrides the top-level one → Submit → **View YAML** (查看 YAML): `archive: uva<id>.zip`, all `test_cases`,
no `verilogchecker` anywhere. You can compare against an existing problem's YAML (e.g. `uva280`).

## Script (`/tmp/cpe/dmoj_data.py`, stdlib only, not in the repo)

Per problem: GET the test_data page (CSRF token) → POST zip → POST rows (above) → GET YAML → compare with expected
(zip name, case count, filenames, `standard`, points). **Any mismatch → stop and report.** Skip problems that
already have test data (never overwrite).
Pass problem ids as **separate arguments**. Last time zsh passed all 48 ids as one string and nothing uploaded.

## Order

1. Show the plan; wait for "授權，先測 3 題".
2. Pilot 3 problems. The user checks them on the site. All 3 must be perfect, else stop and report.
3. Rest of the batch after the user says go.
4. Re-check every problem's YAML.
5. Submit each `answer/uva<id>.cpp` on judge.gai.tw (3 first, then the rest). Every problem must be **AC**; note
   submission ids and the slowest time.

## Report

Uploaded / skipped / failed per problem, YAML check result, AC list with submission ids.
Remind the user to log out of judge.gai.tw to invalidate the cookie, and ask before `trash`-ing
`~/.dmoj_session`. Next: `/cpe-8-publish`, only when the user says "公開".
