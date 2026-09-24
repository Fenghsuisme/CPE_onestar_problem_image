# CPE one-star problem pipeline

Turns CPE / UVa one-star problem PDFs into published problems on the DMOJ judge at judge.gai.tw.
Read `README.md` for the layout and the 8-stage workflow. Each stage has a skill in `.agents/skills/`
(`/cpe-1-fetch-pdfs` … `/cpe-8-publish`); `/cpe-guide` explains the system; `/cpe-next` tells the user which skill to run for their current situation.

## Working rules (apply to every stage)

- **Reply in Traditional Chinese (繁中)** unless the user writes in English and asks for English.
- **Discuss before acting.** Before each stage, list what you understood and what you will do, then wait for
  the user's "ok" / "開始". When the user says "只討論" / "just discuss", change nothing: no files, no git, no websites.
- **One step at a time.** Do only the step asked for. Say what the next step would be; don't start it.
- **Never run git** (add, commit, push, pull, reset, PR) unless the user asks for that exact action.
  Never touch the remote unless asked. The user opens PRs themselves.
- **Nothing becomes public on DMOJ** until the user says "公開". Stop right after publishing.
- **Writing to judge.gai.tw** (upload, submit, edit) needs explicit authorization each time, e.g. "授權，先測 3 題".
  Always pilot 3 problems first; any mismatch → stop and report, don't continue on your own.
- **Credentials:** never type the user's passwords; let them log in. Session cookies live in `~/.dmoj_session`
  (chmod 600) or env vars, never in the repo. Don't bypass CAPTCHAs or rate limits.
- **Delete only with `trash`**, after the user approves the exact paths. Never `rm`.
- **Don't fix what you weren't asked to fix.** If you find a bad test file or data issue, report it and ask.
- **Sub-agents:** if your tool supports them, fan out large batches (e.g. 51 problems) to parallel workers,
  then use separate verifier agents to check their output. Exception: anything that needs the user's logged-in
  browser (uDebug fetching, judge submissions) runs in the main agent; sub-agents can't reach it.
- **End every stage with a report:** what succeeded, what failed, what was tested, what was not, and caveats.
  Be honest about limits; never claim "100% correct" without evidence. Save it in 繁中 as
  `reports/<YYYY-MM-DD>-stage-<N>-<skill>.md` (e.g. `reports/2026-09-24-stage-5-testing-data.md`; add `-2` if it exists),
  following that skill's **Report** section, then give a short summary in chat with the file link.
  Stage 6 also keeps `answer/REPORT.md` up to date. `cpe-guide` and `cpe-next` don't write reports.
- Throwaway helper scripts go in `/tmp/cpe/`, not the repo.
