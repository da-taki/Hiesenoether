# PyPI Static Analyzer Benchmark

## Scope
- packages attempted: 32
- packages successfully analyzed: 30
- Python files scanned: 458
- classes scanned: 1561
- functions scanned: 8971

Packages analyzed: attrs, click, humanize, arrow, cachetools, sortedcontainers, boltons, more-itertools, toolz, multidict, marshmallow, cerberus, tomli, tomlkit, python-dotenv, loguru, structlog, tenacity, pluggy, packaging, importlib-metadata, jsonschema, tqdm, anyio, sniffio, pyparsing, requests, urllib3, jinja2, markupsafe
Packages skipped: pendulum (download_failed), yarl (download_failed)

## Aggregate analyzer labels

| Label | Count |
| --- | ---: |
| SAFE | 1332 |
| LOW | 0 |
| MEDIUM | 111 |
| HIGH | 2 |

## Manual review of flagged findings

| Review label | Count |
| --- | ---: |
| likely true positive | 61 |
| likely false positive | 52 |
| unclear | 0 |

## Precision over reviewed flagged findings

precision = likely_true_positive / (likely_true_positive + likely_false_positive) = 61 / (61 + 52) = 0.5398
Unclear cases are excluded from the denominator.

## Recall

Recall is not estimated because the benchmark does not fully label all SAFE and LOW classes in the analyzed packages.

## Notable findings

Likely true positives:
- click `_FDCapture` in `click-8.4.0\src\click\testing.py`: source review found state mutation on a method/property/call path that returns a value or access handle
- cachetools `_Timer` in `cachetools-7.1.3\src\cachetools\__init__.py`: source review found state mutation on a method/property/call path that returns a value or access handle
- cachetools `TLRUCache` in `cachetools-7.1.3\src\cachetools\__init__.py`: source review found state mutation on a method/property/call path that returns a value or access handle
- cachetools `Wrapper` in `cachetools-7.1.3\src\cachetools\_cachedmethod.py`: source review found state mutation on a method/property/call path that returns a value or access handle
- cachetools `Wrapper` in `cachetools-7.1.3\src\cachetools\_cachedmethod.py`: source review found state mutation on a method/property/call path that returns a value or access handle
- cachetools `Wrapper` in `cachetools-7.1.3\src\cachetools\_cachedmethod.py`: source review found state mutation on a method/property/call path that returns a value or access handle
- boltons `LRI` in `boltons-25.0.0\boltons\cacheutils.py`: source review found state mutation on a method/property/call path that returns a value or access handle
- boltons `LRU` in `boltons-25.0.0\boltons\cacheutils.py`: source review found state mutation on a method/property/call path that returns a value or access handle
- boltons `DeprecatableModule` in `boltons-25.0.0\boltons\deprutils.py`: source review found state mutation on a method/property/call path that returns a value or access handle
- boltons `DeferredValue` in `boltons-25.0.0\boltons\formatutils.py`: source review found state mutation on a method/property/call path that returns a value or access handle

Likely false positives:
- attrs `_ClassBuilder` in `attrs-26.1.0\src\attr\_make.py`: fluent class-builder mutator returns self; not an access/read path
- attrs `_CountingAttr` in `attrs-26.1.0\src\attr\_make.py`: decorator registration mutates validator list and returns the decorated method
- click `ProgressBar` in `click-8.4.0\src\click\_termui_impl.py`: context-manager entry flag returns self; no access-derived value
- click `Context` in `click-8.4.0\src\click\core.py`: context-manager depth tracking returns self; no access-derived value
- click `Command` in `click-8.4.0\src\click\core.py`: lazy help-option cache; repeated access returns the same semantic option
- click `Group` in `click-8.4.0\src\click\core.py`: callback registration decorator, not an access/read path
- click `LazyFile` in `click-8.4.0\src\click\utils.py`: lazy file-open cache; repeated access returns the cached handle
- cachetools `_HashedTuple` in `cachetools-7.1.3\src\cachetools\keys.py`: memoized hash cache; semantic hash value is stable
- sortedcontainers `SortedDict` in `sortedcontainers-2.4.0\sortedcontainers\sorteddict.py`: deprecated cached view property; semantic view is stable
- boltons `CachedFunction` in `boltons-25.0.0\boltons\cacheutils.py`: constructor/local closure pattern; not an access/read path

## Limitations

- packages are not a random sample of PyPI
- analyzer is syntactic and heuristic
- precision is estimated only over reviewed flagged findings
- recall is not established
- absence of findings does not prove absence of access-evolving semantics
