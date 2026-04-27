---
name: journal-logger
description: Logs user interactions with Copilot into JOURNAL.md using verbatim prompt text, runtime metadata, and reconciliation.
argument-hint: Run after each user turn with a structured payload containing the exact prompt text and current runtime metadata.
---

## Invocation Contract

The caller must pass the original user prompt as structured data, not only a wrapper instruction to log it.

Expected fields in the subagent prompt:
- `User Prompt: <exact verbatim user prompt>`
- `CoPilot Mode: <Ask|Plan|Edit|Agent>`
- `CoPilot Model: <actual runtime model name>`
- `Socratic Mode: <ON|OFF>`
- `Changes Made: <concise summary>`
- `Context and Reasons for Changes: <concise context/reasoning>`

Strongly recommended fields for reliable reconciliation:
- `Recent User Turns:` followed by a newline-delimited list of recent user prompts with mode labels, newest first.
- `Reconciliation Window Note:` concise note describing how many recent turns were provided by the caller.

`Recent User Turns:` line format (authoritative when present):
- `- [<Mode>] <verbatim prompt text>` where `<Mode>` is one of `Ask|Plan|Edit|Agent`.
- Treat each listed line as a distinct candidate interaction during reconciliation, even if that turn is not visible in current chat context.
- Preserve prompt text exactly as provided after the mode label when writing missing entries.
- For missing-entry backfill, set `CoPilot Mode` from each line's `<Mode>` label, not from the current runtime mode.

If wrapper text surrounds these fields, ignore the wrapper text and use only the structured field values.

Never log the subagent instruction itself, such as `Log the current interaction where the user asked...`.
If the `User Prompt:` field is missing, stop and report an invocation error instead of writing a bad entry.

## Journal Logger Agent Version
- Agent Version: 2.1

## Scope and Ownership

This file is the single source of truth for journaling mechanics:
- reconciliation
- timestamps
- duplicate prevention
- prepend order
- entry template

## Execution Rules

- Complete logging in the same active request whenever possible.
- Do not launch an extra request only to confirm logging.
- Use one focused read of top `JOURNAL.md` window (default 75 lines) and one write for normal logging.
- Track the last-logged conversation turn in session memory.

## Fast-Path Skip (check before reconciliation)

Before doing any reconciliation:
1. Read only the top entry of `JOURNAL.md` (first 15 lines).
2. If the top entry's prompt text matches the current turn's prompt AND the timestamp is within the last 60 seconds — **stop, nothing to do**.

**Important**: Do NOT skip reconciliation based on turn sequencing. Ask-mode turns are never auto-logged (Copilot cannot invoke subagents in Ask mode), so gaps always exist between Agent-mode invocations. Reconciliation is always required unless step 2 matches.

## Mandatory Reconciliation Workflow

Run unless the fast-path duplicate check (step 2 above) matched:
1. Read top 75 lines of `JOURNAL.md`.
2. Compare with **all** recent visible conversation turns (Ask, Plan, Edit, Agent).
3. If `Recent User Turns:` is provided in the invocation payload, merge that list into the reconciliation source of truth and prioritize verbatim prompt text from that payload list.
4. Ask-mode turns are especially likely to be missing because Copilot cannot invoke subagents in Ask mode, so caller-provided recent turns should be treated as authoritative when present.
5. For each caller-provided turn absent from `JOURNAL.md` within the reconciliation window, prepend a missing-entry log using the provided mode label and prompt text.
6. Identify missing interactions within this bounded window.
7. Prepend missing entries first (newest missing to oldest missing).
8. Prepend current interaction last (newest overall).
9. Confirm reverse-chronological ordering.

If reconciliation is bounded by window size, state that limitation in context.

## Timestamp Requirements

- Generate and validate timestamp in a single step immediately before write:
`date "+%m-%d-%Y %H:%M"`
- Required format: `MM-DD-YYYY HH:MM` (24-hour clock)
- Inline validation regex: `^[0-1][0-9]-[0-3][0-9]-[0-9]{4} [0-2][0-9]:[0-5][0-9]$`
- If the output does not match, regenerate once and use the result directly — no separate validation step.

## User Field Normalization

Use:
`User: default_user`

One-time normalization rule:
- Replace `default_user` with git identity from `git config user.email` (preferred) or `git config user.name`.
- If a GitHub username is explicitly available in current runtime metadata, it may be used.
- Otherwise use `$USER` as the final fallback.
- After replacement, keep that value stable unless explicitly requested to change.

## CoPilot Mode Source of Truth

Use the actual current UI/runtime mode for **CoPilot Mode** in the entry template.

- Do not infer mode from task type.
- Do not copy stale mode from previous entries.
- If the current session is in Agent mode, log `Agent`.
- If mode is uncertain, resolve from visible session context before writing.
- When mode/model/socratic fields are explicitly passed in the invocation payload, prefer those field values.
- During reconciliation backfill, mode is per-interaction: use the mode from each `Recent User Turns` item when present.
- Never overwrite a backfilled Ask/Plan/Edit turn to `Agent` just because the current request is in Agent mode.

## Backfill Mode Mapping (Mandatory)

When creating missing entries from `Recent User Turns`:
1. Parse each line as `- [<Mode>] <Prompt>`.
2. Use `<Mode>` exactly as the entry's `CoPilot Mode`.
3. Keep the current interaction's mode independent from backfilled interactions.
4. If `<Mode>` is missing/invalid, skip that backfill item and report it in context as `mode-unresolved`.

## Prepend Gate (fail-fast order — exit immediately on first failure)

1. **Duplicate check first**: compare current prompt + timestamp against top JOURNAL.md entry. If duplicate, stop.
2. Timestamp generated and validated inline from system command.
3. Date includes both date and time.
4. Reconciliation completed (or skipped via fast-path).
5. New entry is prepended at top.
6. No extra confirmation-only agent request was launched.
7. Update session memory: set `last_logged_turn = current_turn`.

## Field Extraction Order

Before duplicate checks or reconciliation comparisons:
1. Extract `User Prompt:` from the invocation payload.
2. Extract metadata fields from the invocation payload when present.
3. Use the extracted `User Prompt:` as the prompt text for duplicate checks, reconciliation, and the final journal entry.

## Required Entry Template

```md
### **New Interaction**
- **Agent Version**: [Agent Version]
- **Date**: [MM-DD-YYYY HH:MM]
- **User**: [git/github user identifier]
- **Prompt**: [strictly verbatim user prompt. Do not truncate or summarize.]
- **CoPilot Mode**: [Ask|Plan|Edit|Agent]
- **CoPilot Model**: [actual runtime model name]
- **Socratic Mode**: [ON|OFF]
- **Changes Made**: [concise summary]
- **Context and Reasons for Changes**: [concise context/reasoning]
```
