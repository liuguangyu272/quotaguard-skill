# QuotaGuard Skill v0.1.0

An English, portable skill for ChatGPT Plus users who want their agent to
consider both remaining quota and time until reset.

- Live Codex quota reader, using the documented App Server interface.
- Five-hour pacing formula and four levels around a 12-point/hour reference.
- Weekly, near-reset, stale-data, and zero-quota cautions.
- Agent guidance for meaningful progress notes and necessary verification.
- Standard-library runtime and a non-overwriting local installer.
- Seven passing release tests and a live Windows sensing check.
- A narrated English demo with subtitles (illustrative quota values).

Download the ZIP, extract it, and run `python install.py`. Python 3.11+ and a
signed-in local Codex installation are required. An existing skill with the
same name must be backed up or renamed first.

The 12-point reference is a workflow preference, not an official rate limit.
Automatic skill selection is not guaranteed. No extra quota or guaranteed
productivity gains are claimed. See README and docs/validation.md.

Based on MIT-licensed quota-reading code from LUMOSSES/QuotaGuard.
