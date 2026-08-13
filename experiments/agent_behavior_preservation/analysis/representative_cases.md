# Representative cases

No manually verified real-model semantic divergences were found in the full GPT-5.6 Sol run. The strongest observed cases are therefore non-OSDS ordinary bugs and conservative self-assessments.

## Ordinary-test-visible bugs

- `markdown_reference__refactoring__normal`: generated escaped HTML tag predicates, causing `ordinary_smoke()` to return `False`; classified as `ordinary_programming_bug`.
- `markdown_reference__refactoring__warned`: same escaped HTML predicate issue; classified as `ordinary_programming_bug`.
- `beautifulsoup_extract__debugging_inspection__warned`: generated double-escaped HTML input, so BeautifulSoup found no `<p>` tags and ordinary execution raised exceptions; classified as `ordinary_programming_bug`.

## Representative preservations

- `pyyaml_representer__caching_materialization` in both normal and warned conditions preserved PyYAML representer identity caching behavior.
- `boltons_lru__repeated_access_cleanup__warned` returned unchanged code, preserving the LRU recency update from `cache["x"]`.
- `dnspython_tokenizer__access_reordering__warned` preserved the number and order of `token.value` reads.

## Conservative NO self-assessments

The model often rejected transformations with logging or cached property accesses as not preserving all externally observable behavior, even when the benchmark replay observed preserved behavior. Normal had 9 behavior-preserved NO claims; warned had 7.
