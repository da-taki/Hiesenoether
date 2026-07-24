# Reproducibility

Run all commands from the repository root. Use `python` (or `py` on Windows) with Python 3.10+.

## Core tests and validation

```bash
python run_tests.py
python -m pytest tests -q
python -m validation.run_all
```

Expected outputs:

- runtime test summary on stdout
- pytest summary on stdout
- `validation/results.json`

## Supplementary review artifacts

```bash
python paper_artifacts/validate_polynomial_degree_theorem.py
python paper_artifacts/sample_unflagged_recall_audit.py
python paper_artifacts/real_named_case_reproduction.py
```

Expected outputs:

- `paper_artifacts/polynomial_degree_theorem_validation.csv`
- `paper_artifacts/polynomial_degree_theorem_validation.md`
- `paper_artifacts/polynomial_degree_theorem_notes.md`
- `paper_artifacts/THEOREM_UPGRADE_DRAFT.md`
- `paper_artifacts/unflagged_audit_sample.csv`
- `paper_artifacts/unflagged_audit_summary.csv`
- `paper_artifacts/unflagged_audit_report.md`
- `paper_artifacts/real_named_case_reproduction_output.json`

## Real-world corpus

The real-world experiments in `paper_artifacts/realworld_package_study/` ran against a snapshot of third-party PyPI packages. That vendored source is not committed. To rebuild it, download the exact package versions listed in `paper_artifacts/realworld_package_study/corpus_manifest.csv` (each row has the package name, version, wheel filename, SHA-256, and a PyPI URL) into `paper_artifacts/realworld_package_study/downloads/`, then run `build_source_snapshot.py`.

The reviewed-corpus recall audit reports `not_computed_missing_reviewed_source` for recall fields when the reviewed source snapshot is not present.
