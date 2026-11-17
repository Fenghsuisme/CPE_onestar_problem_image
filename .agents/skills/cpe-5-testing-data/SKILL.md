---
name: cpe-5-testing-data
description: Stage 5 of the CPE pipeline. Build the test data for each problem. Two modes - bulk CPE batches take 1-7 complete cases from uDebug; weekly practice sets get 15 self-generated, verified cases per problem with uDebug as a cross-check. Then build .in/.out files and zips.
disable-model-invocation: true
---

# Stage 5: testing data

Follow `AGENTS.md`. Tell the user the plan and wait for "ok". Rules are in `testing_data/README.md`.

## Which mode

- **Bulk mode** (a large CPE batch, e.g. 51 problems from cpelist): sections "Rules", A, B, C below.
  Cases come from uDebug.
- **Weekly practice mode** (the 7 + 1 problems of one weekly practice, picked in
  `presentations/practice/practice_picks_<date>.md`): section W below. Cases are generated here and verified;
  uDebug is a reference, not the source. Use this mode whenever the user asks for a fixed number of cases,
  edge coverage, or values close to the limits.

If it is not clear which one the user wants, ask.

## W. Weekly practice mode

The user's requirement (repeated on 2026-10-20, 10-28, 11-10, 11-17): **15 cases per problem**, covering nearly
all edge conditions, with values **very close to the limits the statement states**; the solution and the data
must both be shown correct.

### W1. Agree on the limits first

Read each official statement. Where it gives no limit (number of lines, string length, number of cases),
propose a cap and **wait for the user's "ok"**. For such unstated limits keep the data at **ordinary sizes**
(user, 2026-11-17: 「沒有範圍的…不要到太極限，一般般的測試就好」): students cannot know how large a buffer to
make when the statement is silent. E.g. string length up to 1000 with most cases under ~100 characters. Push
values close to the limit only for limits the statement itself gives. Do not add our own caps to the problem
statement unless the user asks.
List inputs the statement excludes or leaves undefined (e.g. 10222 keys with no key two to the left, 401's `0`)
and keep them **out** of the data. Ask whether new cases **replace** or **extend** existing judge cases.

### W2. Build, one worker per problem

Work in `presentations/practice/practice<MMDD>/<problem>/` (git-ignored). Each problem ends up with:

- `final/1.in … 15.in` and `.out`. Case 1 is the official sample, byte for byte.
- `validate.py`: checks every `.in` against the statement and the agreed caps (ranges, counts, terminator,
  allowed characters, no stray whitespace, LF only, one final newline, no BOM).
- `gen.py`: fixed seeds, so `final/` can be rebuilt byte-identically.
- `sol.*` (reference) plus **a second, independently written solution** using a different method
  (brute force where possible). Every `.out` must be identical for both.
- `mutants/`: a dozen or so plausible wrong solutions (off-by-one, wrong buffer size, missing reset, wrong
  tie-break, …). Each must fail at least one of the 15 cases; one that survives means a case is missing.
- `check.py`: one command that re-runs validator, both solutions and the mutants.
- `REPORT.md`: an **edge ↔ case table**, a **min/max table for every variable** in the statement, a few
  hand-derived small cases, and any edge left uncovered with the reason.

Every variable is pushed to its maximum in at least one case, not only the "main" one. Include a timing case:
the slowest solution a student would reasonably write must still pass the time limit.

### W3. uDebug as a reference

For UVa problems, in the user's logged-in browser (main agent only; see A.1 for what works):

- Fetch the listed inputs and their **Accepted Output**. Drop incomplete fetches, as in bulk mode.
- Run the reference solution on every uDebug input that satisfies the statement and the agreed caps. It must
  match the Accepted Output byte for byte. A mismatch is investigated on both sides and reported; never edit
  data silently.
- uDebug inputs often **break the statement** (out-of-range values, wrong counts). Run them through
  `validate.py`; invalid ones are not used and are listed in the report.
- If a uDebug input shows an edge our 15 cases lack, add a case for it (a valid uDebug input may be taken
  as one of the 15, with its Accepted Output also confirmed by both solutions).
- Use it to settle conventions the statement leaves open, and say so in the report.

No uDebug for non-UVa problems. If the user cannot log in, skip this step and say it was skipped.

### W4. Verify independently

- Separate verifier agents: each reads only the statement first, writes its own solution and input checker,
  compares all 15 outputs, then measures the real min/max of each variable and tries a few more wrong solutions.
- Main agent: re-run every `check.py`, rebuild `final/` and confirm the hashes did not change.
- Run the solutions under ASan/UBSan on all inputs.
- When solution and data disagree, look at both sides and let the user decide.

### W5. Install only when approved

`final/` stays in `presentations/` until the user approves installing. Then follow section C: copy to
`autofill/done/<name>/` byte for byte and build the zip. Existing folders from older batches are backed up to
`/tmp/cpe/` first and replaced only with the user's "ok". For weekly problems also write
`testing_data/uva_<id>.md` only if the user asks for it.

### W report

Per problem: cases, `check.py` result, mutants caught, verifier result, slowest reasonable solution on the
largest case, file sizes. The min/max table. uDebug: inputs fetched, valid, matched, dropped (why).
Caps chosen by us and whether the user approved them. Decisions still open. Not done / not tested.

## Rules (bulk mode)

- 1–7 cases per problem. Input = uDebug "Input"; Output = uDebug **Accepted Output**
  (press **Get Accepted Output**).
- **Only complete cases.** A fetch that failed, timed out, or has empty/partial Accepted Output is **dropped**,
  never written: "抓取沒成功…沒關係，但是不要把它放進去". Every case must fully test a program.
- A problem with zero complete cases gets no file. List it in the report.

## A. Fetch → `testing_data/uva_<id>.md`

1. uDebug is behind **Cloudflare**: `curl`, API calls from outside, and subagents all get 403.
   The uDebug API with Basic auth also failed (401). What worked: the **user's logged-in browser session** (the agent's in-app/controlled browser)
   on uDebug's own pages, reading the input list and submitting the "Get Accepted Output" form from that tab.
   Ask the user to log in there if needed.
2. Take up to 7 inputs per problem, most-voted first. Save raw JSON to `/tmp/udebug/<id>.json`.
3. Write the md exactly like `testing_data/uva_10010.md`:
   `# Testing Data for UVA <id>`, then `## Test case N` with `**Input**:` and `**Output**:` in ```` ```txt ```` blocks.
   Convert `\r\n` → `\n`; keep every other byte (trailing spaces, blank lines).
4. Some Accepted-Output submissions get blocked by Cloudflare (673: inputs with many parentheses). Drop those cases.

## B. Verify the md files

- Format check: 1–7 sequential `## Test case` headings, non-empty Input/Output.
- Re-fetch independently into a separate folder and byte-compare (catches truncation).
- Separate verifier agents solve each problem and compare against the Accepted Output.

## C. Build `.in/.out` + zips

- `autofill/done/uva<id>/1.in`, `1.out`, … from the md. **Don't** use `fill.py`'s trailing-blank-line
  stripping: it broke 10098, 10800, 275, 706 (required final blank line) and 673 (input declared 8 cases, 5 left).
  The `.out` must equal the Accepted Output byte-for-byte.
- Zip: `autofill/zip_files/uva<id>.zip`, files **flat at the zip root**, sorted names, stored
  (Python `zipfile`, like `fill.py` / existing `uva280.zip`).
- Never overwrite an existing `autofill/done/uva<id>/` from an older batch (e.g. 10004, 280, 439, 524) without asking.
- Check: each zip's contents are byte-identical to its folder and the md.
- Invalid cases (input violates the statement's constraints, e.g. 913 with even N): report and ask; `trash` only when approved.

## Report

Per problem: cases fetched / kept / dropped (why). Totals. Anything that needs the user's decision.
Next: `/cpe-6-verify-answers`.
