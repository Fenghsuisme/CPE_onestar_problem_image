---
name: cpe-guide
description: Beginner guide to the CPE one-star → DMOJ pipeline in this repo. Explains what the system does, the 8 stages and their skills, and inspects the repo to tell the user which stage they are at and what to run next. Use when someone asks how to use this repo/system, what it does, where to start, "what should I do next", or "我現在在哪一步".
---

# CPE pipeline guide

You are onboarding someone who may know nothing about this repo. Reply in 繁中 (see `AGENTS.md`).
Read-only: this skill never changes files, git, or websites.

## 1. Explain the system (short)

This repo turns CPE / UVa one-star problem PDFs into published problems on the DMOJ judge judge.gai.tw.
Read `README.md` and summarize: layout, the 8 stages, which steps the user does by hand
(git merge to `main` + DMOJ import after stage 4; logging in to websites; saving the sessionid cookie).

| # | Skill | One-line purpose |
|---|---|---|
| 1 | `/cpe-1-fetch-pdfs` | download + verify PDFs from cpe.mcu.edu.tw/cpelist.php |
| 2 | `/cpe-2-dedupe` | drop problems already on DMOJ |
| 3 | `/cpe-3-build-csv` | PDFs → images + `output.csv` |
| 4 | `/cpe-4-fill-samples` | exact Sample I/O into `output.csv`, then merge + import |
| 5 | `/cpe-5-testing-data` | uDebug → `testing_data/` → `.in/.out` + zips |
| 6 | `/cpe-6-verify-answers` | AC answers, online-judge + local verification, 3 s check |
| 7 | `/cpe-7-upload-testdata` | upload zips to judge.gai.tw, check YAML, submit answers |
| 8 | `/cpe-8-publish` | make public, only on "公開" |
| ? | `/cpe-next` | not sure what to run? it checks your situation and names the skill |

Mention the house rules from `AGENTS.md` in one or two lines: the agent asks before each stage,
never runs git or publishes on its own, deletes only with `trash`.

## 2. Where are they, and what next?

Follow `.agents/skills/cpe-next/SKILL.md` (repo check + situation table) and answer as it says.
Tell the user they can run `/cpe-next` themselves any time, optionally with a description:
`/cpe-next 匯入時出現 duplicate`.
