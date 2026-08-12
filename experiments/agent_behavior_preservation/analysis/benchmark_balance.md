# Benchmark Balance Audit

Multiple tasks derived from the same witness/package are correlated and should not be described as independent semantic phenomena.

| Package | Underlying witnesses | Normal tasks | Warned tasks | Transformation families |
|---|---|---:|---:|---|
| PyYAML | rc02_PyYAML_SafeRepresenter | 2 | 2 | caching_materialization, instrumentation |
| beautifulsoup4 | re06_beautifulsoup4_PageElement | 1 | 1 | debugging_inspection |
| boltons | re08_boltons_LRU | 1 | 1 | repeated_access_cleanup |
| cerberus | re10_cerberus_Validator | 2 | 2 | caching_materialization, instrumentation |
| dnspython | re11_dnspython_Tokenizer | 1 | 1 | access_reordering |
| h11 | re12_h11_ChunkedReader | 1 | 1 | instrumentation |
| httpcore | rc01_httpcore_Response | 2 | 2 | caching_materialization, instrumentation |
| markdown | re01_markdown_Markdown | 1 | 1 | refactoring |
| pytest | rc03_pytest_catching_logs | 2 | 2 | instrumentation, refactoring |
