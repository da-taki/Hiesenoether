# Case 10: beautifulsoup4 HTML5TreeBuilder

- Runnable harness: `<repo>\paper_artifacts\scp_behavioral_sweep\harnesses\case_10_beautifulsoup4_HTML5TreeBuilder.py`
- Expected operation: `create_treebuilder`
- Expected latent state: `underlying_builder`
- Construction feasibility: `simple`
- Selection reason: +4 likely true positive; +2 read/getter-like mutation; +2 later/cache/branch/composition hint; +1 simple constructor; +1 source import path available

If the generic harness cannot construct or safely call the class, the JSON result records the failure classification and reason.
