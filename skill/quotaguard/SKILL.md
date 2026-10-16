---
name: quotaguard
description: Read remaining Work/Codex quota and reset time, then pace substantial research, document, or coding tasks using quota per hour until reset. Use when asked about quota or before and between expensive stages of a long task. Skip extra checks for simple questions or tiny edits. Requires local Python and a signed-in Codex installation.
---

# QuotaGuard

Help the user finish useful, verified work within their available allowance. Intended primarily for ChatGPT Plus users with a five-hour quota window. This is an on-demand skill, not a background monitor or a guarantee of invocation on every message.

## Read the account

Run `python scripts/query.py` using the **absolute path to this skill's bundled script**. Resolve it from this SKILL.md location; do not assume the user's project contains the script. Python 3.11+ and signed-in Codex are required. The helper has no third-party runtime dependencies and makes no project writes. On Windows, `py -3` is another option if `python` is unavailable; on macOS/Linux use `python3`.

Check at the start of substantial work, after an expensive stage, and when explicitly asked. Reuse a recent reading when little work has happened. Avoid polling on every tool call.

Read `five_hour`, `weekly`, `source`, `timestamp`, `evaluated_at`, `warnings`, and `pacing`. Report both remaining percentages and reset countdowns in the user's language. Convert UTC/local timestamps to the user's timezone when needed. A countdown is time **until reset**, not remaining working time or message count.

Default sensing uses the documented Codex App Server method. Authentication stays with Codex; never read auth.json. The account/workspace is the one selected by the local Codex login. Do not claim it matches a different App account.

If unavailable, explain briefly and continue bounded work. Do not retry in a loop. Only when a fallback is useful, run `scripts/query.py --source session`; label the timestamp and stale source. Log snapshots are not a public compatibility contract. Their pacing level is UNKNOWN, even if a mathematical ratio is available. Do not use them as a hard gate.

## Pace using quota AND time

`pacing.percentage_points_per_hour = remaining_percent / remaining_hours`

The personal reference is **12 percentage points per hour**. This is a configurable-by-editing workflow preference, not an OpenAI limit or an estimate of model throughput. Classify using the unrounded ratio:

| Budget (percentage points/hour) | Level | Suggested behavior |
|---|---|---|
| Below 6 | TIGHT | Focus on the core deliverable; use smaller stages |
| 6 to below 12 | CONSERVATIVE | Proceed with core work; reduce optional exploration |
| 12 to below 18 | COMFORTABLE | Work normally; include useful exploration |
| 18 or more | ABUNDANT | Allow deeper useful work within remaining absolute quota |

For example, 10% with two hours until reset gives 5 points/hour. The same 10% with 15 minutes until reset gives 40. The second case can support a small stage; the absolute budget is still only 10%. Never invent extra work to use up quota.

Always keep these constraints:
- The next stage must fit the absolute remaining budget as far as can reasonably be estimated. Unknown costs call for smaller stages. Zero quota remains zero until a fresh reading shows otherwise.
- Check weekly allowance separately. Low weekly quota can constrain work even when the five-hour ratio is high. Use 20% as a default weekly caution signal, not a hard shutdown threshold.
- Near reset, the ratio can become very large. Do not extrapolate it into unlimited capacity or assume a reset has already occurred.
- A missing/expired reset or non-five-hour window has no valid five-hour pace. Report UNKNOWN; do not divide by zero.
- If comparing actual burn between readings, use the same account and reset window. Other sessions may contribute to the change. Do not attribute all account consumption to this task.

Keep necessary verification at every level. Reduce optional breadth before correctness. Do not silently change the chosen model, reasoning effort, or parallelism, and do not claim to control App settings. Do not abandon required work solely because a heuristic threshold was crossed. If a real limit prevents continuation, report exactly what remains.

## Preserve progress

For long tasks with file outputs, save a concise `.quotaguard/RESUME.md` in the active project after meaningful milestones or when interruption risk rises. Include goal, completed work, remaining work, decisions, actual verification results, and one concrete next action. This is an agent-written work record, not a code backup or an automatic snapshot. Do not create it for a quota-only question.

On resumption, verify the record against current files and refresh quota. Do not automatically wait for resets, schedule tasks, or promise unattended resumption. Respect the user's current priorities.

Give one compact quota summary at the first check. Repeat only on meaningful changes, sensing failures, or explicit requests. If this environment cannot run the local helper, say so and continue the underlying task without fabricated quota numbers.
