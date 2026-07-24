# Case 6: anyio CancelScope

- Runnable harness: `<repo>\paper_artifacts\behavioral_sweep\harnesses\case_06_anyio_CancelScope.py`
- Expected operation: `__enter__`
- Expected latent state: `_active,_host_task,_parent_scope`
- Construction feasibility: `simple`
- Selection reason: +4 likely true positive; +2 read/getter-like mutation; +2 later/cache/branch/composition hint; +1 simple constructor; +1 source import path available

If the generic harness cannot construct or safely call the class, the JSON result records the failure classification and reason.
