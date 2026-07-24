# Case 27: docutils LineBlock

- Runnable harness: `<repo>\paper_artifacts\scp_behavioral_sweep\harnesses\case_27_docutils_LineBlock.py`
- Expected operation: `run`
- Expected latent state: `content_offset`
- Construction feasibility: `simple`
- Selection reason: +4 likely true positive; +2 read/getter-like mutation; +2 later/cache/branch/composition hint; +1 simple constructor; +1 source import path available

If the generic harness cannot construct or safely call the class, the JSON result records the failure classification and reason.
