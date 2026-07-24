# Rescue Manual Review Notes

## 1. markdown `Markdown`

- Original sweep classification: `structural_only_no_runtime_difference`
- Why the generic harness failed or was weak: It used no-argument construction/repeated calls that did not exercise the candidate with meaningful package data.
- Manual fixture built: Two real Markdown strings on one Markdown instance, output_format='html'.
- Realistic fixture: Yes.
- Result: `confirmed_output_divergence`; output_diff=True, branch_flip=False, state_diff=True.
- Should it be used in the paper: Use only with explicit boundary language.
- Exact caution language: The Python-Markdown docs explicitly say reset() should be called between convert() calls; count this as stateful reuse behavior, not a package bug.

## 2. more-itertools `seekable`

- Original sweep classification: `could_not_construct`
- Why the generic harness failed or was weak: constructor requires arguments: iterable
- Manual fixture built: seekable over iter(['a', 'b', 'c']).
- Realistic fixture: Yes.
- Result: `confirmed_output_divergence`; output_diff=True, branch_flip=False, state_diff=True.
- Should it be used in the paper: Use only with explicit boundary language.
- Exact caution language: Iterator consumption is expected behavior; the rescue shows the generic no-arg harness missed a real cursor effect.

## 3. pygments `EscapeSequence`

- Original sweep classification: `structural_only_no_runtime_difference`
- Why the generic harness failed or was weak: It used no-argument construction/repeated calls that did not exercise the candidate with meaningful package data.
- Manual fixture built: EscapeSequence(fg='ansired') using Pygments terminal formatter internals.
- Realistic fixture: Yes.
- Result: `structural_only_no_runtime_difference`; output_diff=False, branch_flip=False, state_diff=False.
- Should it be used in the paper: Do not use as a headline paper example.
- Exact caution language: In this Pygments version the ANSI fixture did not trigger the suspected bold mutation; the case remains structural-only.

## 4. docutils `Transformer`

- Original sweep classification: `could_not_construct`
- Why the generic harness failed or was weak: constructor requires arguments: document
- Manual fixture built: docutils new_document with two tiny Transform subclasses.
- Realistic fixture: Yes.
- Result: `confirmed_state_divergence_only`; output_diff=False, branch_flip=False, state_diff=True.
- Should it be used in the paper: Do not use as a headline paper example.
- Exact caution language: The manual fixture tests Transformer serial bookkeeping, not transform application output.

## 5. soupsieve `CSSMatch`

- Original sweep classification: `import_failed`
- Why the generic harness failed or was weak: import_failed: ModuleNotFoundError: No module named 'bs4'
- Manual fixture built: BeautifulSoup tree and soupsieve compiled selector 'p.a'.
- Realistic fixture: Yes.
- Result: `structural_only_no_runtime_difference`; output_diff=False, branch_flip=False, state_diff=False.
- Should it be used in the paper: Do not use as a headline paper example.
- Exact caution language: The rescue only fixes sys.path/import construction; simple selector matching remained output-equivalent.

## 6. beautifulsoup4 `PageElement`

- Original sweep classification: `structural_only_no_runtime_difference`
- Why the generic harness failed or was weak: It used no-argument construction/repeated calls that did not exercise the candidate with meaningful package data.
- Manual fixture built: BeautifulSoup('<p>a</p><p>b</p>', 'html.parser'); Tag is a PageElement subclass.
- Realistic fixture: Yes.
- Result: `confirmed_output_divergence`; output_diff=True, branch_flip=False, state_diff=True.
- Should it be used in the paper: Use only with explicit boundary language.
- Exact caution language: BeautifulSoup extraction is intentionally destructive; use only as a tree-mutation/access-order example.

## 7. boltons `LRI`

- Original sweep classification: `structural_only_no_runtime_difference`
- Why the generic harness failed or was weak: It used no-argument construction/repeated calls that did not exercise the candidate with meaningful package data.
- Manual fixture built: LRI(max_size=2) with keys a, b, c.
- Realistic fixture: Yes.
- Result: `confirmed_state_divergence_only`; output_diff=False, branch_flip=False, state_diff=True.
- Should it be used in the paper: Do not use as a headline paper example.
- Exact caution language: LRI access affects statistics but not eviction order in this fixture.

## 8. boltons `LRU`

- Original sweep classification: `structural_only_no_runtime_difference`
- Why the generic harness failed or was weak: It used no-argument construction/repeated calls that did not exercise the candidate with meaningful package data.
- Manual fixture built: LRU(max_size=2) with keys a, b, c.
- Realistic fixture: Yes.
- Result: `confirmed_output_divergence`; output_diff=True, branch_flip=False, state_diff=True.
- Should it be used in the paper: Use only with explicit boundary language.
- Exact caution language: LRU access affects eviction order as designed; it is evidence of consequential access state, not a defect.

## 9. boltons `MultiFileReader`

- Original sweep classification: `structural_only_no_runtime_difference`
- Why the generic harness failed or was weak: It used no-argument construction/repeated calls that did not exercise the candidate with meaningful package data.
- Manual fixture built: MultiFileReader(BytesIO(b'ab'), BytesIO(b'cd'), BytesIO(b'e')).
- Realistic fixture: Yes.
- Result: `confirmed_output_divergence`; output_diff=True, branch_flip=False, state_diff=True.
- Should it be used in the paper: Use only with explicit boundary language.
- Exact caution language: MultiFileReader is a stream-like cursor; output divergence is expected after a prior read.

## 10. cerberus `BareValidator`

- Original sweep classification: `structural_only_no_runtime_difference`
- Why the generic harness failed or was weak: It used no-argument construction/repeated calls that did not exercise the candidate with meaningful package data.
- Manual fixture built: Public cerberus.Validator subclass with schema {'name': {'type': 'string', 'minlength': 3}}.
- Realistic fixture: Yes.
- Result: `confirmed_output_divergence`; output_diff=True, branch_flip=False, state_diff=True.
- Should it be used in the paper: Use only with explicit boundary language.
- Exact caution language: BareValidator itself rejects schema-backed validation; the runnable fixture uses the public Validator subclass to exercise inherited BareValidator state.

## 11. click-option-group `_OptGroup`

- Original sweep classification: `structural_only_no_runtime_difference`
- Why the generic harness failed or was weak: It used no-argument construction/repeated calls that did not exercise the candidate with meaningful package data.
- Manual fixture built: Tiny Click command using click-option-group public optgroup helpers and CliRunner.
- Realistic fixture: Yes.
- Result: `structural_only_no_runtime_difference`; output_diff=False, branch_flip=False, state_diff=False.
- Should it be used in the paper: Do not use as a headline paper example.
- Exact caution language: The decorator fixture is tiny and in-process; it did not produce a meaningful runtime divergence.

## 12. dnspython `BTree`

- Original sweep classification: `structural_only_no_runtime_difference`
- Why the generic harness failed or was weak: It used no-argument construction/repeated calls that did not exercise the candidate with meaningful package data.
- Manual fixture built: BTree populated with dns.btree.KV('a','A') and KV('b','B').
- Realistic fixture: Yes.
- Result: `structural_only_no_runtime_difference`; output_diff=False, branch_flip=False, state_diff=False.
- Should it be used in the paper: Do not use as a headline paper example.
- Exact caution language: BTree lookup is stable under this minimal fixture; cursor/copy-on-write behavior was not forced.

## 13. dnspython `Tokenizer`

- Original sweep classification: `confirmed_state_divergence_only`
- Why the generic harness failed or was weak: It used no-argument construction/repeated calls that did not exercise the candidate with meaningful package data.
- Manual fixture built: dns.tokenizer.Tokenizer over io.StringIO('alpha beta\n').
- Realistic fixture: Yes.
- Result: `confirmed_output_divergence`; output_diff=True, branch_flip=False, state_diff=True.
- Should it be used in the paper: Use only with explicit boundary language.
- Exact caution language: Tokenizer is a cursor over token input; output divergence is expected after consuming a token.

## 14. h11 `ChunkedReader`

- Original sweep classification: `structural_only_no_runtime_difference`
- Why the generic harness failed or was weak: It used no-argument construction/repeated calls that did not exercise the candidate with meaningful package data.
- Manual fixture built: h11 ReceiveBuffer containing a complete chunked body b'3\r\nabc\r\n0\r\n\r\n'.
- Realistic fixture: Yes.
- Result: `confirmed_output_divergence`; output_diff=True, branch_flip=False, state_diff=True.
- Should it be used in the paper: Use only with explicit boundary language.
- Exact caution language: ChunkedReader consumes a ReceiveBuffer; Data versus EndOfMessage is expected stream-reader state.

## 15. h11 `ReceiveBuffer`

- Original sweep classification: `structural_only_no_runtime_difference`
- Why the generic harness failed or was weak: It used no-argument construction/repeated calls that did not exercise the candidate with meaningful package data.
- Manual fixture built: ReceiveBuffer containing HTTP-like header bytes.
- Realistic fixture: Yes.
- Result: `confirmed_output_divergence`; output_diff=True, branch_flip=False, state_diff=False.
- Should it be used in the paper: Use only with explicit boundary language.
- Exact caution language: ReceiveBuffer line extraction is destructive by design; it is a cursor semantics example.

