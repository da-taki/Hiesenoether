# Case 17: click-option-group _OptGroup

- Runnable harness: `<repo>\paper_artifacts\behavioral_sweep\harnesses\case_17_click_option_group_OptGroup.py`
- Expected operation: `__call__`
- Expected latent state: `_outer_frame_index`
- Construction feasibility: `simple`
- Selection reason: +4 likely true positive; +2 read/getter-like mutation; +2 later/cache/branch/composition hint; +1 simple constructor; +1 source import path available

If the generic harness cannot construct or safely call the class, the JSON result records the failure classification and reason.
