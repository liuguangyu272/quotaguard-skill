# Validation notes

Validated on Windows with Python 3.14 on October 16, 2026.

## Observed behavior

- The portable helper completed the Codex App Server handshake and returned live
  five-hour and weekly remaining percentages, reset timestamps, and hourly pace.
- Seven release tests passed, including a relocated installation in a temporary
  path containing spaces. Installing over an existing skill was rejected.
- The previously customized full QuotaGuard distribution passed 23 tests before
  this smaller skill distribution was prepared. Those are separate suites, not
  30 tests of this package.

## Reproducible scenarios

| Simulated input | Computed output | Meaning |
|---|---|---|
| 10% left, 2 hours | 5 points/hour, TIGHT | Protect the core deliverable |
| 10% left, 15 minutes | 40 points/hour, ABUNDANT | A small useful stage may still fit |
| 50% left, 1 hour; weekly 5% | ABUNDANT plus weekly caution | Short-window pace does not erase weekly risk |
| Expired or missing reset | UNKNOWN | No division by zero or invented recovery |
| Session log snapshot | UNKNOWN level | Old data is not treated as live advice |
| 0% left near reset | 0 points/hour plus caution | Approaching reset does not restore quota |

These checks demonstrate calculation and guardrail behavior. They do not prove
that an agent always invokes the skill, obeys every recommendation, saves money,
or completes more tasks. There was no controlled productivity benchmark.

The public video uses the simulated cases above. No account tokens, user session
logs, or private task content are included. The helper itself has no project-write
side effect; progress notes are authored by the agent when appropriate.

Live compatibility was checked only on Windows. Other operating systems and
different account/workspace configurations need their own verification.
