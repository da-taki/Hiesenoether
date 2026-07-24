# Case 43: docutils Reader

- Runnable harness: `<repo>\paper_artifacts\behavioral_sweep\harnesses\case_43_docutils_Reader.py`
- Expected operation: `read`
- Expected latent state: `input,parser,settings,source`
- Construction feasibility: `simple`
- Selection reason: +4 likely true positive; +2 read/getter-like mutation; +2 later/cache/branch/composition hint; +1 simple constructor; +1 source import path available

If the generic harness cannot construct or safely call the class, the JSON result records the failure classification and reason.
