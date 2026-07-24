# Input Artifacts Found

This experiment reuses prior real-code / behavioral artifacts already committed to the
repository. Nothing here was newly downloaded from the internet; all package code comes
from a local **source snapshot** captured by an earlier experiment.

## Summary of the input landscape

| Artifact | Contains | Used? | Why |
|---|---|---|---|
| `paper_artifacts/realworld_package_study/source_snapshot/` | 71 real PyPI packages unpacked as source (exact pinned versions), e.g. markdown-3.10.2, boltons-25.0.0, dnspython-2.8.0, h11-0.16.0, docutils-0.22.4, beautifulsoup4-4.14.3, cerberus-1.3.8, more-itertools-11.0.2, PyYAML via installed. | **Yes (primary)** | This is the real-code substrate. `metamorphic_fixtures.add_snapshot_paths()` puts these on `sys.path` so harnesses import the exact pinned real package code with no network. |
| `paper_artifacts/realworld_package_study/real_case_results.csv` | The 4 named confirmed real-code cases: httpcore.Response, pytest catching_logs, PyYAML SafeRepresenter, rich RichHandler. | **Yes** | Highest-priority candidate source (prior confirmed real-code cases). Their harnesses were re-implemented against the metamorphic oracle contract. |
| `paper_artifacts/realworld_package_study/real_case_harnesses/*.py` | Executable reproductions of the 4 named cases. | **Yes (reference)** | Exact operation orderings and fixtures reused (e.g. `httpcore.Response(200, content=[b"alpha", b"beta"])`). |
| `paper_artifacts/behavioral_sweep/behavioral_sweep_results.csv` | 50 statically-flagged package candidates run through a *generic no-arg* runtime harness; most came back `structural_only`, `could_not_construct`, `import_failed`, or `not_applicable`. | **Yes** | Main candidate pool. These are the statically flagged real-code candidates. The generic harness under-powered them; the metamorphic oracle re-attempts them with real fixtures. |
| `paper_artifacts/behavioral_sweep/behavioral_sweep_candidates.csv` | Static metadata for the 50 (class, file, expected observer op, expected latent state, constructor feasibility). | **Yes** | Provides `observation_operation`, `target_read_operation`, `state_fields_suspected`, `construction_hint` for the candidate pool. |
| `paper_artifacts/behavioral_sweep_followup/rescue_results.csv` | 15 manual follow-up re-runs of the weakest sweep candidates with real fixtures; several flipped to `confirmed_output_divergence` / `confirmed_state_divergence_only`. | **Yes** | Second-priority candidate source (manual follow-up candidates). Confirms which fixtures actually construct and diverge; those fixtures are reused verbatim. |
| `paper_artifacts/behavioral_sweep_followup/_rescue_common.py` | Working, importable follow-up harness code for 15 packages incl. the `add_snapshot_paths()` import shim. | **Yes (reference)** | The snapshot import mechanism and several confirmed fixtures were lifted from here. |
| `paper_artifacts/behavioral_sweep_followup/rescue_candidate_selection.csv` | Selection rationale + suspected operation A/B for the 15 follow-up candidates. | **Yes** | Feeds `construction_hint` and `expected_boundary`. |
| `paper_artifacts/rag_prevalence_study/static_findings.csv` | 2,799 static OSDS findings mined from 49 **application** RAG repos (not installable packages). | **No (context only)** | These are application-level snippets from GitHub repos, not instantiable library objects; the prevalence study already characterized them statically. They are the wrong substrate for a *dynamic package-shaped* oracle, so they are not pulled into the harness pool. Cited only for denominator/provenance context. |
| `paper_artifacts/realworld_package_study/real_case_candidates.csv` | Candidate mining list behind the 4 named cases. | **Yes (reference)** | Confirms provenance of the 4 named cases. |
| `paper_artifacts/realworld_package_study/source_snapshot_manifest.csv` | Version + file/class counts for every snapshot package. | **Yes** | Authoritative package_version for pool rows. |
| `paper_artifacts/behavioral_sweep_followup/BEHAVIORAL_SWEEP_FOLLOWUP_RESULTS.md` | Narrative of the follow-up round and its boundary notes. | **Yes (reference)** | Boundary-note wording (e.g. "cursor semantics, not a defect") carried forward. |

## Interpreter availability note

`python` is not on `PATH` on this machine (Windows Store shim). The bundled launcher
`py` (CPython 3.14.4) is used for every command. This is reported in
`QUALITY_GATE_REPORT.md`.

## Installed vs. snapshot-only

- **Installed in the interpreter:** httpcore 1.0.9, pytest 8.3.5, PyYAML 6.0.3, h11 0.16.0, click 8.1.8.
- **Snapshot-only (imported via `add_snapshot_paths`):** markdown, more-itertools, pygments,
  docutils, beautifulsoup4, boltons, cerberus, dnspython, soupsieve, click-option-group,
  mistune, tomlkit, structlog, tenacity, marshmallow, anyio, and ~55 others.
- **Unavailable (neither installed nor snapshotted):** `rich` — so the rich RichHandler
  case is honestly recorded as `import_failed` rather than reconstructed.
