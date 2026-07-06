# Case 15: boltons SpooledStringIO

- Runnable harness: `C:\Users\Asus\Desktop\Profitlo Projects\Hiesenoether\paper_artifacts\scp_behavioral_sweep\harnesses\case_15_boltons_SpooledStringIO.py`
- Expected operation: `read`
- Expected latent state: `_tell`
- Construction feasibility: `simple`
- Selection reason: +4 likely true positive; +2 read/getter-like mutation; +2 later/cache/branch/composition hint; +1 simple constructor; +1 source import path available

If the generic harness cannot construct or safely call the class, the JSON result records the failure classification and reason.
