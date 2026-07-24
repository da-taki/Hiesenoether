# Case 2: more-itertools seekable

- Runnable harness: `<repo>\paper_artifacts\behavioral_sweep\harnesses\case_02_more_itertools_seekable.py`
- Expected operation: `__next__`
- Expected latent state: `_index`
- Construction feasibility: `requires_args`
- Selection reason: +4 likely true positive; +3 HIGH; +2 read/getter-like mutation; +2 later/cache/branch/composition hint; +1 source import path available

If the generic harness cannot construct or safely call the class, the JSON result records the failure classification and reason.
