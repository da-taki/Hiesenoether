# Artifact Polish Recommendations

## Search Hits

The repository still foregrounds terms that may weaken OSDS positioning:

- `entropy`: appears in `README.md`, `docs/uncertainty.md`, `docs/energy_model.md`, `docs/formal_core_design.md`, and proof-support outputs.
- `Hiesenoether`: appears in `README.md`, `docs/uncertainty.md`, `docs/formal_core_design.md`, and rewrite notes.
- `2.2 million` / `2,200,000`: appears in `README.md`, `results/paper_results_tables.md`, and `docs/review_results_brief.md`.

## Replacement Recommendations

| Current wording | Recommended replacement |
| --- | --- |
| entropy | drift, access drift, or observation-induced drift; keep `entropy` only when referring to implementation variable names or legacy output columns |
| Hiesenoether | the reference implementation, the experimental reference interpreter, or the replay substrate |
| 2.2 million executions | a deterministic replay suite with exact, ablatable mechanisms; move execution count to evaluation details |
| volume-first claims | mechanism-first claims tied to theorem-backed calibration and real-code behavioral cases |

## Positive Novelty Wording

Use:

"The contribution is an exactly replayable, ablatable operational account of the access-observation feedback loop, together with theorem-backed calibration and real-code behavioral cases."

Avoid leading with raw execution count. Lead with why the mechanism matters in real code: read-shaped operations such as logging, content materialization, low-level representation, and rendering can mutate latent state and change later outputs or branches.

