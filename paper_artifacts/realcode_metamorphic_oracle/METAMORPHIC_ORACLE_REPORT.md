# Real-Code Metamorphic Oracle & Branch-Flip Study

*review artifact — "Access-Induced Semantic Divergence in Software Systems: A Formal and
Empirical Study."*

Artifact directory: `paper_artifacts/realcode_metamorphic_oracle/`

## 1. Executive summary

This study attacks the central external-validity objection to the review artifact — that
most dynamic evidence characterizes an interpreter/model **we built ourselves** — by
running a metamorphic order-sensitivity oracle directly against **real, unmodified PyPI
package code**.

From a pool of **60 statically-flagged real-code candidates**, all **60 were selected**
for harness attempts. **39 harnesses constructed** an executable package-shaped instance.
Under observation/read reordering the oracle found:

- **1 branch divergence** (value-vs-exception control-flow flip): `httpcore.Response`;
- **17 output divergences** (differing returned values);
- **0 exception-vs-exception divergences**;
- **2 state-only divergences**: `docutils.Transformer`, `boltons.LRI`;
- **19 constructed-but-no-divergence** (honest negatives);
- **21 could-not-construct / import-failed / not-relevant / unsafe** (honest failures, not hidden).

That is **20 confirmed divergences across 12 distinct real packages** (httpcore, PyYAML,
pytest, markdown, more-itertools, docutils, beautifulsoup4, boltons, cerberus, dnspython,
h11, anyio).

We then lifted confirmed divergences into **9 realistic caller-level branch flips**
(RQ2). **All 9 flipped both the branch label and its downstream consequence** — e.g.
`cache_response` vs `stream_response_or_error`, `accept_request` vs `reject_request`,
`emit_alert` vs `suppress_alert` — purely from reordering an observation relative to a
read, with the divergence-causing operation being a real package operation in every case.

**19 negative controls all confirmed** that each divergence is caused specifically by the
observation/read ordering on a shared object and disappears under `fresh_object`,
`reset_between`, or `pure_observation`, with deterministic repeats.

## 2. Research questions

- **RQ1.** Among statically flagged real-code candidates that can be instantiated safely,
  how often do observation-shaped operations produce order-dependent output, exception,
  branch, or state divergence?
  → Of **39 constructed** harnesses, **20 (51%)** showed a confirmed divergence
  (1 branch, 17 output, 2 state-only); **19** showed none.
- **RQ2.** Can confirmed real-code divergences be lifted into realistic caller-level branch
  flips, where reordering an access/observation changes the downstream program path?
  → **Yes: 9/9 constructed caller branches flipped**, each changing a concrete downstream
  consequence.

## 3. Candidate sources

Candidates were drawn from prior repository artifacts in priority order (see
`INPUT_ARTIFACTS_FOUND.md` and `metamorphic_candidate_pool.csv`). All package code is the
local **source snapshot** (`realworld_package_study/source_snapshot/`, 71 pinned packages)
or already-installed distributions — **no network access**.

| Priority | Source | Count | Notes |
|---|---|---|---|
| 1 | Prior confirmed real-code cases (`real_case_results.csv`) | 4 | httpcore, PyYAML, pytest, rich |
| 1–2 | Manual rescue candidates (`rescue_results.csv`) | 15 | markdown, more-itertools, boltons, dnspython, h11, cerberus, docutils, bs4, soupsieve, pygments, click-option-group |
| 3 | Behavioral-sweep candidates (`behavioral_sweep_results.csv`) | 20 | anyio, docutils family, dnspython, bs4 (incl. honest could-not-construct/import-failed) |
| — | Extra snapshot cursor/stateful classes | 8 | mistune, more-itertools, tomlkit, marshmallow, boltons, dnspython |
| — | docutils RST directive family (honest construction attempts) | 13 | all `could_not_construct` (need a state machine) |
| | **Total** | **60** | all `selected_for_harness = yes` |

**Denominator statement.** The selected denominator is **60** candidates; the constructed
denominator is **39**. All divergence rates in this report are quoted over the **39
constructed** harnesses. We make **no PyPI-prevalence claim**: 60/39 are the candidates we
chose to attempt, not a random sample of PyPI.

## 4. Fixture synthesis strategy

`metamorphic_fixtures.py` provides deterministic per-family factories
(`string_text`, `bytes`, `io_bytes`, `iterator`, `list_or_dict`, `tree_or_html`,
`yaml_or_repr`, `logging_handler`, `http_response`, `parser_tokenizer`, `buffer`, `cache`,
`path_or_tempfile`). Each factory returns a `Fixture` whose **`builder` produces a fresh,
equivalent object on every call**, so the oracle can create the two independent instances
each ordering needs. Missing dependencies raise `FixtureUnavailable`, which becomes a
per-candidate `fixture_unavailable` classification rather than a global crash. Snapshot
package code is imported via `add_snapshot_paths()` (the same shim the rescue round used).

## 5. Metamorphic oracle design

`run_metamorphic_oracle.py` constructs two fresh equivalent instances and runs an order
pair:

- **pair1** (observation before target read): A = `[target]`; B = `[observation, target]`.
- **pair3** (repeated read, for cursors): A = `[target, target]`; B = `[observation, target, target]`.
- **custom** harnesses assemble their own two orderings where the shape does not fit
  builder/observation/target (e.g. PyYAML's identity cache; pytest's handler-level mutation).

Orderings are compared **position-by-position**. A value-vs-exception flip on a read →
**branch** divergence; differing values → **output** divergence; differing exceptions →
**exception** divergence; equal reads with differing object state → **state-only**
divergence. This is a direct dynamic instantiation of the formal OSDS read/observation
transition model (§9): the observation updates latent state and the read exposes a value
that depends on it.

Every attempted harness is classified into exactly one of:
`confirmed_output_divergence`, `confirmed_exception_divergence`, `confirmed_branch_divergence`,
`confirmed_output_and_branch_divergence`, `confirmed_state_only_divergence`, `no_divergence`,
`could_not_construct`, `fixture_unavailable`, `import_failed`, `unsafe_to_execute`,
`not_relevant_after_inspection`. Full per-candidate reproduction traces are written to
`traces/<candidate_id>.json`.

## 6. Main metamorphic results

| Candidates selected | Harnesses attempted | Constructed | Output div. | Exception div. | Branch div. | State-only | No div. | Failed |
|---|---|---|---|---|---|---|---|---|
| 60 | 60 | 39 | 17 | 0 | 1 | 2 | 19 | 21 |

Failure breakdown (21): `could_not_construct` 14 · `import_failed` 3 · `not_relevant_after_inspection` 2 · `unsafe_to_execute` 2.

### Confirmed divergences (20 across 12 packages)

| Candidate | Package | Classification | Boundary note |
|---|---|---|---|
| rc01_httpcore_Response | httpcore 1.0.9 | **branch** | `read()` materializes `_content`; `.content` flips `RuntimeError`→value |
| rc02_PyYAML_SafeRepresenter | PyYAML 6.0.3 | output | identity cache returns a stale node for a mutated object |
| rc03_pytest_catching_logs | pytest 8.3.5 | output | `catching_logs` raises `handler.level` and does not restore it |
| re01_markdown_Markdown | markdown 3.10.2 | output | reference registry from a prior `convert()` changes later render |
| re02_more_itertools_seekable | more-itertools 11.0.2 | output | cursor advance changes later `next()` |
| re04_docutils_Transformer | docutils 0.22.4 | state-only | `get_priority_string()` advances serial bookkeeping |
| re06_beautifulsoup4_PageElement | beautifulsoup4 4.14.3 | output | `extract()` destructively mutates the tree |
| re07_boltons_LRI | boltons 25.0.0 | state-only | access updates hit/miss stats (not eviction order) |
| re08_boltons_LRU | boltons 25.0.0 | output | access reorders recency → changes eviction |
| re09_boltons_MultiFileReader | boltons 25.0.0 | output | multi-stream cursor advances |
| re10_cerberus_Validator | cerberus 1.3.8 | output | `validate()` populates the later-read `errors` |
| re11_dnspython_Tokenizer | dnspython 2.8.0 | output | token consumption advances the cursor |
| re12_h11_ChunkedReader | h11 0.16.0 | output | consuming a chunk flips `Data` vs `EndOfMessage` |
| re13_h11_ReceiveBuffer | h11 0.16.0 | output | line extraction is destructive |
| bs09_anyio_BlockingPortalProvider | anyio 4.13.0 | output | `__enter__` mutates the lease/portal state |
| bs15_boltons_SpooledStringIO | boltons 25.0.0 | output | text spool cursor advances |
| bs23_docutils_Publisher | docutils 0.22.4 | output | `get_settings()` caches settings read later |
| ext02_boltons_SpooledBytesIO | boltons 25.0.0 | output | byte spool cursor advances |
| ext07_dnspython_Tokenizer_concat | dnspython 2.8.0 | output | consuming a token changes remaining concatenation |
| ext08_boltons_LRU_pair2 | boltons 25.0.0 | output | an access between two reads changes the eviction victim |

## 7. Branch-flip results

`run_branch_flip_cases.py` wraps confirmed divergences in ordinary-looking caller
functions and runs each under both orderings. **9/9 confirmed branch flips.** The branch
wrappers are ours; every divergence-causing operation inside them is a real package
operation.

| Package | Ordering A branch → consequence | Ordering B branch → consequence | Consequence change | Boundary note |
|---|---|---|---|---|
| httpcore | `stream_pending` → stream_response_or_error | `content_ready` → cache_response | ✓ | `read()` before `.content` flips exception→value |
| pytest | `warning_seen` → emit_alert | `warning_hidden` → suppress_alert | ✓ | `catching_logs` raises handler level, not restored |
| PyYAML | `after_payload` → use_after_payload | `before_payload` → use_before_payload | ✓ | identity cache returns the stale node |
| boltons (LRU) | `x_evicted` → recompute_x | `x_live` → serve_x_from_cache | ✓ | a read refreshes recency → different eviction |
| dnspython | `has_aa` → handle_first_field | `has_bb` → continue_parse | ✓ | consuming a token moves the cursor |
| h11 | `data` → continue_parse | `end` → finish_response | ✓ | consuming a chunk flips Data vs EndOfMessage |
| cerberus | `clean` → accept_request | `has_errors` → reject_request | ✓ | `validate()` populates errors read next |
| markdown | `plain` → render_plain_text | `linked` → render_hyperlink | ✓ | a prior `convert()` registers the reference |
| beautifulsoup4 | `first_is_a` → process_a | `first_is_b` → process_b | ✓ | `extract()` removes the node read next |

Each caller's exact code is in `branch_flip_results.csv` (`code_snippet`) and
`branch_flip_results.json`.

## 8. Negative controls

`run_metamorphic_controls.py` → `metamorphic_controls.csv`, summarized in
`CONTROL_SUMMARY.md`. **19/19 controls behaved as expected** (`divergence_removed = True`):
every divergence disappeared under `fresh_object` / `reset_between` / `pure_observation`,
and every divergent ordering reproduced bit-for-bit under `determinism`. This rules out
flakiness and confirms the ordering (not some incidental artifact) is the cause.

## 9. Relation to the formal OSDS model

The formal core (`docs/formal_core_design.md`, `validation/exact_semantics.py`) models a
straight-line program over a latent state `(b, a, d)`: a **read** exposes `f(b, a, d)` and
increments/updates latent state; an **observation** exposes no additive value but updates
latent drift `g`. Order sensitivity arises because reordering read/observation changes the
latent state seen by a later read.

This study is a **dynamic, real-code instantiation** of exactly that transition structure:

- the *observation* (`read()`, `validate()`, `cache['x']`, `catching_logs` enter/exit,
  `extract()`, a prior `convert()`) updates real latent object state;
- the *target read* (`.content`, `.errors`, `items()`, `.messages`, `str(soup)`,
  `convert('[a][]')`) exposes a value depending on that latent state;
- reordering the two changes the exposed value — the model's core prediction.

The httpcore case additionally realizes the model's *exception/branch* extension, which the
proof core deliberately abstracts away: the latent-state difference is observable as a
control-flow flip, not just a value change.

## 10. Relation to the static screen and rescue audit

The static screen and behavioral sweep flagged candidates by source shape; the generic
no-arg sweep harness then under-powered most of them (`structural_only`,
`could_not_construct`). This oracle **re-attempts the same statically-flagged candidates
with real fixtures** and separates three things the earlier rounds conflated:

- candidates that genuinely diverge under ordering (20);
- candidates that construct but do **not** diverge under our fixtures (19 — e.g.
  `pygments.EscapeSequence`, `soupsieve.CSSMatch`, `dnspython.BTree`, `tomlkit`,
  `marshmallow`, `more-itertools.peekable/spy`);
- candidates that cannot be safely instantiated at all (21, itemized above).

This is consistent with, and sharper than, the rescue audit: it reproduces the rescue's
confirmed cases and adds caller-level branch flips and controls the rescue lacked.

## 11. Threats to validity

- **Selection, not prevalence.** Candidates are curated from prior artifacts, not sampled
  from PyPI. We report rates over 39 constructed harnesses only; no prevalence is claimed.
- **Not bugs.** Most divergences are *intended* semantics (cursors, caches, LRU recency,
  destructive parsers). We claim order-sensitivity/observability, **not** defects.
- **Fixture influence.** A `no_divergence` verdict is fixture-relative: a different input
  might expose a divergence (e.g. soupsieve with a stateful selector). We report the exact
  fixtures and count these as honest negatives, not proof of order-insensitivity.
- **Branch wrappers are ours.** The caller functions in Task 5 are written by us; only the
  divergence-*causing* operations are real package code. We do not claim the packages ship
  these callers.
- **`rich` unavailable.** One of the four prior named cases (`rich.RichHandler`) is
  `import_failed` because `rich` is neither installed nor snapshotted; we do not
  reconstruct it.
- **No soundness/completeness claim.** The oracle is an existence detector over chosen
  orderings, not a decision procedure.

## 12. Artifact integration recommendation

Add a subsection "Real-code metamorphic evidence" to the empirical section. Lead with the
39-constructed / 20-confirmed / 12-package result and the 9/9 caller branch flips, and cite
the controls. This directly answers the "you only tested your own interpreter" objection:
the divergences and branch flips are observed in unmodified httpcore, pytest, PyYAML,
markdown, boltons, dnspython, h11, cerberus, beautifulsoup4, more-itertools, docutils, and
anyio. Keep the framing at "order-sensitive/observable behavior," not "bug."

## 13. Suggested abstract / introduction wording

> Using a metamorphic oracle over 60 statically-flagged real-code candidates, we
> constructed 39 executable package-shaped harnesses from unmodified PyPI packages. Under
> observation/read reordering, 20 harnesses (across 12 distinct packages) exhibited
> confirmed divergence — 1 value-vs-exception branch flip, 17 output divergences, and 2
> state-only divergences — while 19 showed none and 21 could not be safely instantiated.
> We further lifted confirmed divergences into 9 realistic caller branches, all 9 of which
> flipped their downstream program path (e.g. cache-vs-stream, accept-vs-reject) solely
> from reordering an access relative to a read. Nineteen negative controls confirmed that
> each divergence is caused specifically by the ordering and vanishes when the shared
> object, latent state, or observation is neutralized.

## 14. Exact command log

```
# interpreter: `python` is not on PATH (Windows Store shim); the bundled `py` launcher
# (CPython 3.14.4) is used for all commands.
py paper_artifacts/realcode_metamorphic_oracle/metamorphic_fixtures.py       # fixture self-test
py paper_artifacts/realcode_metamorphic_oracle/run_metamorphic_oracle.py     # RQ1 + pool CSV + traces
py paper_artifacts/realcode_metamorphic_oracle/run_branch_flip_cases.py      # RQ2 caller branch flips
py paper_artifacts/realcode_metamorphic_oracle/run_metamorphic_controls.py   # negative controls
py run_tests.py                                                                  # project test suite
py -m pytest tests                                                               # project pytest suite
```

Generated artifacts: `metamorphic_candidate_pool.csv`, `metamorphic_results.{json,csv}`,
`traces/*.json`, `branch_flip_results.{json,csv}`, `metamorphic_controls.csv`,
`CONTROL_SUMMARY.md`, `INPUT_ARTIFACTS_FOUND.md`, `QUALITY_GATE_REPORT.md`, this report.
