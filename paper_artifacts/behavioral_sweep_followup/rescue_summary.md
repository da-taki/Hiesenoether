# Rescue Summary

| Rescue selected | Manual harnesses attempted | Branch/output confirmed | State-only confirmed | Structural only | Still could not construct | Import failed | External fixture | Not applicable |
| --------------: | -------------------------: | ----------------------: | -------------------: | --------------: | ------------------------: | ------------: | ---------------: | -------------: |
| 15 | 15 | 9 | 2 | 4 | 0 | 0 | 0 | 0 |

## Selected Rescue Candidates

| Rank | Original | Package | Class | Previous |
| --- | --- | --- | --- | --- |
| 1 | 1 | markdown | Markdown | structural_only_no_runtime_difference |
| 2 | 2 | more-itertools | seekable | could_not_construct |
| 3 | 3 | pygments | EscapeSequence | structural_only_no_runtime_difference |
| 4 | 4 | docutils | Transformer | could_not_construct |
| 5 | 5 | soupsieve | CSSMatch | import_failed |
| 6 | 11 | beautifulsoup4 | PageElement | structural_only_no_runtime_difference |
| 7 | 12 | boltons | LRI | structural_only_no_runtime_difference |
| 8 | 13 | boltons | LRU | structural_only_no_runtime_difference |
| 9 | 14 | boltons | MultiFileReader | structural_only_no_runtime_difference |
| 10 | 16 | cerberus | BareValidator | structural_only_no_runtime_difference |
| 11 | 17 | click-option-group | _OptGroup | structural_only_no_runtime_difference |
| 12 | 18 | dnspython | BTree | structural_only_no_runtime_difference |
| 13 | 22 | dnspython | Tokenizer | confirmed_state_divergence_only |
| 14 | 49 | h11 | ChunkedReader | structural_only_no_runtime_difference |
| 15 | 50 | h11 | ReceiveBuffer | structural_only_no_runtime_difference |

## Runnable Manual Harnesses Attempted

Attempted 15 manual harnesses with a 20 second timeout per harness.

## Output/Branch Divergences Found

| Rank | Package | Class | Classification | Boundary |
| --- | --- | --- | --- | --- |
| 1 | markdown | Markdown | confirmed_output_divergence | The Python-Markdown docs explicitly say reset() should be called between convert() calls; count this as stateful reuse behavior, not a package bug. |
| 2 | more-itertools | seekable | confirmed_output_divergence | Iterator consumption is expected behavior; the rescue shows the generic no-arg harness missed a real cursor effect. |
| 6 | beautifulsoup4 | PageElement | confirmed_output_divergence | BeautifulSoup extraction is intentionally destructive; use only as a tree-mutation/access-order example. |
| 8 | boltons | LRU | confirmed_output_divergence | LRU access affects eviction order as designed; it is evidence of consequential access state, not a defect. |
| 9 | boltons | MultiFileReader | confirmed_output_divergence | MultiFileReader is a stream-like cursor; output divergence is expected after a prior read. |
| 10 | cerberus | BareValidator | confirmed_output_divergence | BareValidator itself rejects schema-backed validation; the runnable fixture uses the public Validator subclass to exercise inherited BareValidator state. |
| 13 | dnspython | Tokenizer | confirmed_output_divergence | Tokenizer is a cursor over token input; output divergence is expected after consuming a token. |
| 14 | h11 | ChunkedReader | confirmed_output_divergence | ChunkedReader consumes a ReceiveBuffer; Data versus EndOfMessage is expected stream-reader state. |
| 15 | h11 | ReceiveBuffer | confirmed_output_divergence | ReceiveBuffer line extraction is destructive by design; it is a cursor semantics example. |

## State-Only Divergences Found

| Rank | Package | Class | Boundary |
| --- | --- | --- | --- |
| 4 | docutils | Transformer | The manual fixture tests Transformer serial bookkeeping, not transform application output. |
| 7 | boltons | LRI | LRI access affects statistics but not eviction order in this fixture. |

## Structural Or Failed Manual Attempts

| Rank | Package | Class | Classification | Reason |
| --- | --- | --- | --- | --- |
| 3 | pygments | EscapeSequence | structural_only_no_runtime_difference | In this Pygments version the ANSI fixture did not trigger the suspected bold mutation; the case remains structural-only. |
| 5 | soupsieve | CSSMatch | structural_only_no_runtime_difference | The rescue only fixes sys.path/import construction; simple selector matching remained output-equivalent. |
| 11 | click-option-group | _OptGroup | structural_only_no_runtime_difference | The decorator fixture is tiny and in-process; it did not produce a meaningful runtime divergence. |
| 12 | dnspython | BTree | structural_only_no_runtime_difference | BTree lookup is stable under this minimal fixture; cursor/copy-on-write behavior was not forced. |

## JSON Validation

None.

## Comparison With Original Generic Sweep

The original generic sweep selected 50 candidates and found 0 output/branch divergences and 4 state-only divergences. This manual rescue selected 15 candidates, attempted 15 package-specific fixtures, and found 9 output/branch divergences plus 2 state-only divergences. The result supports the narrower claim that package-specific construction can recover behavior that a no-argument generic harness misses; it is not a PyPI prevalence estimate.
