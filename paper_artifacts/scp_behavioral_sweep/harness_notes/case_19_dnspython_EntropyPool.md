# Case 19: dnspython EntropyPool

- Runnable harness: `<repo>\paper_artifacts\scp_behavioral_sweep\harnesses\case_19_dnspython_EntropyPool.py`
- Expected operation: `random_8`
- Expected latent state: `digest,next_byte`
- Construction feasibility: `simple`
- Selection reason: +4 likely true positive; +2 read/getter-like mutation; +2 later/cache/branch/composition hint; +1 simple constructor; +1 source import path available

If the generic harness cannot construct or safely call the class, the JSON result records the failure classification and reason.
