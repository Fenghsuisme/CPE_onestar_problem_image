@AGENTS.md

## Claude-specific

- Skills: `.claude/skills/<name>` are symlinks to `.agents/skills/<name>`. Edit the files in `.agents/`.
- Sub-agents: use the `sonnet` model for workers and verifiers.
- "The user's logged-in browser" = Synara's in-app browser (`browser_*` tools).
