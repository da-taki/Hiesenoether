# SCP New Experiments Master Report

## 1. What New Experiments Were Run

- Expanded exact-rational mechanism sweep.
- Extended exhaustive enumeration.
- Sampling convergence study.
- Expanded controlled Python analyzer benchmark.
- Expanded PyPI static screen, subject to package availability.
- Manual review queue generation for expanded PyPI results.
- Case-study report generation.

## 2. New Total Executions

- New evaluated order executions across generated experiment artifacts: 712216

## 3. New Sweep Ranges

- Body lengths: [3, 5, 8, 10, 15, 20, 30, 50]
- Observation counts: [0, 10]
- Cap degrees: [1, 8]
- Drift schedules: ['constant', 'linear_decay', 'exponential_decay']
- Total mechanism-sweep configurations: 2112
- Mechanism-sweep executions: 622416

## 4. New Exhaustive Enumeration Coverage

- Total configurations: 240
- Exhaustive feasible configurations: 240
- Extended beyond original 112 scope: 128
- Sample-vs-exact range mismatches when exact is known: 15

## 5. Sampling Convergence Findings

- Budget 8: match rate 0.0, average relative error 0.434900793651, max relative error 0.672222222222
- Budget 16: match rate 0.0, average relative error 0.342599206349, max relative error 0.644444444444
- Budget 32: match rate 0.15, average relative error 0.200555555555, max relative error 0.394444444444
- Budget 64: match rate 0.3, average relative error 0.125505952381, max relative error 0.3
- Budget 128: match rate 0.4, average relative error 0.08498015873, max relative error 0.266666666667
- Budget 256: match rate 0.65, average relative error 0.0425, max relative error 0.194444444444
- Budget 512: match rate 0.8, average relative error 0.02, max relative error 0.138888888889
- Budget 1024: match rate 0.85, average relative error 0.010833333333, max relative error 0.127777777778

## 6. Extended Controlled Benchmark Performance

- Cases: 64
- New cases added: 44
- TP/FP/TN/FN: 40/9/15/0
- Precision: 0.8163
- Recall: 1.0
- Specificity: 0.625
- F1: 0.8989
- Exact-label accuracy: 0.8594

## 7. Expanded PyPI Screen Size and Label Counts

- Target packages: 150
- Packages analyzed: 116
- Target met: False
- Files/classes/functions: 3275/6441/49523
- SAFE/LOW/MEDIUM/HIGH: 5874/0/408/0

## 8. Manual Review Queue Size

- Review queue rows: 250
- Manual labels are intentionally blank.

## 9. Case Studies Generated

- Case-study report generated: True
- Output: `results/scp_new_experiments/case_study_report.md`

## 10. Counterexamples Found

- Zero-observation counterexamples: 0
- Nonlinear cap counterexamples over positive-observation configs: 0
- Sampling max-budget extrema failures: 3

## 11. Failed or Blocked Experiments

# New Experiment Gaps

## Expanded PyPI target not met

Target was 150 packages, but only 116 packages were analyzed. Reason: candidate list exhausted or packages unavailable in local cache. The script reused all available local/cache packages it could acquire and left manual labels blank.

## 12. New Results Ready for the Manuscript

- Expanded exact-rational mechanism sweep, with exact/sampled status per configuration.
- Extended exhaustive enumeration coverage.
- Sampling convergence tables.
- Extended controlled benchmark metrics, including false positives and specificity.
- Controlled case studies and benign near-misses.

## 13. Results Requiring Manual Review Before Inclusion

- Expanded PyPI precision/recall-style claims require manual review of `pypi_expanded_manual_review_queue.csv`.
- PyPI flagged case studies are presentation candidates only until reviewed.
- LOW/SAFE queue rows can support a limited false-negative estimate only after manual labeling.
