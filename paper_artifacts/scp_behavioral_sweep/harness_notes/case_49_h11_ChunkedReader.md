# Case 49: h11 ChunkedReader

- Runnable harness: `C:\Users\Asus\Desktop\Profitlo Projects\Hiesenoether\paper_artifacts\scp_behavioral_sweep\harnesses\case_49_h11_ChunkedReader.py`
- Expected operation: `__call__`
- Expected latent state: `_bytes_in_chunk,_bytes_to_discard,_reading_trailer`
- Construction feasibility: `simple`
- Selection reason: +4 likely true positive; +2 read/getter-like mutation; +2 later/cache/branch/composition hint; +1 simple constructor; +1 source import path available

If the generic harness cannot construct or safely call the class, the JSON result records the failure classification and reason.
