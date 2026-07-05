# Paper Results Tables

## Number Reproduction Status

| Claim | Expected | Actual | Status | Source |
| --- | ---: | ---: | --- | --- |
| 2.2 million executions | 2200000 | 2200000 | reproduced_from_existing_results | `results/summary.csv` |
| exhaustive enumeration configurations | 112 | 112 | reproduced_from_code | `results/exhaustive_enumeration_summary.json` |
| exhaustive enumeration mismatches | 0 | 0 | reproduced_from_code | `results/exhaustive_enumeration_summary.json` |
| controlled analyzer benchmark cases | 20 | 20 | reproduced_from_code | `analysis\benchmark_examples.py` |
| controlled analyzer benchmark precision | 0.9231 | 0.9231 | reproduced_from_code | `analysis\benchmark_examples.py` |
| controlled analyzer benchmark recall | 1.0 | 1.0 | reproduced_from_code | `analysis\benchmark_examples.py` |
| controlled analyzer benchmark exact_label_accuracy | 0.95 | 0.95 | reproduced_from_code | `analysis\benchmark_examples.py` |
| controlled analyzer benchmark TP | 12 | 12 | reproduced_from_code | `analysis\benchmark_examples.py` |
| controlled analyzer benchmark FP | 1 | 1 | reproduced_from_code | `analysis\benchmark_examples.py` |
| controlled analyzer benchmark TN | 7 | 7 | reproduced_from_code | `analysis\benchmark_examples.py` |
| controlled analyzer benchmark FN | 0 | 0 | reproduced_from_code | `analysis\benchmark_examples.py` |
| PyPI packages | 73 | 73 | reproduced_from_existing_results | `results_static/pypi_static_benchmark_findings.csv` |
| PyPI files | 1858 | 1858 | reproduced_from_existing_results | `results_static/pypi_static_benchmark_findings.csv` |
| PyPI classes | 4437 | 4437 | reproduced_from_existing_results | `results_static/pypi_static_benchmark_findings.csv` |
| PyPI functions | 21530 | 21530 | reproduced_from_existing_results | `results_static/pypi_static_benchmark_findings.csv` |
| reviewed MEDIUM/HIGH findings | 278 | 278 | reproduced_from_existing_results | `results_static/pypi_static_benchmark_findings.csv` |
| likely true positives | 203 | 203 | reproduced_from_existing_results | `results_static/pypi_static_benchmark_findings.csv` |
| likely false positives | 75 | 75 | reproduced_from_existing_results | `results_static/pypi_static_benchmark_findings.csv` |
| reviewed PyPI precision | 0.7302 | 0.7302 | reproduced_from_existing_results | `results_static/pypi_static_benchmark_findings.csv` |

## Observation Count Sweep

Status: reproduced_from_existing_results. Source: `results\A1.csv`.

| config | inspects | std | range | n_valid | status |
| --- | --- | --- | --- | --- | --- |
| A1_inspect0 | 0 | 0.0 | 0.0 | 100000 | reproduced_from_existing_results |
| A1_inspect1 | 1 | 70.6351 | 210.24 | 100000 | reproduced_from_existing_results |
| A1_inspect2 | 2 | 125.5293 | 497.76 | 100000 | reproduced_from_existing_results |
| A1_inspect3 | 3 | 189.9506 | 878.04 | 100000 | reproduced_from_existing_results |
| A1_inspect4 | 4 | 269.13 | 1368.0 | 100000 | reproduced_from_existing_results |
| A1_inspect5 | 5 | 365.7408 | 1986.0 | 100000 | reproduced_from_existing_results |

## Cap Degree Sweep

Status: reproduced_from_existing_results. Source: `results\A2.csv`.

| config | nonlinear | std | range | log_range | n_valid | status |
| --- | --- | --- | --- | --- | --- | --- |
| A2_linear | linear | 3.2187 | 9.6 | 2.261763 | 100000 | reproduced_from_existing_results |
| A2_quadratic | quadratic | 70.612 | 210.24 | 5.34825 | 100000 | reproduced_from_existing_results |
| A2_cubic | cubic | 1722.0659 | 5129.856 | 8.542833 | 100000 | reproduced_from_existing_results |
| A2_extreme | extreme | 12098.2108 | 36098.208 | 10.493999 | 100000 | reproduced_from_existing_results |

## Ablation Table

Status: reproduced_from_existing_results. Source: `results_extended\e3_ablation_comparison.csv`.

| config | ablation | std | range | std_vs_baseline | range_vs_baseline | status |
| --- | --- | --- | --- | --- | --- | --- |
| ablation_baseline | none | 135.7523 | 384.0 | 1.0 | 1.0 | reproduced_from_existing_results |
| ablation_noop_inspect | noop_inspect | 0.0 | 0.0 | 0.0 | 0.0 | reproduced_from_existing_results |
| ablation_no_entropy | no_entropy | 116.7647 | 330.0 | 0.8601 | 0.8594 | reproduced_from_existing_results |
| ablation_fixed_order | fixed_order | 0.0 | 0.0 | 0.0 | 0.0 | reproduced_from_existing_results |

## Boundary Notes

- The analyzer metrics are reproduced from code on the controlled benchmark.
- The PyPI precision is reproduced from existing reviewed labels, not from a production-prevalence claim.
- Exhaustive enumeration is a bounded computational check over the stated 112 configurations.
