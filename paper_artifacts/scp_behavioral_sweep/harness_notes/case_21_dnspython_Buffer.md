# Case 21: dnspython Buffer

- Runnable harness: `<repo>\paper_artifacts\scp_behavioral_sweep\harnesses\case_21_dnspython_Buffer.py`
- Expected operation: `get`
- Expected latent state: `_buffer`
- Construction feasibility: `simple`
- Selection reason: +4 likely true positive; +2 read/getter-like mutation; +2 later/cache/branch/composition hint; +1 simple constructor; +1 source import path available

If the generic harness cannot construct or safely call the class, the JSON result records the failure classification and reason.
