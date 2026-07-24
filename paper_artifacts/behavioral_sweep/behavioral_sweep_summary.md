# Behavioral Sweep Summary

- total selected candidates: 50
- runnable harnesses attempted: 50
- confirmed branch flips: 0
- confirmed output divergences: 0
- confirmed state-only divergences: 4
- structural only: 21
- could not construct: 17
- import failed: 3
- unsafe: 2
- fixture required: 0
- not applicable: 3

- output/branch confirmed divided by selected: 0/50
- output/branch confirmed divided by runnable attempted: 0/50
- any visible divergence divided by selected: 4/50
- any visible divergence divided by runnable attempted: 4/50

| Selected | Runnable attempted | Branch/output confirmed | State-only confirmed | Structural only | Could not construct | Import failed | Fixture required | Unsafe |
| -------: | -----------------: | ----------------------: | -------------------: | --------------: | ------------------: | ------------: | ---------------: | -----: |
| 50 | 50 | 0 | 4 | 21 | 17 | 3 | 0 | 2 |

## Confirmed Cases

| Package | Class | Classification | Operation A | Operation B | Boundary note |
| ------- | ----- | -------------- | ----------- | ----------- | ------------- |
| anyio | BlockingPortalProvider | confirmed_state_divergence_only | __enter__() once on fresh instance | __enter__() once first; then __enter__() again | generic safe repeated-operation harness; confirmation depends on no-arg construction and no-arg operation |
| boltons | SpooledStringIO | confirmed_state_divergence_only | read() once on fresh instance | read() once first; then read() again | generic safe repeated-operation harness; confirmation depends on no-arg construction and no-arg operation |
| dnspython | Tokenizer | confirmed_state_divergence_only | _get_char() once on fresh instance | _get_char() once first; then _get_char() again | generic safe repeated-operation harness; confirmation depends on no-arg construction and no-arg operation |
| docutils | Publisher | confirmed_state_divergence_only | get_settings() once on fresh instance | get_settings() once first; then get_settings() again | generic safe repeated-operation harness; confirmation depends on no-arg construction and no-arg operation |
