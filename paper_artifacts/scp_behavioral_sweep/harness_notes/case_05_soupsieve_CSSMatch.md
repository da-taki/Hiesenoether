# Case 5: soupsieve CSSMatch

- Runnable harness: `<repo>\paper_artifacts\scp_behavioral_sweep\harnesses\case_05_soupsieve_CSSMatch.py`
- Expected operation: `match_selectors`
- Expected latent state: `iframe_restrict,namespaces`
- Construction feasibility: `requires_args`
- Selection reason: +4 likely true positive; +2 read/getter-like mutation; +2 observer/repr/logging/debug-like mutation; +2 later/cache/branch/composition hint; +1 source import path available

If the generic harness cannot construct or safely call the class, the JSON result records the failure classification and reason.
