# Codex Task-Model Cross-Model Analysis

Provider scope: Codex task-model configurations only (`gpt-5.6-sol`, `gpt-5.6-terra`, `gpt-5.6-luna`), not cross-provider validation.

## Summary

| Model | Condition | Tasks | Executable | Preserved | Ordinary bugs | Invalid patches | Verified OSDS | Silent divergences | YES | NO | False YES | Conservative NO | Silent false-preservation |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| gpt-5.6-sol | normal | 13 | 13 | 12 | 1 | 0 | 0 | 0 | 3 | 10 | 0 | 9 | 0 |
| gpt-5.6-sol | warned | 13 | 13 | 11 | 2 | 0 | 0 | 0 | 4 | 9 | 0 | 7 | 0 |
| gpt-5.6-sol | all | 26 | 26 | 23 | 3 | 0 | 0 | 0 | 7 | 19 | 0 | 16 | 0 |
| gpt-5.6-terra | normal | 13 | 12 | 9 | 2 | 1 | 1 | 1 | 4 | 9 | 0 | 5 | 0 |
| gpt-5.6-terra | warned | 13 | 12 | 9 | 2 | 1 | 1 | 1 | 2 | 11 | 0 | 7 | 0 |
| gpt-5.6-terra | all | 26 | 24 | 18 | 4 | 2 | 2 | 2 | 6 | 20 | 0 | 12 | 0 |
| gpt-5.6-luna | normal | 13 | 12 | 8 | 2 | 1 | 2 | 2 | 4 | 9 | 0 | 4 | 0 |
| gpt-5.6-luna | warned | 13 | 12 | 9 | 2 | 1 | 1 | 1 | 4 | 9 | 0 | 5 | 0 |
| gpt-5.6-luna | all | 26 | 24 | 17 | 4 | 2 | 3 | 3 | 8 | 18 | 0 | 9 | 0 |

## Verified OSDS Divergences

- `gpt-5.6-terra` `pytest_catching_logs__instrumentation__normal`: package `pytest`, transformation `instrumentation`, evidence `hidden_observation`, divergence `branch/path divergence`, self-assessment `NO`.
- `gpt-5.6-terra` `pytest_catching_logs__instrumentation__warned`: package `pytest`, transformation `instrumentation`, evidence `hidden_observation`, divergence `branch/path divergence`, self-assessment `NO`.
- `gpt-5.6-luna` `pytest_catching_logs__instrumentation__normal`: package `pytest`, transformation `instrumentation`, evidence `hidden_observation`, divergence `branch/path divergence`, self-assessment `NO`.
- `gpt-5.6-luna` `pytest_catching_logs__instrumentation__warned`: package `pytest`, transformation `instrumentation`, evidence `hidden_observation`, divergence `branch/path divergence`, self-assessment `NO`.
- `gpt-5.6-luna` `pyyaml_representer__caching_materialization__normal`: package `PyYAML`, transformation `caching_materialization`, evidence `hidden_observation`, divergence `branch/path divergence`, self-assessment `NO`.

## Ordinary Programming Bugs And Invalid Patches

- `gpt-5.6-sol` `markdown_reference__refactoring__normal`: ordinary_programming_bug, package `markdown`, divergence `branch/path divergence`, ordinary `False`, self-assessment `NO`.
- `gpt-5.6-sol` `markdown_reference__refactoring__warned`: ordinary_programming_bug, package `markdown`, divergence `branch/path divergence`, ordinary `False`, self-assessment `NO`.
- `gpt-5.6-sol` `beautifulsoup_extract__debugging_inspection__warned`: ordinary_programming_bug, package `beautifulsoup4`, divergence `exception/value divergence`, ordinary `False`, self-assessment `NO`.
- `gpt-5.6-terra` `h11_chunked_reader__instrumentation__normal`: invalid_patch, package `h11`, divergence `syntax_failure`, ordinary `False`, self-assessment `NO`.
- `gpt-5.6-terra` `h11_chunked_reader__instrumentation__warned`: invalid_patch, package `h11`, divergence `syntax_failure`, ordinary `False`, self-assessment `NO`.
- `gpt-5.6-terra` `markdown_reference__refactoring__normal`: ordinary_programming_bug, package `markdown`, divergence `branch/path divergence`, ordinary `False`, self-assessment `NO`.
- `gpt-5.6-terra` `markdown_reference__refactoring__warned`: ordinary_programming_bug, package `markdown`, divergence `branch/path divergence`, ordinary `False`, self-assessment `NO`.
- `gpt-5.6-terra` `beautifulsoup_extract__debugging_inspection__normal`: ordinary_programming_bug, package `beautifulsoup4`, divergence `exception/value divergence`, ordinary `False`, self-assessment `NO`.
- `gpt-5.6-terra` `beautifulsoup_extract__debugging_inspection__warned`: ordinary_programming_bug, package `beautifulsoup4`, divergence `exception/value divergence`, ordinary `False`, self-assessment `NO`.
- `gpt-5.6-luna` `h11_chunked_reader__instrumentation__normal`: invalid_patch, package `h11`, divergence `syntax_failure`, ordinary `False`, self-assessment `NO`.
- `gpt-5.6-luna` `h11_chunked_reader__instrumentation__warned`: invalid_patch, package `h11`, divergence `syntax_failure`, ordinary `False`, self-assessment `NO`.
- `gpt-5.6-luna` `markdown_reference__refactoring__normal`: ordinary_programming_bug, package `markdown`, divergence `branch/path divergence`, ordinary `False`, self-assessment `NO`.
- `gpt-5.6-luna` `markdown_reference__refactoring__warned`: ordinary_programming_bug, package `markdown`, divergence `branch/path divergence`, ordinary `False`, self-assessment `NO`.
- `gpt-5.6-luna` `beautifulsoup_extract__debugging_inspection__normal`: ordinary_programming_bug, package `beautifulsoup4`, divergence `exception/value divergence`, ordinary `False`, self-assessment `NO`.
- `gpt-5.6-luna` `beautifulsoup_extract__debugging_inspection__warned`: ordinary_programming_bug, package `beautifulsoup4`, divergence `exception/value divergence`, ordinary `False`, self-assessment `NO`.

## Model-Differential Cases

- `beautifulsoup_extract__debugging_inspection__normal`: gpt-5.6-sol: preserved, gpt-5.6-terra: ordinary_programming_bug, gpt-5.6-luna: ordinary_programming_bug.
- `h11_chunked_reader__instrumentation__normal`: gpt-5.6-sol: preserved, gpt-5.6-terra: invalid_patch, gpt-5.6-luna: invalid_patch.
- `h11_chunked_reader__instrumentation__warned`: gpt-5.6-sol: preserved, gpt-5.6-terra: invalid_patch, gpt-5.6-luna: invalid_patch.
- `pytest_catching_logs__instrumentation__normal`: gpt-5.6-sol: preserved, gpt-5.6-terra: verified_semantic_divergence, gpt-5.6-luna: verified_semantic_divergence.
- `pytest_catching_logs__instrumentation__warned`: gpt-5.6-sol: preserved, gpt-5.6-terra: verified_semantic_divergence, gpt-5.6-luna: verified_semantic_divergence.
- `pyyaml_representer__caching_materialization__normal`: gpt-5.6-sol: preserved, gpt-5.6-terra: preserved, gpt-5.6-luna: verified_semantic_divergence.

## Normal/Warned Paired Outcomes

- `gpt-5.6-sol` `beautifulsoup_extract__debugging_inspection`: normal preserved / NO; warned ordinary_programming_bug / NO.
- `gpt-5.6-sol` `pytest_catching_logs__refactoring`: normal preserved / NO; warned preserved / YES.
- `gpt-5.6-terra` `httpcore_response__caching_materialization`: normal preserved / YES; warned preserved / NO.
- `gpt-5.6-terra` `pyyaml_representer__caching_materialization`: normal preserved / YES; warned preserved / NO.
- `gpt-5.6-luna` `dnspython_tokenizer__access_reordering`: normal preserved / YES; warned preserved / NO.
- `gpt-5.6-luna` `pyyaml_representer__caching_materialization`: normal verified_semantic_divergence / NO; warned preserved / YES.
