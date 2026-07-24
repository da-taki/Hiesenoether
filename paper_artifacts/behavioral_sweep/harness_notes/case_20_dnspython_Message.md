# Case 20: dnspython Message

- Runnable harness: `<repo>\paper_artifacts\behavioral_sweep\harnesses\case_20_dnspython_Message.py`
- Expected operation: `to_wire`
- Expected latent state: `tsig_ctx,wire`
- Construction feasibility: `simple`
- Selection reason: +4 likely true positive; +2 read/getter-like mutation; +2 later/cache/branch/composition hint; +1 simple constructor; +1 source import path available

If the generic harness cannot construct or safely call the class, the JSON result records the failure classification and reason.
