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

## Real-code metamorphic evidence

The stored real-code metamorphic evidence is supported by these committed files:

- `paper_artifacts/realcode_metamorphic_oracle/metamorphic_results.json`
- `paper_artifacts/realcode_metamorphic_oracle/metamorphic_results.csv`
- `paper_artifacts/realcode_metamorphic_oracle/METAMORPHIC_ORACLE_REPORT.md`
- `paper_artifacts/realcode_metamorphic_oracle/traces/*.json`
- `paper_artifacts/realcode_metamorphic_oracle/branch_flip_results.json`
- `paper_artifacts/realcode_metamorphic_oracle/branch_flip_results.csv`
- `paper_artifacts/realcode_metamorphic_oracle/metamorphic_controls.csv`
- `paper_artifacts/realcode_metamorphic_oracle/CONTROL_SUMMARY.md`

The command associated with the stored 60-selected / 39-constructed / 20-confirmed result is:

```bash
python paper_artifacts/realcode_metamorphic_oracle/run_metamorphic_oracle.py
```

The full result requires the exact-version source snapshot at `paper_artifacts/realworld_package_study/source_snapshot/`, rebuilt from the manifests above, plus any installed distributions used by the named cases. The candidate pool records these pinned package versions: httpcore 1.0.9, PyYAML 6.0.3, pytest 8.3.5, rich 15.0.0, markdown 3.10.2, more-itertools 11.0.2, pygments 2.20.0, docutils 0.22.4, soupsieve 2.8.3, beautifulsoup4 4.14.3, boltons 25.0.0, cerberus 1.3.8, dnspython 2.8.0, h11 0.16.0, click-option-group 0.5.9, anyio 4.13.0, tomlkit 0.15.0, marshmallow 4.3.0, and mistune 3.2.1.

If the source snapshot is absent, the oracle can only exercise packages already importable in the local interpreter. Such a reduced environment may construct only a subset of the 60 candidates and must not be interpreted as reproducing the stored 39/20 result. In this mode, import failures or fixture-unavailable outcomes are environment/setup limitations, not changes to the committed evidence files.
