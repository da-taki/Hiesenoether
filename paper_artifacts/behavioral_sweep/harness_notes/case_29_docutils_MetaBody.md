# Case 29: docutils MetaBody

- Runnable harness: `<repo>\paper_artifacts\behavioral_sweep\harnesses\case_29_docutils_MetaBody.py`
- Expected operation: `field_marker`
- Expected latent state: `parent`
- Construction feasibility: `simple`
- Selection reason: +4 likely true positive; +2 read/getter-like mutation; +2 later/cache/branch/composition hint; +1 simple constructor; +1 source import path available

If the generic harness cannot construct or safely call the class, the JSON result records the failure classification and reason.
