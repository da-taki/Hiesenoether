# Case 4: docutils Transformer

- Runnable harness: `C:\Users\Asus\Desktop\Profitlo Projects\Hiesenoether\paper_artifacts\scp_behavioral_sweep\harnesses\case_04_docutils_Transformer.py`
- Expected operation: `get_priority_string`
- Expected latent state: `serialno`
- Construction feasibility: `requires_args`
- Selection reason: +4 likely true positive; +2 read/getter-like mutation; +2 observer/repr/logging/debug-like mutation; +2 later/cache/branch/composition hint; +1 source import path available

If the generic harness cannot construct or safely call the class, the JSON result records the failure classification and reason.
