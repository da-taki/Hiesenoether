# PyPI Static Analyzer Benchmark

## Scope
- packages attempted: 73
- packages successfully analyzed: 73
- Python files scanned: 1858
- classes scanned: 4437
- functions scanned: 21530
- MEDIUM/HIGH findings reviewed: 278

Packages analyzed: attrs, click, humanize, pendulum, arrow, cachetools, sortedcontainers, boltons, more-itertools, toolz, yarl, multidict, marshmallow, cerberus, tomli, tomlkit, python-dotenv, loguru, structlog, tenacity, pluggy, packaging, importlib-metadata, jsonschema, tqdm, anyio, sniffio, pyparsing, requests, urllib3, jinja2, markupsafe, flask, werkzeug, itsdangerous, blinker, iniconfig, filelock, platformdirs, pathspec, mypy-extensions, typing-extensions, typing-inspection, dacite, cattrs, deprecated, wrapt, dateparser, parsedatetime, Babel, soupsieve, beautifulsoup4, pygments, mistune, markdown, docutils, pydocstyle, flake8, mccabe, pycodestyle, pyflakes, click-option-group, fastjsonschema, jsonpointer, jsonpatch, email-validator, dnspython, h11, h2, wsproto, websockets, frozenlist, aiosignal
Packages skipped: none

## Aggregate analyzer labels

| Label | Count |
| --- | ---: |
| SAFE | 3909 |
| LOW | 0 |
| MEDIUM | 276 |
| HIGH | 2 |

## Manual review of flagged findings

| Review label | Count |
| --- | ---: |
| likely true positive | 203 |
| likely false positive | 75 |
| unclear | 0 |

## Precision over reviewed flagged findings

precision = likely_true_positive / (likely_true_positive + likely_false_positive) = 203 / (203 + 75) = 0.7302
Unclear cases are excluded from the denominator.

## Recall

Recall is not estimated because SAFE and LOW classes were not exhaustively manually labeled.

## Notable findings

Likely true positives:
- pendulum `Duration` in `pendulum\duration.py`: source review found state mutation on a method/property/call path that returns a value or access handle
- pendulum `AbsoluteDuration` in `pendulum\duration.py`: source review found state mutation on a method/property/call path that returns a value or access handle
- cachetools `_Timer` in `cachetools-7.1.3\src\cachetools\__init__.py`: source review found state mutation on a method/property/call path that returns a value or access handle
- cachetools `TLRUCache` in `cachetools-7.1.3\src\cachetools\__init__.py`: source review found state mutation on a method/property/call path that returns a value or access handle
- cachetools `Wrapper` in `cachetools-7.1.3\src\cachetools\_cachedmethod.py`: source review found state mutation on a method/property/call path that returns a value or access handle
- cachetools `Wrapper` in `cachetools-7.1.3\src\cachetools\_cachedmethod.py`: source review found state mutation on a method/property/call path that returns a value or access handle
- cachetools `Wrapper` in `cachetools-7.1.3\src\cachetools\_cachedmethod.py`: source review found state mutation on a method/property/call path that returns a value or access handle
- boltons `LRI` in `boltons-25.0.0\boltons\cacheutils.py`: source review found state mutation on a method/property/call path that returns a value or access handle
- boltons `LRU` in `boltons-25.0.0\boltons\cacheutils.py`: source review found state mutation on a method/property/call path that returns a value or access handle
- boltons `DeprecatableModule` in `boltons-25.0.0\boltons\deprutils.py`: source review found state mutation on a method/property/call path that returns a value or access handle

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
