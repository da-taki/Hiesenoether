# Prospective Expansion Results

The prospective expansion was frozen at commit `0f7dea5ca3cfc62e040026a8c780f1127526b0dc` before model execution. It contains 7 new base tasks and 14 normal/warned variants from 7 witnesses in 3 packages. All rows are expected-access-sensitive calibration witnesses from the unused confirmed real-code OSDS pool.

| Model | Tasks | Executable | Preserved | Ordinary bugs | Invalid patches | Verified OSDS divergences | Silent OSDS divergences |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `gpt-5.6-sol` | 14 | 14 | 14 | 0 | 0 | 0 | 0 |
| `gpt-5.6-terra` | 14 | 14 | 14 | 0 | 0 | 0 | 0 |
| `gpt-5.6-luna` | 14 | 14 | 14 | 0 | 0 | 0 | 0 |

Package spread: 3 packages: boltons, dnspython, h11.
Witness spread: 7 unique witnesses.
Hidden-observation outcomes: 0 rows in the expansion. Expected-access-sensitive outcomes: 42/42 preserved.
Normal prompt outcomes: 21/21 preserved. Warned prompt outcomes: 21/21 preserved.
Manual failure review: no expansion row required OSDS divergence adjudication because every candidate was executable, ordinary-pass, and OSDS-pass.
