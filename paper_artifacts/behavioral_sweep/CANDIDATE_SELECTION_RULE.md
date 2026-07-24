# Candidate Selection Rule

Input pool: `results_static/pypi_static_benchmark_findings.csv`, restricted to rows with `manual_review = likely true positive` and an existing source file in the rebuilt exact-version snapshot.

Scoring:

- +4 likely true positive
- +3 HIGH risk label
- +2 read/property/getter-like mutation hint
- +2 observer/repr/str/logging/debug/snapshot mutation hint
- +2 later read/composition/threshold/cache/branch hint
- +1 simple/no-required-args constructor inferred from AST
- +1 source import path available
- -2 tests/docs/examples path
- -2 abstract/protocol/base-like class
- -3 likely external service/network/database/framework context

Tie-breaks: higher score, package name, file path, class name, line number.

- reviewed findings: 278
- likely true positives: 203
- likely true positives with source available: 202
- selected candidates: 50
- previous four confirmed cases selected by this rule: none
