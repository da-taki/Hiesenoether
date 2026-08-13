# Hiesenoether Agent Behavior Preservation: GPT-5.6 Sol Full Run

## Run

- Branch: `experiment/agent-behavior-preservation`
- Starting commit: `f90a3a0a7cda1f6e43b0e0799dedf78e5fbcfefa`
- Provider: Codex task model
- Model: `gpt-5.6-sol`
- Reasoning: `low`
- Temperature: `null`
- Seed: `null`
- Valid normal replay: `codex-gpt-5-6-sol-full-normal-exact-20260813T1415Z`
- Valid warned replay: `codex-gpt-5-6-sol-full-warned-exact-20260813T1430Z`

## Normal results

- Attempted/responses: 13/13
- Patches extracted/applied: 13/13
- Executable candidates: 13/13
- Behavior preserved by replay: 12/13
- Verified semantic divergences: 0
- Silent semantic divergences: 0
- Ordinary programming bugs: 1
- Self-assessment: 3 YES, 10 NO, 0 UNCLEAR
- False YES claims: 0
- Behavior-preserved NO claims: 9

## Warned results

- Attempted/responses: 13/13
- Patches extracted/applied: 13/13
- Executable candidates: 13/13
- Behavior preserved by replay: 11/13
- Verified semantic divergences: 0
- Silent semantic divergences: 0
- Ordinary programming bugs: 2
- Self-assessment: 4 YES, 9 NO, 0 UNCLEAR
- False YES claims: 0
- Behavior-preserved NO claims: 7

## Paired semantic results

- normal diverged / warned diverged: 0
- normal diverged / warned preserved: 0
- normal preserved / warned diverged: 0
- normal preserved / warned preserved: 13

## Controls

Pipeline controls remain separate from GPT-5.6 Sol: noop-preserving was 26/26 preserved, and static-semantics-blind-transformer was 26/26 divergent with ordinary-pass / OSDS-fail behavior.

## Manual review

Manual review classified the non-preserved real-model rows as ordinary programming bugs, not verified semantic divergences: normal Markdown refactoring, warned Markdown refactoring, and warned BeautifulSoup debugging/inspection.

## Workshop readiness

Verdict: promising but needs expansion. The run is clean and useful as a calibration result, but no verified semantic divergence was observed in the real-model data.
