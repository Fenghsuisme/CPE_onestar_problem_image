---
name: cpe-5-testing-data
description: Stage 5 of the CPE pipeline. Fetch test cases from uDebug (Input + Accepted Output) into testing_data/uva_<id>.md, then turn them into autofill/done/uva<id>/N.in/N.out and flat zips in autofill/zip_files/.
disable-model-invocation: true
---

# Stage 5: testing data

Follow `AGENTS.md`. Tell the user the plan and wait for "ok". Rules are in `testing_data/README.md`.

## Rules

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
