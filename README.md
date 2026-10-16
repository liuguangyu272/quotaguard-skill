# QuotaGuard Skill

**Help your agent make better use of each five-hour quota window.**

A lightweight skill for ChatGPT Plus users working with Codex. It gives the agent two pieces of context: **how much quota is left, and how long until it resets**.

The goal is simple: make useful progress on the task you have already given the agent while quota is available. Do not leave worthwhile work undone just because the agent cannot see its allowance. Do not create unnecessary work just to empty the meter.

## Why this exists

I built this because I wanted to make better use of my Plus quota between resets, including when my account offered additional reset opportunities. Seeing only a remaining percentage was not enough: the time until the next reset changes how that allowance can be used.

QuotaGuard supplies that missing context. It does not manage or redeem reset offers.

## One calculation

```text
hourly budget = remaining quota percentage / hours until reset
```

| Quota left | Reset in | Hourly budget |
|---|---|---|
| 10% | 2 hours | 5 percentage points/hour |
| 10% | 15 minutes | 40 percentage points/hour |

Both cases still have only **10% available**. The second has more quota available per remaining hour, not more quota overall.

The personal reference is **12 percentage points per hour**, with four guidance levels:

| Hourly budget | Level | Guidance |
|---|---|---|
| Below 6 | TIGHT | Focus on core work; reduce optional exploration. |
| 6 to below 12 | CONSERVATIVE | Continue the task with restrained extra investigation. |
| 12 to below 18 | COMFORTABLE | Proceed at normal, useful depth. |
| 18 or more | ABUNDANT | Make room for worthwhile depth within the requested task. |

These are preferences, not official limits or predictions of task cost. Necessary verification stays in every level. Absolute remaining quota and weekly limits still apply. A large hourly budget near reset does not make a large task affordable or guarantee it will finish before a limit is reached.

## Install and use

Requirements: **Python 3.11+**, local **Codex signed in with your ChatGPT account**, and an environment that supports skills and local command execution. Windows has been live-tested; macOS and Linux have not.

```sh
git clone https://github.com/liuguangyu272/quotaguard-skill.git
cd quotaguard-skill
python install.py
```

Use `python3` if needed. The installer copies the skill to `$CODEX_HOME/skills/quotaguard`, or `~/.codex/skills/quotaguard`, and refuses to overwrite an existing installation.

Refresh the skill list or start a new session, then ask:

```text
$quotaguard Check my remaining quota and reset time, then use that context to make useful progress on this task.
```

Automatic skill selection is enabled, but invocation on every message is not guaranteed. This is an on-demand check, not continuous monitoring.

To try the reader without installing the skill:

```sh
python skill/quotaguard/scripts/query.py
```

If Codex is not detected, set `QUOTAGUARD_CODEX_COMMAND` to its executable path.

## Keep it simple

This project reads quota, calculates a time-aware budget, and gives the agent pacing guidance. It is not a task scheduler, a task-cost predictor, or an automatic reset-credit tool. It does not change the model or grant extra quota.

Readings belong to the account used by local Codex; make sure it matches your current task. Unavailable or stale data must not be treated as a live allowance. The helper uses Codex's local app-server interface without opening credential files. It does not cover every ordinary ChatGPT feature's limit.

The purpose is **useful work within the current window**, not maximum consumption, guaranteed savings, or a promise that tasks will never be interrupted.

## Validation and credits

```sh
python -m unittest discover -s tests -v
```

See [validation notes](docs/validation.md) for tested behavior and limitations, and [OpenAI's app-server documentation](https://learn.chatgpt.com/docs/app-server) for the underlying account interface.

Built on the MIT-licensed readers from [LUMOSSES/QuotaGuard](https://github.com/LUMOSSES/QuotaGuard). See [NOTICE](NOTICE.md). Independent community project; not affiliated with OpenAI.
