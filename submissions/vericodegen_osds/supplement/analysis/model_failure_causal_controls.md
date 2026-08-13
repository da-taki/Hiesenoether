# Model Failure Causal Controls

This report replays the five verified OSDS failures from the frozen primary Codex task-model study under mechanism-neutralizing witness controls. The generated candidate files are read exactly from the frozen replay result directories and are not edited.

## Summary

| Causal status | Count |
| --- | ---: |
| `mechanism_neutralized_divergence_disappeared` | 5 |

## Per-Failure Results

| Model | Task | Package | Intervention | Original OSDS | Controlled OSDS | Causal status |
| --- | --- | --- | --- | --- | --- | --- |
| gpt-5.6-terra | `pytest_catching_logs__instrumentation__normal` | pytest | isolate diagnostic logger from the captured handler hierarchy | fail | pass | `mechanism_neutralized_divergence_disappeared` |
| gpt-5.6-terra | `pytest_catching_logs__instrumentation__warned` | pytest | isolate diagnostic logger from the captured handler hierarchy | fail | pass | `mechanism_neutralized_divergence_disappeared` |
| gpt-5.6-luna | `pytest_catching_logs__instrumentation__normal` | pytest | isolate diagnostic logger from the captured handler hierarchy | fail | pass | `mechanism_neutralized_divergence_disappeared` |
| gpt-5.6-luna | `pytest_catching_logs__instrumentation__warned` | pytest | isolate diagnostic logger from the captured handler hierarchy | fail | pass | `mechanism_neutralized_divergence_disappeared` |
| gpt-5.6-luna | `pyyaml_representer__caching_materialization__normal` | PyYAML | clear representer identity cache after represent_data observations | fail | pass | `mechanism_neutralized_divergence_disappeared` |

## Interpretation

For pytest, the control isolates the diagnostic logger from the logger hierarchy that owns the captured handler. The exact generated patch still executes its diagnostic logging calls, but those calls no longer populate the same handler whose level is later mutated by `catching_logs`. Under this neutralized witness environment, the candidate behavior matches the controlled baseline.

For PyYAML, the control wraps `SafeRepresenter.represent_data` so the identity cache is cleared after each representer observation. The exact Luna candidate still uses its generated caching transformation. Under this cache-neutralized environment, the controlled baseline no longer returns the stale pre-mutation node, and the candidate matches the controlled baseline.

These controls support the causal attribution that the five verified failures depend on the access-induced latent-state mechanisms identified by the OSDS witnesses.

CSV source: `analysis/model_failure_causal_controls.csv`.
