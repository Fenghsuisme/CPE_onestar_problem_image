---
name: cpe-8-publish
description: Stage 8 of the CPE pipeline. Make the batch's problems public on judge.gai.tw, only after the user explicitly says "公開", after re-checking test data and AC for every problem. Stops immediately afterwards.
disable-model-invocation: true
---

# Stage 8: publish (公開)

Follow `AGENTS.md`. Run only after the user explicitly says **"公開" / "幫我公開"**. Invoking this skill alone
isn't enough; confirm the problem list with them first.

## Pre-checks (all must pass, otherwise report and stop)

1. The batch = `problem_list.md`. Find each problem's internal DMOJ id in admin. Exactly one match each,
   currently **not** public.
2. Every problem's View YAML is correct (stage 7 rules: all cases, `standard` everywhere).
3. Every problem has an **AC** submission of `answer/uva<id>.cpp`.
4. Show the list + check results; wait for the final "ok".

## Publish

In DMOJ admin's problem list, select **only these problems** and run the bulk action
**"把題目標記為公開"** (mark problems as public). Touch nothing else.

## Verify

- The site says "已成功將 N 個題目標記為公開" with the right N.
- Re-query: none of the batch is still private.
- Open two problems while logged out (or in a private window) and confirm they're visible.

## Then stop

No further actions and no git. Report what was published and how it was verified. Suggest (don't do):
log out of judge.gai.tw to invalidate the stage 7 cookie, and commit the repo changes when the user is ready.
