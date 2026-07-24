# Case 3: pygments EscapeSequence

- Runnable harness: `<repo>\paper_artifacts\behavioral_sweep\harnesses\case_03_pygments_EscapeSequence.py`
- Expected operation: `color_string`
- Expected latent state: `bold`
- Construction feasibility: `simple`
- Selection reason: +4 likely true positive; +2 read/getter-like mutation; +2 observer/repr/logging/debug-like mutation; +2 later/cache/branch/composition hint; +1 simple constructor; +1 source import path available

If the generic harness cannot construct or safely call the class, the JSON result records the failure classification and reason.
