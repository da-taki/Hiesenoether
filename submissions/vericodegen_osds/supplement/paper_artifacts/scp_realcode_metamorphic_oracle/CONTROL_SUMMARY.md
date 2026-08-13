# Negative Control Summary

Controls confirm that each divergence is **caused specifically by observation/read
ordering on a shared real object**, and vanishes when that mechanism is removed. Generated
by `run_metamorphic_controls.py` → `metamorphic_controls.csv`.

## Result

**19 / 19 controls behaved as expected (`divergence_removed = True` for every row).**

| Control type | What it removes | Rows | Divergence removed |
|---|---|---|---|
| `determinism` | nothing (repeat the divergent ordering twice) | 8 | 8/8 identical — no flakiness |
| `fresh_object` | the shared object (observe one, read a fresh one) | 8 | 8/8 back to baseline |
| `reset_between` | latent state via the package's documented reset | 1 | 1/1 back to baseline |
| `pure_observation` | replaces the observation with an unrelated pure read | 2 | 2/2 no divergence |

## Interpretation per case

- **httpcore.Response** — `determinism`: `read()→content` is stably `'alphabeta'`.
  `fresh_object`: materializing one response leaves a *fresh* streaming response still
  raising `RuntimeError`. `pure_observation`: reading `.headers` does **not** materialize
  content (still raises). → The `read()` op, on the same object, is the cause.
- **markdown.Markdown** — `reset_between`: the documented `reset()` restores the
  no-reference baseline `<p>[alpha][]</p>`. `fresh_object`: a fresh instance carries no
  references. → The shared reference registry is the cause.
- **boltons.LRU** — `pure_observation`: `len(cache)` does not refresh recency, so `x` is
  still evicted; only an actual `cache['x']` read saves it. `fresh_object`: touching one
  cache does not affect another. → The recency-updating read is the cause.
- **dnspython.Tokenizer**, **h11.ChunkedReader** — `fresh_object`: a fresh cursor restarts
  at the first token / first `Data` event. → Cursor consumption is the cause.
- **cerberus.Validator** — `fresh_object`: a fresh validator has no errors. → `validate()`
  populates the later-read `errors`.
- **pytest catching_logs** — `fresh_object`: emitting on a fresh (non-level-mutated)
  handler makes the warning visible again. → `catching_logs` raising `handler.level` (and
  not restoring it) is the cause.
- **PyYAML SafeRepresenter** — `fresh_object`: a fresh representer has no identity cache
  and correctly sees the mutated `'after'` value. → The identity cache is the cause.

No control produced a residual or spurious divergence, and every divergent ordering was
bit-for-bit reproducible across repeats.
