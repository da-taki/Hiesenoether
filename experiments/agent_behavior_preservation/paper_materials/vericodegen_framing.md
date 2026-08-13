# VeriCodeGen framing

Readiness judgment: promising but needs expansion.

The strongest workshop value is methodological and semantic: the task design, exact-response replay, task-scoped evaluation, controls, and manual review process produced a clean real-model result for three Codex task-model configurations. The primary frozen benchmark produced 0/26 verified OSDS divergences for `gpt-5.6-sol`, 2/26 for `gpt-5.6-terra`, and 3/26 for `gpt-5.6-luna`. All five verified failures were silent under ordinary tests, detected by the OSDS-aware oracle, manually reviewed, and located in hidden-observation cases.

For VeriCodeGen, frame this as a bounded semantic-preservation study rather than a failure-rate claim. The benchmark can show how hidden-state preservation should be tested, how ordinary tests differ from OSDS-aware checks, and how self-assessment can be conservative. Expansion should add more witnesses and at least one additional genuine Codex model version where available before making stronger claims.
