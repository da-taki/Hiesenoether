# Expanded PyPI Screen Tables

## Aggregate

- packages analyzed: 116
- files scanned: 3275
- classes scanned: 6441
- functions scanned: 49523
- SAFE/LOW/MEDIUM/HIGH: 5874/0/408/0

## Packages With Most MEDIUM/HIGH Findings

| package | version | files_scanned | classes_scanned | functions_scanned | SAFE | LOW | MEDIUM | HIGH |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| sympy | 1.14.0 | 814 | 1972 | 21913 | 1878 | 0 | 93 | 0 |
| hypothesis | 6.155.7 | 104 | 257 | 1883 | 205 | 0 | 32 | 0 |
| ipython | 9.15.0 | 158 | 314 | 2018 | 279 | 0 | 31 | 0 |
| prompt-toolkit | 3.0.52 | 145 | 319 | 2192 | 289 | 0 | 30 | 0 |
| pytest | 9.1.1 | 85 | 260 | 2054 | 234 | 0 | 21 | 0 |
| tox | 4.56.1 | 126 | 150 | 1087 | 127 | 0 | 20 | 0 |
| coverage | 7.15.0 | 64 | 114 | 809 | 95 | 0 | 19 | 0 |
| rich | 15.0.0 | 67 | 181 | 912 | 125 | 0 | 12 | 0 |
| networkx | 3.6.1 | 285 | 149 | 2247 | 137 | 0 | 12 | 0 |
| mpmath | 1.4.1 | 60 | 56 | 1349 | 44 | 0 | 12 | 0 |
| pydantic | 2.13.4 | 104 | 431 | 1866 | 394 | 0 | 11 | 0 |
| httpx | 0.28.1 | 23 | 87 | 446 | 76 | 0 | 11 | 0 |
| virtualenv | 21.5.1 | 96 | 108 | 598 | 97 | 0 | 11 | 0 |
| jedi | 0.20.0 | 86 | 300 | 1739 | 289 | 0 | 11 | 0 |
| cffi | 2.0.0 | 18 | 60 | 573 | 50 | 0 | 10 | 0 |
| distlib | 0.4.3 | 13 | 78 | 582 | 69 | 0 | 9 | 0 |
| PyYAML | 6.0.3 | 18 | 88 | 347 | 80 | 0 | 8 | 0 |
| httpcore | 1.0.9 | 31 | 91 | 429 | 84 | 0 | 7 | 0 |
| black | 26.5.1 | 51 | 76 | 631 | 65 | 0 | 7 | 0 |
| traitlets | 5.15.1 | 21 | 87 | 467 | 81 | 0 | 6 | 0 |
| parso | 0.8.7 | 22 | 136 | 448 | 130 | 0 | 6 | 0 |
| lxml | 6.1.1 | 29 | 55 | 406 | 49 | 0 | 6 | 0 |
| starlette | 1.3.1 | 33 | 99 | 456 | 94 | 0 | 5 | 0 |
| pycparser | 3.0 | 8 | 65 | 370 | 60 | 0 | 5 | 0 |
| fastapi | 0.139.0 | 524 | 394 | 1158 | 364 | 0 | 4 | 0 |

## Top False-Positive-Risk Patterns

| pattern | count |
| --- | --- |
| state_mutating_reader | 368 |
| context_manager_bookkeeping | 18 |
| cache_or_memoization | 17 |
| builder_or_fluent_mutator | 3 |
| descriptor_or_proxy | 2 |
