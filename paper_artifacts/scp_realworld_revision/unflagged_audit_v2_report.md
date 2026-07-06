# Unflagged Recall Audit V2

| total_corpus_classes | flagged_classes_or_findings | likely_flagged_matches | likely_flagged_false_positives | unflagged_classes | sampled_unflagged_classes | likely_missed_matches | likely_nonmatches | uncertain_cases | estimated_false_negatives | estimated_recall |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |
| 4383 | 278 | 203 | 75 | 4093 | 200 | 0 | 200 | 0 | 0/1 | 1/1 |

## Sensitivity

| Treat uncertain as | Estimated FN | Estimated recall |
| --- | ---: | ---: |
| nonmatch | 0/1 | 1/1 |
| half_missed | 0/1 | 1/1 |
| missed | 0/1 | 1/1 |

Uncertainty note: computed only over successfully rebuilt source snapshot; not full reviewed corpus unless total classes=4437
