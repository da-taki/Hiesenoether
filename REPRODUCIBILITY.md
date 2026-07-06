# Reproducibility

Run commands from the repository root.

On this machine, use the bundled Python runtime:

```powershell
& 'C:\Users\Asus\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' --version
```

## Existing Validation

```powershell
& 'C:\Users\Asus\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' run_tests.py
& 'C:\Users\Asus\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m pytest tests -q
& 'C:\Users\Asus\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m validation.run_all
```

Expected outputs:

- runtime test summary on stdout
- pytest summary on stdout
- `validation/results.json`

Approximate runtimes observed here: 2 seconds, 6 seconds, and 81 seconds.

## New SCP Revision Artifacts

```powershell
& 'C:\Users\Asus\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' paper_artifacts\validate_polynomial_degree_theorem.py
& 'C:\Users\Asus\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' paper_artifacts\sample_unflagged_recall_audit.py
& 'C:\Users\Asus\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' paper_artifacts\real_named_case_reproduction.py
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

Approximate runtimes observed here: 9 seconds, 3 seconds, and 1 second.

## Data Limitation For Recall Audit

The reviewed PyPI corpus source files are required to compute a true 200-class unflagged reviewed-corpus audit. They were not available in this checkout/cache. The audit script therefore reports `not_computed_missing_reviewed_source` for recall fields and uses available expanded SAFE queue rows only as an uncertainty fallback.

