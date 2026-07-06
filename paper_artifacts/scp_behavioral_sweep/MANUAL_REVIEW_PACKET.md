# Manual Review Packet

## 1. markdown `Markdown`

- Path: `markdown-3.10.2\markdown\core.py`
- Score: 12
- Selection reason: +4 likely true positive; +2 read/getter-like mutation; +2 observer/repr/logging/debug-like mutation; +2 later/cache/branch/composition hint; +1 simple constructor; +1 source import path available
- Suspected observer/read operation: `build_parser`
- Suspected latent state: `inlinePatterns,parser,postprocessors,preprocessors,treeprocessors`
- Suspected later read/behavior: repeat the same read-shaped operation and compare result/state
- Harness classification: `structural_only_no_runtime_difference`
- Result A summary: {"after": {"ESCAPED_CHARS": "['\\\\', '`', '*', '_', '{', '}', '[', ']', '(', ')', '>', '#', '+', '-', '.', '!']", "block_level_elements": "['address', 'article', 'aside', 'blockquote', 'details', 'div', 'dl', 'fieldset', 'figcaption', 'figure', 'footer', 'form', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6...
- Result B summary: {"after": {"ESCAPED_CHARS": "['\\\\', '`', '*', '_', '{', '}', '[', ']', '(', ')', '>', '#', '+', '-', '.', '!']", "block_level_elements": "['address', 'article', 'aside', 'blockquote', 'details', 'div', 'dl', 'fieldset', 'figcaption', 'figure', 'footer', 'form', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6...
- Failure reason: 

```python
41: 
42: 
43: logger = logging.getLogger('MARKDOWN')
44: 
45: 
46: class Markdown:
47:     """
48:     A parser which converts Markdown to HTML.
49: 
50:     Attributes:
51:         Markdown.tab_length (int): The number of spaces which correspond to a single tab. Default: `4`.
52:         Markdown.ESCAPED_CHARS (list[str]): List of characters which get the backslash escape treatment.
53:         Markdown.block_level_elements (list[str]): List of HTML tags which get treated as block-level elements.
54:             See [`markdown.util.BLOCK_LEVEL_ELEMENTS`][] for the full list of elements.
55:         Markdown.registeredExtensions (list[Extension]): List of extensions which have called
56:             [`registerExtension`][markdown.Markdown.registerExtension] during setup.
57:         Markdown.doc_tag (str): Element used to wrap document. Default: `div`.
58:         Markdown.stripTopLevelTags (bool): Indicates whether the `doc_tag` should be removed. Default: 'True'.
59:         Markdown.references (dict[str, tuple[str, str]]): A mapping of link references found in a parsed document
60:              where the key is the reference name and the value is a tuple of the URL and title.
61:         Markdown.htmlStash (util.HtmlStash): The instance of the `HtmlStash` used by an instance of this class.
62:         Markdown.output_formats (dict[str, Callable[xml.etree.ElementTree.Element]]): A mapping of known output
63:              formats by name and their respective serializers. Each serializer must be a callable which accepts an
64:             [`Element`][xml.etree.ElementTree.Element] and returns a `str`.
65:         Markdown.output_format (str): The output format set by
66:             [`set_output_format`][markdown.Markdown.set_output_format].
67:         Markdown.serializer (Callable[xml.etree.ElementTree.Element]): The serializer set by
68:             [`set_output_format`][markdown.Markdown.set_output_format].
69:         Markdown.preprocessors (util.Registry): A collection of [`preprocessors`][markdown.preprocessors].
70:         Markdown.parser (blockparser.BlockParser): A collection of [`blockprocessors`][markdown.blockprocessors].
71:         Markdown.inlinePatterns (util.Registry): A collection of [`inlinepatterns`][markdown.inlinepatterns].
72:         Markdown.treeprocessors (util.Registry): A collection of [`treeprocessors`][markdown.treeprocessors].
73:         Markdown.postprocessors (util.Registry): A collection of [`postprocessors`][markdown.postprocessors].
74: 
75:     """
76: 
77:     doc_tag = "div"     # Element used to wrap document - later removed
78: 
79:     output_formats: ClassVar[dict[str, Callable[[Element], str]]] = {
80:         'html':   to_html_string,
```

## 2. more-itertools `seekable`

- Path: `more_itertools-11.0.2\more_itertools\more.py`
- Score: 12
- Selection reason: +4 likely true positive; +3 HIGH; +2 read/getter-like mutation; +2 later/cache/branch/composition hint; +1 source import path available
- Suspected observer/read operation: `__next__`
- Suspected latent state: `_index`
- Suspected later read/behavior: repeat the same read-shaped operation and compare result/state
- Harness classification: `could_not_construct`
- Result A summary: {}
- Result B summary: {}
- Failure reason: constructor requires arguments: iterable

```python
2912: 
2913:     def __repr__(self):
2914:         return f'{self.__class__.__name__}({self._target!r})'
2915: 
2916: 
2917: class seekable:
2918:     """Wrap an iterator to allow for seeking backward and forward. This
2919:     progressively caches the items in the source iterable so they can be
2920:     re-visited.
2921: 
2922:     Call :meth:`seek` with an index to seek to that position in the source
2923:     iterable.
2924: 
2925:     To "reset" an iterator, seek to ``0``:
2926: 
2927:         >>> from itertools import count
2928:         >>> it = seekable((str(n) for n in count()))
2929:         >>> next(it), next(it), next(it)
2930:         ('0', '1', '2')
2931:         >>> it.seek(0)
2932:         >>> next(it), next(it), next(it)
2933:         ('0', '1', '2')
2934: 
2935:     You can also seek forward:
2936: 
2937:         >>> it = seekable((str(n) for n in range(20)))
2938:         >>> it.seek(10)
2939:         >>> next(it)
2940:         '10'
2941:         >>> it.seek(20)  # Seeking past the end of the source isn't a problem
2942:         >>> list(it)
2943:         []
2944:         >>> it.seek(0)  # Resetting works even after hitting the end
2945:         >>> next(it)
2946:         '0'
2947: 
2948:     Call :meth:`relative_seek` to seek relative to the source iterator's
2949:     current position.
2950: 
2951:         >>> it = seekable((str(n) for n in range(20)))
```

## 3. pygments `EscapeSequence`

- Path: `pygments-2.20.0\pygments\formatters\terminal256.py`
- Score: 12
- Selection reason: +4 likely true positive; +2 read/getter-like mutation; +2 observer/repr/logging/debug-like mutation; +2 later/cache/branch/composition hint; +1 simple constructor; +1 source import path available
- Suspected observer/read operation: `color_string`
- Suspected latent state: `bold`
- Suspected later read/behavior: repeat the same read-shaped operation and compare result/state
- Harness classification: `structural_only_no_runtime_difference`
- Result A summary: {"after": {"bg": "None", "bold": "False", "fg": "None", "italic": "False", "underline": "False"}, "before": {"bg": "None", "bold": "False", "fg": "None", "italic": "False", "underline": "False"}, "result": {"kind": "value", "value": "''"}}
- Result B summary: {"after": {"bg": "None", "bold": "False", "fg": "None", "italic": "False", "underline": "False"}, "after_observation": {"bg": "None", "bold": "False", "fg": "None", "italic": "False", "underline": "False"}, "before": {"bg": "None", "bold": "False", "fg": "None", "italic": "False", "underline": "F...
- Failure reason: 

```python
29: 
30: 
31: __all__ = ['Terminal256Formatter', 'TerminalTrueColorFormatter']
32: 
33: 
34: class EscapeSequence:
35:     def __init__(self, fg=None, bg=None, bold=False, underline=False, italic=False):
36:         self.fg = fg
37:         self.bg = bg
38:         self.bold = bold
39:         self.underline = underline
40:         self.italic = italic
41: 
42:     def escape(self, attrs):
43:         if len(attrs):
44:             return "\x1b[" + ";".join(attrs) + "m"
45:         return ""
46: 
47:     def color_string(self):
48:         attrs = []
49:         if self.fg is not None:
50:             if self.fg in ansicolors:
51:                 esc = codes[self.fg.replace('ansi','')]
52:                 if ';01m' in esc:
53:                     self.bold = True
54:                 # extract fg color code.
55:                 attrs.append(esc[2:4])
56:             else:
57:                 attrs.extend(("38", "5", "%i" % self.fg))
58:         if self.bg is not None:
59:             if self.bg in ansicolors:
60:                 esc = codes[self.bg.replace('ansi','')]
61:                 # extract fg color code, add 10 for bg.
62:                 attrs.append(str(int(esc[2:4])+10))
63:             else:
64:                 attrs.extend(("48", "5", "%i" % self.bg))
65:         if self.bold:
66:             attrs.append("01")
67:         if self.underline:
68:             attrs.append("04")
```

## 4. docutils `Transformer`

- Path: `docutils-0.22.4\docutils\transforms\__init__.py`
- Score: 11
- Selection reason: +4 likely true positive; +2 read/getter-like mutation; +2 observer/repr/logging/debug-like mutation; +2 later/cache/branch/composition hint; +1 source import path available
- Suspected observer/read operation: `get_priority_string`
- Suspected latent state: `serialno`
- Suspected later read/behavior: repeat the same read-shaped operation and compare result/state
- Harness classification: `could_not_construct`
- Result A summary: {}
- Result B summary: {}
- Failure reason: constructor requires arguments: document

```python
60:     def apply(self, **kwargs):
61:         """Override to apply the transform to the document tree."""
62:         raise NotImplementedError('subclass must override this method')
63: 
64: 
65: class Transformer(TransformSpec):
66:     """
67:     Store "transforms" and apply them to the document tree.
68: 
69:     Collect lists of `Transform` instances from Docutils
70:     components (`TransformSpec` instances).
71:     Apply collected "transforms" to the document tree.
72: 
73:     Also keeps track of components by component type name.
74: 
75:     https://docutils.sourceforge.io/docs/peps/pep-0258.html#transformer
76:     """
77: 
78:     def __init__(self, document) -> None:
79:         self.transforms = []
80:         """List of transforms to apply.  Each item is a 4-tuple:
81:         ``(priority string, transform class, pending node or None, kwargs)``.
82:         """
83: 
84:         self.unknown_reference_resolvers = []
85:         """List of hook functions which assist in resolving references.
86: 
87:         Deprecated. Will be removed in Docutils 1.0.
88:         """
89: 
90:         self.document = document
91:         """The `nodes.document` object this Transformer is attached to."""
92: 
93:         self.applied = []
94:         """Transforms already applied, in order."""
95: 
96:         self.sorted = False
97:         """Boolean: is `self.tranforms` sorted?"""
98: 
99:         self.components = {}
```

## 5. soupsieve `CSSMatch`

- Path: `soupsieve-2.8.3\soupsieve\css_match.py`
- Score: 11
- Selection reason: +4 likely true positive; +2 read/getter-like mutation; +2 observer/repr/logging/debug-like mutation; +2 later/cache/branch/composition hint; +1 source import path available
- Suspected observer/read operation: `match_selectors`
- Suspected latent state: `iframe_restrict,namespaces`
- Suspected later read/behavior: repeat the same read-shaped operation and compare result/state
- Harness classification: `import_failed`
- Result A summary: {}
- Result B summary: {}
- Failure reason: import_failed: ModuleNotFoundError: No module named 'bs4'

```python
539:             if m:
540:                 parsed = (float(m.group('value')),)
541:         return parsed
542: 
543: 
544: class CSSMatch(_DocumentNav):
545:     """Perform CSS matching."""
546: 
547:     def __init__(
548:         self,
549:         selectors: ct.SelectorList,
550:         scope: bs4.Tag | None,
551:         namespaces: ct.Namespaces | None,
552:         flags: int
553:     ) -> None:
554:         """Initialize."""
555: 
556:         self.assert_valid_input(scope)
557:         self.tag = scope
558:         self.cached_meta_lang = []  # type: list[tuple[str, str]]
559:         self.cached_default_forms = []  # type: list[tuple[bs4.Tag, bs4.Tag]]
560:         self.cached_indeterminate_forms = []  # type: list[tuple[bs4.Tag, str, bool]]
561:         self.selectors = selectors
562:         self.namespaces = {} if namespaces is None else namespaces  # type: ct.Namespaces | dict[str, str]
563:         self.flags = flags
564:         self.iframe_restrict = False
565: 
566:         # Find the root element for the whole tree
567:         doc = scope
568:         parent = self.get_parent(doc)
569:         while parent:
570:             doc = parent
571:             parent = self.get_parent(doc)
572:         root = None  # type: bs4.Tag | None
573:         if not self.is_doc(doc):
574:             root = doc
575:         else:
576:             for child in self.get_tag_children(doc):
577:                 root = child
578:                 break
```

## 6. anyio `CancelScope`

- Path: `anyio-4.13.0\src\anyio\_backends\_asyncio.py`
- Score: 10
- Selection reason: +4 likely true positive; +2 read/getter-like mutation; +2 later/cache/branch/composition hint; +1 simple constructor; +1 source import path available
- Suspected observer/read operation: `__enter__`
- Suspected latent state: `_active,_host_task,_parent_scope`
- Suspected later read/behavior: repeat the same read-shaped operation and compare result/state
- Harness classification: `structural_only_no_runtime_difference`
- Result A summary: {"after": {"_active": "False", "_cancel_called": "False", "_cancel_handle": "None", "_cancel_reason": "None", "_cancelled_caught": "False", "_child_scopes": "set()", "_deadline": "inf", "_host_task": "None", "_parent_scope": "None", "_pending_uncancellations": "0", "_shield": "False", "_tasks": "...
- Result B summary: {"after": {"_active": "False", "_cancel_called": "False", "_cancel_handle": "None", "_cancel_reason": "None", "_cancelled_caught": "False", "_child_scopes": "set()", "_deadline": "inf", "_host_task": "None", "_parent_scope": "None", "_pending_uncancellations": "0", "_shield": "False", "_tasks": "...
- Failure reason: 

```python
384:             continue
385: 
386:         return False
387: 
388: 
389: class CancelScope(BaseCancelScope):
390:     def __new__(
391:         cls, *, deadline: float = math.inf, shield: bool = False
392:     ) -> CancelScope:
393:         return object.__new__(cls)
394: 
395:     def __init__(self, deadline: float = math.inf, shield: bool = False):
396:         self._deadline = deadline
397:         self._shield = shield
398:         self._parent_scope: CancelScope | None = None
399:         self._child_scopes: set[CancelScope] = set()
400:         self._cancel_called = False
401:         self._cancel_reason: str | None = None
402:         self._cancelled_caught = False
403:         self._active = False
404:         self._timeout_handle: asyncio.TimerHandle | None = None
405:         self._cancel_handle: asyncio.Handle | None = None
406:         self._tasks: set[asyncio.Task] = set()
407:         self._host_task: asyncio.Task | None = None
408:         if sys.version_info >= (3, 11):
409:             self._pending_uncancellations: int | None = 0
410:         else:
411:             self._pending_uncancellations = None
412: 
413:     def __enter__(self) -> CancelScope:
414:         if self._active:
415:             raise RuntimeError(
416:                 "Each CancelScope may only be used for a single 'with' block"
417:             )
418: 
419:         self._host_task = host_task = cast(asyncio.Task, current_task())
420:         self._tasks.add(host_task)
421:         try:
422:             task_state = _task_states[host_task]
423:         except KeyError:
```

## 7. anyio `Runner`

- Path: `anyio-4.13.0\src\anyio\_backends\_asyncio.py`
- Score: 10
- Selection reason: +4 likely true positive; +2 read/getter-like mutation; +2 later/cache/branch/composition hint; +1 simple constructor; +1 source import path available
- Suspected observer/read operation: `run`
- Suspected latent state: `_interrupt_count`
- Suspected later read/behavior: repeat the same read-shaped operation and compare result/state
- Harness classification: `structural_only_no_runtime_difference`
- Result A summary: {"after": {"_context": "None", "_debug": "None", "_interrupt_count": "0", "_loop": "None", "_loop_factory": "None", "_set_event_loop": "False", "_state": "<_State.CREATED: 'created'>"}, "before": {"_context": "None", "_debug": "None", "_interrupt_count": "0", "_loop": "None", "_loop_factory": "No...
- Result B summary: {"after": {"_context": "None", "_debug": "None", "_interrupt_count": "0", "_loop": "None", "_loop_factory": "None", "_set_event_loop": "False", "_state": "<_State.CREATED: 'created'>"}, "after_observation": {"_context": "None", "_debug": "None", "_interrupt_count": "0", "_loop": "None", "_loop_fa...
- Failure reason: 

```python
123:     class _State(enum.Enum):
124:         CREATED = "created"
125:         INITIALIZED = "initialized"
126:         CLOSED = "closed"
127: 
128:     class Runner:
129:         # Copied from CPython 3.11
130:         def __init__(
131:             self,
132:             *,
133:             debug: bool | None = None,
134:             loop_factory: Callable[[], AbstractEventLoop] | None = None,
135:         ):
136:             self._state = _State.CREATED
137:             self._debug = debug
138:             self._loop_factory = loop_factory
139:             self._loop: AbstractEventLoop | None = None
140:             self._context = None
141:             self._interrupt_count = 0
142:             self._set_event_loop = False
143: 
144:         def __enter__(self) -> Runner:
145:             self._lazy_init()
146:             return self
147: 
148:         def __exit__(
149:             self,
150:             exc_type: type[BaseException] | None,
151:             exc_val: BaseException | None,
152:             exc_tb: TracebackType | None,
153:         ) -> None:
154:             self.close()
155: 
156:         def close(self) -> None:
157:             """Shutdown and close event loop."""
158:             loop = self._loop
159:             if self._state is not _State.INITIALIZED or loop is None:
160:                 return
161:             try:
162:                 _cancel_all_tasks(loop)
```

## 8. anyio `ContextManagerMixin`

- Path: `anyio-4.13.0\src\anyio\_core\_contextmanagers.py`
- Score: 10
- Selection reason: +4 likely true positive; +2 read/getter-like mutation; +2 later/cache/branch/composition hint; +1 simple constructor; +1 source import path available
- Suspected observer/read operation: `__enter__`
- Suspected latent state: `__cm`
- Suspected later read/behavior: repeat the same read-shaped operation and compare result/state
- Harness classification: `structural_only_no_runtime_difference`
- Result A summary: {"after": {}, "before": {}, "result": {"kind": "exception", "message": "__contextmanager__() did not return a context manager object, but <class 'NoneType'>", "type": "TypeError"}}
- Result B summary: {"after": {}, "after_observation": {}, "before": {}, "observation_result": {"kind": "exception", "message": "__contextmanager__() did not return a context manager object, but <class 'NoneType'>", "type": "TypeError"}, "result": {"kind": "exception", "message": "__contextmanager__() did not return...
- Failure reason: 

```python
18:     def __asynccontextmanager__(
19:         self,
20:     ) -> AbstractAsyncContextManager[_T_co, _ExitT_co]: ...
21: 
22: 
23: class ContextManagerMixin:
24:     """
25:     Mixin class providing context manager functionality via a generator-based
26:     implementation.
27: 
28:     This class allows you to implement a context manager via :meth:`__contextmanager__`
29:     which should return a generator. The mechanics are meant to mirror those of
30:     :func:`@contextmanager <contextlib.contextmanager>`.
31: 
32:     .. note:: Classes using this mix-in are not reentrant as context managers, meaning
33:         that once you enter it, you can't re-enter before first exiting it.
34: 
35:     .. seealso:: :doc:`contextmanagers`
36:     """
37: 
38:     __cm: AbstractContextManager[object, bool | None] | None = None
39: 
40:     @final
41:     def __enter__(self: _SupportsCtxMgr[_T_co, bool | None]) -> _T_co:
42:         # Needed for mypy to assume self still has the __cm member
43:         assert isinstance(self, ContextManagerMixin)
44:         if self.__cm is not None:
45:             raise RuntimeError(
46:                 f"this {self.__class__.__qualname__} has already been entered"
47:             )
48: 
49:         cm = self.__contextmanager__()
50:         if not isinstance(cm, AbstractContextManager):
51:             if isgenerator(cm):
52:                 raise TypeError(
53:                     "__contextmanager__() returned a generator object instead of "
54:                     "a context manager. Did you forget to add the @contextmanager "
55:                     "decorator?"
56:                 )
57: 
```

## 9. anyio `BlockingPortalProvider`

- Path: `anyio-4.13.0\src\anyio\from_thread.py`
- Score: 10
- Selection reason: +4 likely true positive; +2 read/getter-like mutation; +2 later/cache/branch/composition hint; +1 simple constructor; +1 source import path available
- Suspected observer/read operation: `__enter__`
- Suspected latent state: `_leases,_portal,_portal_cm`
- Suspected later read/behavior: repeat the same read-shaped operation and compare result/state
- Harness classification: `confirmed_state_divergence_only`
- Result A summary: {"after": {"_leases": "1", "_lock": "<unlocked _thread.lock object at 0xADDR>", "_portal": "<anyio.from_thread.BlockingPortal object at 0xADDR>", "_portal_cm": "<contextlib._GeneratorContextManager object at 0xADDR>", "backend": "'asyncio'", "backend_options": "None"}, "before": {"_lock": "<unloc...
- Result B summary: {"after": {"_leases": "2", "_lock": "<unlocked _thread.lock object at 0xADDR>", "_portal": "<anyio.from_thread.BlockingPortal object at 0xADDR>", "_portal_cm": "<contextlib._GeneratorContextManager object at 0xADDR>", "backend": "'asyncio'", "backend_options": "None"}, "after_observation": {"_lea...
- Failure reason: 

```python
438:         """
439:         return _BlockingAsyncContextManager(cm, self)
440: 
441: 
442: @dataclass
443: class BlockingPortalProvider:
444:     """
445:     A manager for a blocking portal. Used as a context manager. The first thread to
446:     enter this context manager causes a blocking portal to be started with the specific
447:     parameters, and the last thread to exit causes the portal to be shut down. Thus,
448:     there will be exactly one blocking portal running in this context as long as at
449:     least one thread has entered this context manager.
450: 
451:     The parameters are the same as for :func:`~anyio.run`.
452: 
453:     :param backend: name of the backend
454:     :param backend_options: backend options
455: 
456:     .. versionadded:: 4.4
457:     """
458: 
459:     backend: str = "asyncio"
460:     backend_options: dict[str, Any] | None = None
461:     _lock: Lock = field(init=False, default_factory=Lock)
462:     _leases: int = field(init=False, default=0)
463:     _portal: BlockingPortal = field(init=False)
464:     _portal_cm: AbstractContextManager[BlockingPortal] | None = field(
465:         init=False, default=None
466:     )
467: 
468:     def __enter__(self) -> BlockingPortal:
469:         with self._lock:
470:             if self._portal_cm is None:
471:                 self._portal_cm = start_blocking_portal(
472:                     self.backend, self.backend_options
473:                 )
474:                 self._portal = self._portal_cm.__enter__()
475: 
476:             self._leases += 1
477:             return self._portal
```

## 10. beautifulsoup4 `HTML5TreeBuilder`

- Path: `beautifulsoup4-4.14.3\bs4\builder\_html5lib.py`
- Score: 10
- Selection reason: +4 likely true positive; +2 read/getter-like mutation; +2 later/cache/branch/composition hint; +1 simple constructor; +1 source import path available
- Suspected observer/read operation: `create_treebuilder`
- Suspected latent state: `underlying_builder`
- Suspected later read/behavior: repeat the same read-shaped operation and compare result/state
- Harness classification: `import_failed`
- Result A summary: {}
- Result B summary: {}
- Failure reason: import_failed: ModuleNotFoundError: No module named 'html5lib'

```python
54:     from bs4 import BeautifulSoup
55: 
56: from html5lib.treebuilders import base as treebuilder_base
57: 
58: 
59: class HTML5TreeBuilder(HTMLTreeBuilder):
60:     """Use `html5lib <https://github.com/html5lib/html5lib-python>`_ to
61:     build a tree.
62: 
63:     Note that `HTML5TreeBuilder` does not support some common HTML
64:     `TreeBuilder` features. Some of these features could theoretically
65:     be implemented, but at the very least it's quite difficult,
66:     because html5lib moves the parse tree around as it's being built.
67: 
68:     Specifically:
69: 
70:     * This `TreeBuilder` doesn't use different subclasses of
71:       `NavigableString` (e.g. `Script`) based on the name of the tag
72:       in which the string was found.
73:     * You can't use a `SoupStrainer` to parse only part of a document.
74:     """
75: 
76:     NAME: str = "html5lib"
77: 
78:     features: Iterable[str] = [NAME, PERMISSIVE, HTML_5, HTML]
79: 
80:     #: html5lib can tell us which line number and position in the
81:     #: original file is the source of an element.
82:     TRACKS_LINE_NUMBERS: bool = True
83: 
84:     underlying_builder: "TreeBuilderForHtml5lib"  #: :meta private:
85:     user_specified_encoding: Optional[_Encoding]
86: 
87:     def prepare_markup(
88:         self,
89:         markup: _RawMarkup,
90:         user_specified_encoding: Optional[_Encoding] = None,
91:         document_declared_encoding: Optional[_Encoding] = None,
92:         exclude_encodings: Optional[_Encodings] = None,
93:     ) -> Iterable[Tuple[_RawMarkup, Optional[_Encoding], Optional[_Encoding], bool]]:
```

## 11. beautifulsoup4 `PageElement`

- Path: `beautifulsoup4-4.14.3\bs4\element.py`
- Score: 10
- Selection reason: +4 likely true positive; +2 read/getter-like mutation; +2 later/cache/branch/composition hint; +1 simple constructor; +1 source import path available
- Suspected observer/read operation: `extract`
- Suspected latent state: `next_sibling,parent,previous_element,previous_sibling`
- Suspected later read/behavior: repeat the same read-shaped operation and compare result/state
- Harness classification: `structural_only_no_runtime_difference`
- Result A summary: {"after": {}, "before": {}, "result": {"kind": "exception", "message": "'PageElement' object has no attribute 'parent'", "type": "AttributeError"}}
- Result B summary: {"after": {}, "after_observation": {}, "before": {}, "observation_result": {"kind": "exception", "message": "'PageElement' object has no attribute 'parent'", "type": "AttributeError"}, "result": {"kind": "exception", "message": "'PageElement' object has no attribute 'parent'", "type": "AttributeE...
- Failure reason: 

```python
347:             return match.group(1) + eventual_encoding
348: 
349:         return self.CHARSET_RE.sub(rewrite, self.original_value)
350: 
351: 
352: class PageElement(object):
353:     """An abstract class representing a single element in the parse tree.
354: 
355:     `NavigableString`, `Tag`, etc. are all subclasses of
356:     `PageElement`. For this reason you'll see a lot of methods that
357:     return `PageElement`, but you'll never see an actual `PageElement`
358:     object. For the most part you can think of `PageElement` as
359:     meaning "a `Tag` or a `NavigableString`."
360:     """
361: 
362:     #: In general, we can't tell just by looking at an element whether
363:     #: it's contained in an XML document or an HTML document. But for
364:     #: `Tag` objects (q.v.) we can store this information at parse time.
365:     #: :meta private:
366:     known_xml: Optional[bool] = None
367: 
368:     #: Whether or not this element has been decomposed from the tree
369:     #: it was created in.
370:     _decomposed: bool
371: 
372:     parent: Optional[Tag]
373:     next_element: _AtMostOneElement
374:     previous_element: _AtMostOneElement
375:     next_sibling: _AtMostOneElement
376:     previous_sibling: _AtMostOneElement
377: 
378:     #: Whether or not this element is hidden from generated output.
379:     #: Only the `BeautifulSoup` object itself is hidden.
380:     hidden: bool = False
381: 
382:     def setup(
383:         self,
384:         parent: Optional[Tag] = None,
385:         previous_element: _AtMostOneElement = None,
386:         next_element: _AtMostOneElement = None,
```

## 12. boltons `LRI`

- Path: `boltons-25.0.0\boltons\cacheutils.py`
- Score: 10
- Selection reason: +4 likely true positive; +2 read/getter-like mutation; +2 later/cache/branch/composition hint; +1 simple constructor; +1 source import path available
- Suspected observer/read operation: `_set_key_and_evict_last_in_ll`
- Suspected latent state: `_anchor`
- Suspected later read/behavior: repeat the same read-shaped operation and compare result/state
- Harness classification: `structural_only_no_runtime_difference`
- Result A summary: {"after": {"_anchor": "[[...], [...], _MISSING, _MISSING]", "_link_lookup": "{}", "_lock": "<unlocked _thread.RLock object owner=0 count=0 at 0xADDR>", "hit_count": "0", "max_size": "128", "miss_count": "0", "on_miss": "None", "soft_miss_count": "0"}, "before": {"_anchor": "[[...], [...], _MISSIN...
- Result B summary: {"after": {"_anchor": "[[...], [...], _MISSING, _MISSING]", "_link_lookup": "{}", "_lock": "<unlocked _thread.RLock object owner=0 count=0 at 0xADDR>", "hit_count": "0", "max_size": "128", "miss_count": "0", "on_miss": "None", "soft_miss_count": "0"}, "after_observation": {"_anchor": "[[...], [.....
- Failure reason: 

```python
89: 
90: PREV, NEXT, KEY, VALUE = range(4)   # names for the link fields
91: DEFAULT_MAX_SIZE = 128
92: 
93: 
94: class LRI(dict):
95:     """The ``LRI`` implements the basic *Least Recently Inserted* strategy to
96:     caching. One could also think of this as a ``SizeLimitedDefaultDict``.
97: 
98:     *on_miss* is a callable that accepts the missing key (as opposed
99:     to :class:`collections.defaultdict`'s "default_factory", which
100:     accepts no arguments.) Also note that, like the :class:`LRI`,
101:     the ``LRI`` is instrumented with statistics tracking.
102: 
103:     >>> cap_cache = LRI(max_size=2)
104:     >>> cap_cache['a'], cap_cache['b'] = 'A', 'B'
105:     >>> from pprint import pprint as pp
106:     >>> pp(dict(cap_cache))
107:     {'a': 'A', 'b': 'B'}
108:     >>> [cap_cache['b'] for i in range(3)][0]
109:     'B'
110:     >>> cap_cache['c'] = 'C'
111:     >>> print(cap_cache.get('a'))
112:     None
113:     >>> cap_cache.hit_count, cap_cache.miss_count, cap_cache.soft_miss_count
114:     (3, 1, 1)
115:     """
116:     def __init__(self, max_size=DEFAULT_MAX_SIZE, values=None,
117:                  on_miss=None):
118:         if max_size <= 0:
119:             raise ValueError('expected max_size > 0, not %r' % max_size)
120:         self.hit_count = self.miss_count = self.soft_miss_count = 0
121:         self.max_size = max_size
122:         self._lock = RLock()
123:         self._init_ll()
124: 
125:         if on_miss is not None and not callable(on_miss):
126:             raise TypeError('expected on_miss to be a callable'
127:                             ' (or None), not %r' % on_miss)
128:         self.on_miss = on_miss
```

## 13. boltons `LRU`

- Path: `boltons-25.0.0\boltons\cacheutils.py`
- Score: 10
- Selection reason: +4 likely true positive; +2 read/getter-like mutation; +2 later/cache/branch/composition hint; +1 simple constructor; +1 source import path available
- Suspected observer/read operation: `__getitem__`
- Suspected latent state: `hit_count,miss_count`
- Suspected later read/behavior: repeat the same read-shaped operation and compare result/state
- Harness classification: `structural_only_no_runtime_difference`
- Result A summary: {"after": {"_anchor": "[[...], [...], _MISSING, _MISSING]", "_link_lookup": "{}", "_lock": "<unlocked _thread.RLock object owner=0 count=0 at 0xADDR>", "hit_count": "0", "max_size": "128", "miss_count": "0", "on_miss": "None", "soft_miss_count": "0"}, "before": {"_anchor": "[[...], [...], _MISSIN...
- Result B summary: {"after": {"_anchor": "[[...], [...], _MISSING, _MISSING]", "_link_lookup": "{}", "_lock": "<unlocked _thread.RLock object owner=0 count=0 at 0xADDR>", "hit_count": "0", "max_size": "128", "miss_count": "0", "on_miss": "None", "soft_miss_count": "0"}, "after_observation": {"_anchor": "[[...], [.....
- Failure reason: 

```python
327:         val_map = super().__repr__()
328:         return ('%s(max_size=%r, on_miss=%r, values=%s)'
329:                 % (cn, self.max_size, self.on_miss, val_map))
330: 
331: 
332: class LRU(LRI):
333:     """The ``LRU`` is :class:`dict` subtype implementation of the
334:     *Least-Recently Used* caching strategy.
335: 
336:     Args:
337:         max_size (int): Max number of items to cache. Defaults to ``128``.
338:         values (iterable): Initial values for the cache. Defaults to ``None``.
339:         on_miss (callable): a callable which accepts a single argument, the
340:             key not present in the cache, and returns the value to be cached.
341: 
342:     >>> cap_cache = LRU(max_size=2)
343:     >>> cap_cache['a'], cap_cache['b'] = 'A', 'B'
344:     >>> from pprint import pprint as pp
345:     >>> pp(dict(cap_cache))
346:     {'a': 'A', 'b': 'B'}
347:     >>> [cap_cache['b'] for i in range(3)][0]
348:     'B'
349:     >>> cap_cache['c'] = 'C'
350:     >>> print(cap_cache.get('a'))
351:     None
352: 
353:     This cache is also instrumented with statistics
354:     collection. ``hit_count``, ``miss_count``, and ``soft_miss_count``
355:     are all integer members that can be used to introspect the
356:     performance of the cache. ("Soft" misses are misses that did not
357:     raise :exc:`KeyError`, e.g., ``LRU.get()`` or ``on_miss`` was used to
358:     cache a default.
359: 
360:     >>> cap_cache.hit_count, cap_cache.miss_count, cap_cache.soft_miss_count
361:     (3, 1, 1)
362: 
363:     Other than the size-limiting caching behavior and statistics,
364:     ``LRU`` acts like its parent class, the built-in Python :class:`dict`.
365:     """
366:     def __getitem__(self, key):
```

## 14. boltons `MultiFileReader`

- Path: `boltons-25.0.0\boltons\ioutils.py`
- Score: 10
- Selection reason: +4 likely true positive; +2 read/getter-like mutation; +2 later/cache/branch/composition hint; +1 simple constructor; +1 source import path available
- Suspected observer/read operation: `read`
- Suspected latent state: `_index`
- Suspected later read/behavior: repeat the same read-shaped operation and compare result/state
- Harness classification: `structural_only_no_runtime_difference`
- Result A summary: {"after": {"_fileobjs": "()", "_index": "0", "_joiner": "''"}, "before": {"_fileobjs": "()", "_index": "0", "_joiner": "''"}, "result": {"kind": "value", "value": "''"}}
- Result B summary: {"after": {"_fileobjs": "()", "_index": "0", "_joiner": "''"}, "after_observation": {"_fileobjs": "()", "_index": "0", "_joiner": "''"}, "before": {"_fileobjs": "()", "_index": "0", "_joiner": "''"}, "observation_result": {"kind": "value", "value": "''"}, "result": {"kind": "value", "value": "''"}}
- Failure reason: 

```python
520:         except Exception:
521:             pass
522:     return False
523: 
524: 
525: class MultiFileReader:
526:     """Takes a list of open files or file-like objects and provides an
527:     interface to read from them all contiguously. Like
528:     :func:`itertools.chain()`, but for reading files.
529: 
530:        >>> mfr = MultiFileReader(BytesIO(b'ab'), BytesIO(b'cd'), BytesIO(b'e'))
531:        >>> mfr.read(3).decode('ascii')
532:        u'abc'
533:        >>> mfr.read(3).decode('ascii')
534:        u'de'
535: 
536:     The constructor takes as many fileobjs as you hand it, and will
537:     raise a TypeError on non-file-like objects. A ValueError is raised
538:     when file-like objects are a mix of bytes- and text-handling
539:     objects (for instance, BytesIO and StringIO).
540:     """
541: 
542:     def __init__(self, *fileobjs):
543:         if not all([callable(getattr(f, 'read', None)) and
544:                     callable(getattr(f, 'seek', None)) for f in fileobjs]):
545:             raise TypeError('MultiFileReader expected file-like objects'
546:                             ' with .read() and .seek()')
547:         if all([is_text_fileobj(f) for f in fileobjs]):
548:             # codecs.open and io.TextIOBase
549:             self._joiner = ''
550:         elif any([is_text_fileobj(f) for f in fileobjs]):
551:             raise ValueError('All arguments to MultiFileReader must handle'
552:                              ' bytes OR text, not a mix')
553:         else:
554:             # open/file and io.BytesIO
555:             self._joiner = b''
556:         self._fileobjs = fileobjs
557:         self._index = 0
558: 
559:     def read(self, amt=None):
```

## 15. boltons `SpooledStringIO`

- Path: `boltons-25.0.0\boltons\ioutils.py`
- Score: 10
- Selection reason: +4 likely true positive; +2 read/getter-like mutation; +2 later/cache/branch/composition hint; +1 simple constructor; +1 source import path available
- Suspected observer/read operation: `read`
- Suspected latent state: `_tell`
- Suspected later read/behavior: repeat the same read-shaped operation and compare result/state
- Harness classification: `confirmed_state_divergence_only`
- Result A summary: {"after": {"_buffer": "<codecs.StreamRecoder object at 0xADDR>", "_dir": "None", "_max_size": "5000000", "_tell": "0"}, "before": {"_dir": "None", "_max_size": "5000000", "_tell": "0"}, "result": {"kind": "value", "value": "''"}}
- Result B summary: {"after": {"_buffer": "<codecs.StreamRecoder object at 0xADDR>", "_dir": "None", "_max_size": "5000000", "_tell": "0"}, "after_observation": {"_buffer": "<codecs.StreamRecoder object at 0xADDR>", "_dir": "None", "_max_size": "5000000", "_tell": "0"}, "before": {"_dir": "None", "_max_size": "50000...
- Failure reason: 

```python
362:     def tell(self):
363:         self._checkClosed()
364:         return self.buffer.tell()
365: 
366: 
367: class SpooledStringIO(SpooledIOBase):
368:     """
369:     SpooledStringIO is a spooled file-like-object that only accepts unicode
370:     values. On Python 2.x this means the 'unicode' type and on Python 3.x this
371:     means the 'str' type. Values are accepted as unicode and then coerced into
372:     utf-8 encoded bytes for storage. On retrieval, the values are returned as
373:     unicode.
374: 
375:     Example::
376: 
377:         >>> from boltons import ioutils
378:         >>> with ioutils.SpooledStringIO() as f:
379:         ...     f.write(u"\u2014 Hey, an emdash!")
380:         ...     _ = f.seek(0)
381:         ...     isinstance(f.read(), str)
382:         True
383: 
384:     """
385:     def __init__(self, *args, **kwargs):
386:         self._tell = 0
387:         super().__init__(*args, **kwargs)
388: 
389:     def read(self, n=-1):
390:         self._checkClosed()
391:         ret = self.buffer.reader.read(n, n)
392:         self._tell = self.tell() + len(ret)
393:         return ret
394: 
395:     def write(self, s):
396:         self._checkClosed()
397:         if not isinstance(s, str):
398:             raise TypeError("str expected, got {}".format(
399:                 type(s).__name__
400:             ))
401:         current_pos = self.tell()
```

## 16. cerberus `BareValidator`

- Path: `cerberus-1.3.8\cerberus\validator.py`
- Score: 10
- Selection reason: +4 likely true positive; +2 read/getter-like mutation; +2 later/cache/branch/composition hint; +1 simple constructor; +1 source import path available
- Suspected observer/read operation: `__normalize_mapping`
- Suspected latent state: `_is_normalized`
- Suspected later read/behavior: repeat the same read-shaped operation and compare result/state
- Harness classification: `structural_only_no_runtime_difference`
- Result A summary: {"after": {"_config": "{'allow_unknown': False, 'require_all': False}", "_errors": "[]", "_remaining_rules": "[]", "_schema": "None", "document": "None", "document_error_tree": "[],{}", "document_path": "()", "error_handler": "<cerberus.errors.BasicErrorHandler object at 0xADDR>", "recent_error":...
- Result B summary: {"after": {"_config": "{'allow_unknown': False, 'require_all': False}", "_errors": "[]", "_remaining_rules": "[]", "_schema": "None", "document": "None", "document_error_tree": "[],{}", "document_path": "()", "error_handler": "<cerberus.errors.BasicErrorHandler object at 0xADDR>", "recent_error":...
- Failure reason: 

```python
54:     """
55: 
56:     pass
57: 
58: 
59: class BareValidator(object):
60:     """
61:     Validator class. Normalizes and/or validates any mapping against a
62:     validation-schema which is provided as an argument at class instantiation
63:     or upon calling the :meth:`~cerberus.Validator.validate`,
64:     :meth:`~cerberus.Validator.validated` or
65:     :meth:`~cerberus.Validator.normalized` method. An instance itself is
66:     callable and executes a validation.
67: 
68:     All instantiation parameters are optional.
69: 
70:     There are the introspective properties :attr:`types`, :attr:`validators`,
71:     :attr:`coercers`, :attr:`default_setters`, :attr:`rules`,
72:     :attr:`normalization_rules` and :attr:`validation_rules`.
73: 
74:     The attributes reflecting the available rules are assembled considering
75:     constraints that are defined in the docstrings of rules' methods and is
76:     effectively used as validation schema for :attr:`schema`.
77: 
78:     :param schema: See :attr:`~cerberus.Validator.schema`.
79:                    Defaults to :obj:`None`.
80:     :type schema: any :term:`mapping`
81:     :param ignore_none_values: See :attr:`~cerberus.Validator.ignore_none_values`.
82:                                Defaults to ``False``.
83:     :type ignore_none_values: :class:`bool`
84:     :param allow_unknown: See :attr:`~cerberus.Validator.allow_unknown`.
85:                           Defaults to ``False``.
86:     :type allow_unknown: :class:`bool` or any :term:`mapping`
87:     :param require_all: See :attr:`~cerberus.Validator.require_all`.
88:                         Defaults to ``False``.
89:     :type require_all: :class:`bool`
90:     :param purge_unknown: See :attr:`~cerberus.Validator.purge_unknown`.
91:                           Defaults to to ``False``.
92:     :type purge_unknown: :class:`bool`
93:     :param purge_readonly: Removes all fields that are defined as ``readonly`` in the
```

## 17. click-option-group `_OptGroup`

- Path: `click_option_group-0.5.9\src\click_option_group\_decorators.py`
- Score: 10
- Selection reason: +4 likely true positive; +2 read/getter-like mutation; +2 later/cache/branch/composition hint; +1 simple constructor; +1 source import path available
- Suspected observer/read operation: `__call__`
- Suspected latent state: `_outer_frame_index`
- Suspected later read/behavior: repeat the same read-shaped operation and compare result/state
- Harness classification: `structural_only_no_runtime_difference`
- Result A summary: {"after": {"_decorating_state": "defaultdict(<class 'list'>, {})", "_not_attached_options": "defaultdict(<class 'list'>, {})", "_outer_frame_index": "1"}, "before": {"_decorating_state": "defaultdict(<class 'list'>, {})", "_not_attached_options": "defaultdict(<class 'list'>, {})", "_outer_frame_i...
- Result B summary: {"after": {"_decorating_state": "defaultdict(<class 'list'>, {})", "_not_attached_options": "defaultdict(<class 'list'>, {})", "_outer_frame_index": "1"}, "after_observation": {"_decorating_state": "defaultdict(<class 'list'>, {})", "_not_attached_options": "defaultdict(<class 'list'>, {})", "_ou...
- Failure reason: 

```python
39: 
40:         msg = f"Missing option group decorator in '{ctx.command.name}' command for the following grouped options:\n{options_error_hint}\n"
41:         raise TypeError(msg)
42: 
43: 
44: class _OptGroup:
45:     """A helper class to manage creating groups and group options via decorators
46: 
47:     The class provides two decorator-methods: `group`/`__call__` and `option`.
48:     These decorators should be used for adding grouped options. The class have
49:     single global instance `optgroup` that should be used in most cases.
50: 
51:     The example of usage::
52: 
53:         ...
54:         @optgroup('Group 1', help='option group 1')
55:         @optgroup.option('--foo')
56:         @optgroup.option('--bar')
57:         @optgroup.group('Group 2', help='option group 2')
58:         @optgroup.option('--spam')
59:         ...
60:     """
61: 
62:     def __init__(self) -> None:
63:         self._decorating_state: Dict[Callable, List[OptionStackItem]] = collections.defaultdict(list)
64:         self._not_attached_options: Dict[Callable, List[click.Option]] = collections.defaultdict(list)
65:         self._outer_frame_index = 1
66: 
67:     def __call__(
68:         self,
69:         name: Optional[str] = None,
70:         *,
71:         help: Optional[str] = None,
72:         cls: Optional[Type[OptionGroup]] = None,
73:         **attrs,
74:     ):
75:         """Creates a new group and collects its options
76: 
77:         Creates the option group and registers all grouped options
78:         which were added by `option` decorator.
```

## 18. dnspython `BTree`

- Path: `dnspython-2.8.0\dns\btree.py`
- Score: 10
- Selection reason: +4 likely true positive; +2 read/getter-like mutation; +2 later/cache/branch/composition hint; +1 simple constructor; +1 source import path available
- Suspected observer/read operation: `insert_element`
- Suspected latent state: `root,size`
- Suspected later read/behavior: repeat the same read-shaped operation and compare result/state
- Harness classification: `structural_only_no_runtime_difference`
- Result A summary: {"after": {"_immutable": "False", "creator": "<dns.btree._Creator object at 0xADDR>", "cursors": "set()", "root": "<dns.btree._Node object at 0xADDR>", "size": "0", "t": "127"}, "before": {"_immutable": "False", "creator": "<dns.btree._Creator object at 0xADDR>", "cursors": "set()", "root": "<dns...
- Result B summary: {"after": {"_immutable": "False", "creator": "<dns.btree._Creator object at 0xADDR>", "cursors": "set()", "root": "<dns.btree._Node object at 0xADDR>", "size": "0", "t": "127"}, "after_observation": {"_immutable": "False", "creator": "<dns.btree._Creator object at 0xADDR>", "cursors": "set()", "r...
- Failure reason: 

```python
608: 
609: class Immutable(Exception):
610:     """The BTree is immutable."""
611: 
612: 
613: class BTree(Generic[KT, ET]):
614:     """An in-memory BTree with copy-on-write and cursors."""
615: 
616:     def __init__(self, *, t: int = DEFAULT_T, original: Optional["BTree"] = None):
617:         """Create a BTree.
618: 
619:         If *original* is not ``None``, then the BTree is shallow-cloned from
620:         *original* using copy-on-write.  Otherwise a new BTree with the specified
621:         *t* value is created.
622: 
623:         The BTree is not thread-safe.
624:         """
625:         # We don't use a reference to ourselves as a creator as we don't want
626:         # to prevent GC of old btrees.
627:         self.creator = _Creator()
628:         self._immutable = False
629:         self.t: int
630:         self.root: _Node
631:         self.size: int
632:         self.cursors: set[Cursor] = set()
633:         if original is not None:
634:             if not original._immutable:
635:                 raise ValueError("original BTree is not immutable")
636:             self.t = original.t
637:             self.root = original.root
638:             self.size = original.size
639:         else:
640:             if t < 3:
641:                 raise ValueError("t must be >= 3")
642:             self.t = t
643:             self.root = _Node(self.t, self.creator, True)
644:             self.size = 0
645: 
646:     def make_immutable(self):
647:         """Make the BTree immutable.
```

## 19. dnspython `EntropyPool`

- Path: `dnspython-2.8.0\dns\entropy.py`
- Score: 10
- Selection reason: +4 likely true positive; +2 read/getter-like mutation; +2 later/cache/branch/composition hint; +1 simple constructor; +1 source import path available
- Suspected observer/read operation: `random_8`
- Suspected latent state: `digest,next_byte`
- Suspected later read/behavior: repeat the same read-shaped operation and compare result/state
- Harness classification: `not_applicable_after_inspection`
- Result A summary: {}
- Result B summary: {}
- Failure reason: method name treated as nondeterministic: random_8

```python
21: import threading
22: import time
23: from typing import Any
24: 
25: 
26: class EntropyPool:
27:     # This is an entropy pool for Python implementations that do not
28:     # have a working SystemRandom.  I'm not sure there are any, but
29:     # leaving this code doesn't hurt anything as the library code
30:     # is used if present.
31: 
32:     def __init__(self, seed: bytes | None = None):
33:         self.pool_index = 0
34:         self.digest: bytearray | None = None
35:         self.next_byte = 0
36:         self.lock = threading.Lock()
37:         self.hash = hashlib.sha1()
38:         self.hash_len = 20
39:         self.pool = bytearray(b"\0" * self.hash_len)
40:         if seed is not None:
41:             self._stir(seed)
42:             self.seeded = True
43:             self.seed_pid = os.getpid()
44:         else:
45:             self.seeded = False
46:             self.seed_pid = 0
47: 
48:     def _stir(self, entropy: bytes | bytearray) -> None:
49:         for c in entropy:
50:             if self.pool_index == self.hash_len:
51:                 self.pool_index = 0
52:             b = c & 0xFF
53:             self.pool[self.pool_index] ^= b
54:             self.pool_index += 1
55: 
56:     def stir(self, entropy: bytes | bytearray) -> None:
57:         with self.lock:
58:             self._stir(entropy)
59: 
60:     def _maybe_seed(self) -> None:
```

## 20. dnspython `Message`

- Path: `dnspython-2.8.0\dns\message.py`
- Score: 10
- Selection reason: +4 likely true positive; +2 read/getter-like mutation; +2 later/cache/branch/composition hint; +1 simple constructor; +1 source import path available
- Suspected observer/read operation: `to_wire`
- Suspected latent state: `tsig_ctx,wire`
- Suspected later read/behavior: repeat the same read-shaped operation and compare result/state
- Harness classification: `not_applicable_after_inspection`
- Result A summary: {}
- Result B summary: {}
- Failure reason: fresh instances were not comparable under canonical state snapshot

```python
138: ]
139: IndexType = Dict[IndexKeyType, dns.rrset.RRset]
140: SectionType = int | str | List[dns.rrset.RRset]
141: 
142: 
143: class Message:
144:     """A DNS message."""
145: 
146:     _section_enum = MessageSection
147: 
148:     def __init__(self, id: int | None = None):
149:         if id is None:
150:             self.id = dns.entropy.random_16()
151:         else:
152:             self.id = id
153:         self.flags = 0
154:         self.sections: List[List[dns.rrset.RRset]] = [[], [], [], []]
155:         self.opt: dns.rrset.RRset | None = None
156:         self.request_payload = 0
157:         self.pad = 0
158:         self.keyring: Any = None
159:         self.tsig: dns.rrset.RRset | None = None
160:         self.want_tsig_sign = False
161:         self.request_mac = b""
162:         self.xfr = False
163:         self.origin: dns.name.Name | None = None
164:         self.tsig_ctx: Any | None = None
165:         self.index: IndexType = {}
166:         self.errors: List[MessageError] = []
167:         self.time = 0.0
168:         self.wire: bytes | None = None
169: 
170:     @property
171:     def question(self) -> List[dns.rrset.RRset]:
172:         """The question section."""
173:         return self.sections[0]
174: 
175:     @question.setter
176:     def question(self, v):
177:         self.sections[0] = v
```

## 21. dnspython `Buffer`

- Path: `dnspython-2.8.0\dns\quic\_common.py`
- Score: 10
- Selection reason: +4 likely true positive; +2 read/getter-like mutation; +2 later/cache/branch/composition hint; +1 simple constructor; +1 source import path available
- Suspected observer/read operation: `get`
- Suspected latent state: `_buffer`
- Suspected later read/behavior: repeat the same read-shaped operation and compare result/state
- Harness classification: `import_failed`
- Result A summary: {}
- Result B summary: {}
- Failure reason: import_failed: ModuleNotFoundError: No module named 'aioquic'

```python
25: 
26: class UnexpectedEOF(Exception):
27:     pass
28: 
29: 
30: class Buffer:
31:     def __init__(self):
32:         self._buffer = b""
33:         self._seen_end = False
34: 
35:     def put(self, data, is_end):
36:         if self._seen_end:
37:             return
38:         self._buffer += data
39:         if is_end:
40:             self._seen_end = True
41: 
42:     def have(self, amount):
43:         if len(self._buffer) >= amount:
44:             return True
45:         if self._seen_end:
46:             raise UnexpectedEOF
47:         return False
48: 
49:     def seen_end(self):
50:         return self._seen_end
51: 
52:     def get(self, amount):
53:         assert self.have(amount)
54:         data = self._buffer[:amount]
55:         self._buffer = self._buffer[amount:]
56:         return data
57: 
58:     def get_all(self):
59:         assert self.seen_end()
60:         data = self._buffer
61:         self._buffer = b""
62:         return data
63: 
64: 
```

## 22. dnspython `Tokenizer`

- Path: `dnspython-2.8.0\dns\tokenizer.py`
- Score: 10
- Selection reason: +4 likely true positive; +2 read/getter-like mutation; +2 later/cache/branch/composition hint; +1 simple constructor; +1 source import path available
- Suspected observer/read operation: `_get_char`
- Suspected latent state: `eof,line_number,ungotten_char`
- Suspected later read/behavior: repeat the same read-shaped operation and compare result/state
- Harness classification: `confirmed_state_divergence_only`
- Result A summary: {"after": {"delimiters": "{'\"', '\\n', ')', ';', '\\t', '(', ' '}", "eof": "True", "file": "<_io.TextIOWrapper name='<stdin>' mode='r' encoding='cp1252'>", "filename": "'<stdin>'", "idna_codec": "<dns.name.IDNA2003Codec object at 0xADDR>", "line_number": "1", "multiline": "0", "quoting": "False"...
- Result B summary: {"after": {"delimiters": "{'\"', '\\n', ')', ';', '\\t', '(', ' '}", "eof": "True", "file": "<_io.TextIOWrapper name='<stdin>' mode='r' encoding='cp1252'>", "filename": "'<stdin>'", "idna_codec": "<dns.name.IDNA2003Codec object at 0xADDR>", "line_number": "1", "multiline": "0", "quoting": "False"...
- Failure reason: 

```python
193:             else:
194:                 unescaped += c.encode()
195:         return Token(self.ttype, bytes(unescaped))
196: 
197: 
198: class Tokenizer:
199:     """A DNS zone file format tokenizer.
200: 
201:     A token object is basically a (type, value) tuple.  The valid
202:     types are EOF, EOL, WHITESPACE, IDENTIFIER, QUOTED_STRING,
203:     COMMENT, and DELIMITER.
204: 
205:     file: The file to tokenize
206: 
207:     ungotten_char: The most recently ungotten character, or None.
208: 
209:     ungotten_token: The most recently ungotten token, or None.
210: 
211:     multiline: The current multiline level.  This value is increased
212:     by one every time a '(' delimiter is read, and decreased by one every time
213:     a ')' delimiter is read.
214: 
215:     quoting: This variable is true if the tokenizer is currently
216:     reading a quoted string.
217: 
218:     eof: This variable is true if the tokenizer has encountered EOF.
219: 
220:     delimiters: The current delimiter dictionary.
221: 
222:     line_number: The current line number
223: 
224:     filename: A filename that will be returned by the where() method.
225: 
226:     idna_codec: A dns.name.IDNACodec, specifies the IDNA
227:     encoder/decoder.  If None, the default IDNA 2003
228:     encoder/decoder is used.
229:     """
230: 
231:     def __init__(
232:         self,
```

## 23. docutils `Publisher`

- Path: `docutils-0.22.4\docutils\core.py`
- Score: 10
- Selection reason: +4 likely true positive; +2 read/getter-like mutation; +2 later/cache/branch/composition hint; +1 simple constructor; +1 source import path available
- Suspected observer/read operation: `get_settings`
- Suspected latent state: `settings`
- Suspected later read/behavior: repeat the same read-shaped operation and compare result/state
- Harness classification: `confirmed_state_divergence_only`
- Result A summary: {"after": {"_stderr": "<docutils.io.ErrorOutput object at 0xADDR>", "destination": "None", "destination_class": "<class 'docutils.io.FileOutput'>", "document": "None", "parser": "None", "reader": "None", "settings": "<Values at 0xADDR: {'output_path': None, 'title': None, 'generator': None, 'date...
- Result B summary: {"after": {"_stderr": "<docutils.io.ErrorOutput object at 0xADDR>", "destination": "None", "destination_class": "<class 'docutils.io.FileOutput'>", "document": "None", "parser": "None", "reader": "None", "settings": "<Values at 0xADDR: {'output_path': None, 'title': None, 'generator': None, 'date...
- Failure reason: 

```python
32: if TYPE_CHECKING:
33:     from typing import TextIO
34:     from docutils.nodes import StrPath
35: 
36: 
37: class Publisher:
38: 
39:     """
40:     A facade encapsulating the high-level logic of a Docutils system.
41:     """
42: 
43:     def __init__(self, reader=None, parser=None, writer=None,
44:                  source=None, source_class=io.FileInput,
45:                  destination=None, destination_class=io.FileOutput,
46:                  settings=None) -> None:
47:         """
48:         Initial setup.
49: 
50:         The components `reader`, `parser`, or `writer` should all be
51:         specified, either as instances or via their names.
52:         """
53:         # get component instances from their names:
54:         if isinstance(reader, str):
55:             reader = readers.get_reader_class(reader)(parser)
56:         if isinstance(parser, str):
57:             if isinstance(reader, readers.Reader):
58:                 if reader.parser is None:
59:                     reader.set_parser(parser)
60:                 parser = reader.parser
61:             else:
62:                 parser = parsers.get_parser_class(parser)()
63:         if isinstance(writer, str):
64:             writer = writers.get_writer_class(writer)()
65: 
66:         self.document = None
67:         """The document tree (`docutils.nodes` objects)."""
68: 
69:         self.reader = reader
70:         """A `docutils.readers.Reader` instance."""
71: 
```

## 24. docutils `OptionParser`

- Path: `docutils-0.22.4\docutils\frontend.py`
- Score: 10
- Selection reason: +4 likely true positive; +2 read/getter-like mutation; +2 later/cache/branch/composition hint; +1 simple constructor; +1 source import path available
- Suspected observer/read operation: `get_config_file_settings`
- Suspected latent state: `config_files`
- Suspected later read/behavior: repeat the same read-shaped operation and compare result/state
- Harness classification: `structural_only_no_runtime_difference`
- Result A summary: {"after": {"_long_opt": "{'--output-path': <Option at 0xADDR: --output-path/--output>, '--output': <Option at 0xADDR: --output-path/--output>, '--title': <Option at 0xADDR: --title>,...", "_short_opt": "{'-g': <Option at 0xADDR: -g/--generator>, '-d': <Option at 0xADDR: -d/--date>, '-t': <Option ...
- Result B summary: {"after": {"_long_opt": "{'--output-path': <Option at 0xADDR: --output-path/--output>, '--output': <Option at 0xADDR: --output-path/--output>, '--title': <Option at 0xADDR: --title>,...", "_short_opt": "{'-g': <Option at 0xADDR: -g/--generator>, '-d': <Option at 0xADDR: -d/--date>, '-t': <Option ...
- Failure reason: 

```python
641:             if self.overrides:
642:                 setattr(values, self.overrides, None)
643:         return result
644: 
645: 
646: class OptionParser(optparse.OptionParser, docutils.SettingsSpec):
647:     """
648:     Settings parser for command-line and library use.
649: 
650:     The `settings_spec` specification here and in other Docutils components
651:     are merged to build the set of command-line options and runtime settings
652:     for this process.
653: 
654:     Common settings (defined below) and component-specific settings must not
655:     conflict.  Short options are reserved for common settings, and components
656:     are restricted to using long options.
657: 
658:     Deprecated.
659:     Will be replaced by a subclass of `argparse.ArgumentParser`.
660:     """
661: 
662:     standard_config_files: ClassVar[list[str]] = [
663:         '/etc/docutils.conf',           # system-wide
664:         './docutils.conf',              # project-specific
665:         '~/.docutils']                  # user-specific
666:     """Docutils configuration files, using ConfigParser syntax.
667: 
668:     Filenames will be tilde-expanded later. Later files override earlier ones.
669:     """
670: 
671:     threshold_choices: ClassVar[tuple[str]] = (
672:         'info', '1', 'warning', '2', 'error', '3', 'severe', '4', 'none', '5')
673:     """Possible inputs for for --report and --halt threshold values."""
674: 
675:     thresholds: ClassVar[dict[str, int]] = {
676:         'info': 1, 'warning': 2, 'error': 3, 'severe': 4, 'none': 5}
677:     """Lookup table for --report and --halt threshold values."""
678: 
679:     booleans: ClassVar[dict[str, bool]] = {
680:         '1': True, 'on': True, 'yes': True, 'true': True,
```

## 25. docutils `Input`

- Path: `docutils-0.22.4\docutils\io.py`
- Score: 10
- Selection reason: +4 likely true positive; +2 read/getter-like mutation; +2 later/cache/branch/composition hint; +1 simple constructor; +1 source import path available
- Suspected observer/read operation: `decode`
- Suspected latent state: `successful_encoding`
- Suspected later read/behavior: repeat the same read-shaped operation and compare result/state
- Harness classification: `structural_only_no_runtime_difference`
- Result A summary: {"after": {"encoding": "'utf-8'", "error_handler": "'strict'", "source": "None", "source_path": "None", "successful_encoding": "None"}, "before": {"encoding": "'utf-8'", "error_handler": "'strict'", "source": "None", "source_path": "None", "successful_encoding": "None"}, "result": {"kind": "not_c...
- Result B summary: {"after": {"encoding": "'utf-8'", "error_handler": "'strict'", "source": "None", "source_path": "None", "successful_encoding": "None"}, "after_observation": {"encoding": "'utf-8'", "error_handler": "'strict'", "source": "None", "source_path": "None", "successful_encoding": "None"}, "before": {"en...
- Failure reason: 

```python
73:     """Return string representation of Exception `err`.
74:     """
75:     return f'{err.__class__.__name__}: {err}'
76: 
77: 
78: class Input(TransformSpec):
79:     """
80:     Abstract base class for input wrappers.
81: 
82:     Docutils input objects must provide a `read()` method that
83:     returns the source, typically as `str` instance.
84: 
85:     Inheriting `TransformSpec` allows input objects to add "transforms" to
86:     the "Transformer".  (Since Docutils 0.19, input objects are no longer
87:     required to be `TransformSpec` instances.)
88:     """
89: 
90:     component_type: Final = 'input'
91: 
92:     default_source_path: ClassVar[str | None] = None
93: 
94:     def __init__(
95:         self,
96:         source: str | TextIO | nodes.document | None = None,
97:         source_path: StrPath | None = None,
98:         encoding: str | Literal['unicode'] | None = 'utf-8',
99:         error_handler: str | None = 'strict',
100:     ) -> None:
101:         self.encoding = encoding
102:         """Text encoding for the input source."""
103: 
104:         self.error_handler = error_handler
105:         """Text decoding error handler."""
106: 
107:         self.source = source
108:         """The source of input data."""
109: 
110:         self.source_path = source_path
111:         """A text reference to the source."""
112: 
```

## 26. docutils `StringOutput`

- Path: `docutils-0.22.4\docutils\io.py`
- Score: 10
- Selection reason: +4 likely true positive; +2 read/getter-like mutation; +2 later/cache/branch/composition hint; +1 simple constructor; +1 source import path available
- Suspected observer/read operation: `write`
- Suspected latent state: `destination`
- Suspected later read/behavior: repeat the same read-shaped operation and compare result/state
- Harness classification: `unsafe_to_execute`
- Result A summary: {}
- Result B summary: {}
- Failure reason: method name treated as unsafe: write

```python
643:         Decode, if required (see `Input.decode`).
644:         """
645:         return self.decode(self.source)
646: 
647: 
648: class StringOutput(Output):
649:     """Output to a `bytes` or `str` instance.
650: 
651:     Provisional.
652:     """
653: 
654:     destination: str | bytes
655: 
656:     default_destination_path: Final = '<string>'
657: 
658:     def write(self, data: str | bytes) -> str | bytes:
659:         """Store `data` in `self.destination`, and return it.
660: 
661:         If `self.encoding` is set to the pseudo encoding name "unicode",
662:         `data` must be a `str` instance and is stored/returned unchanged
663:         (cf. `Output.encode`).
664: 
665:         Otherwise, `data` can be a `bytes` or `str` instance and is
666:         stored/returned as a `bytes` instance
667:         (`str` data is encoded with `self.encode()`).
668: 
669:         Attention: the `output_encoding`_ setting may affect the content
670:         of the output (e.g. an encoding declaration in HTML or XML or the
671:         representation of characters as LaTeX macro vs. literal character).
672:         """
673:         self.destination = self.encode(data)
674:         return self.destination
675: 
676: 
677: class NullInput(Input):
678: 
679:     """Degenerate input: read nothing."""
680: 
681:     source: None
682: 
```

## 27. docutils `LineBlock`

- Path: `docutils-0.22.4\docutils\parsers\rst\directives\body.py`
- Score: 10
- Selection reason: +4 likely true positive; +2 read/getter-like mutation; +2 later/cache/branch/composition hint; +1 simple constructor; +1 source import path available
- Suspected observer/read operation: `run`
- Suspected latent state: `content_offset`
- Suspected later read/behavior: repeat the same read-shaped operation and compare result/state
- Harness classification: `could_not_construct`
- Result A summary: {}
- Result B summary: {}
- Failure reason: constructor requires arguments: name, arguments, options, content, lineno, content_offset, block_text, state, state_machine

```python
94:                              'without a title.')
95: 
96:         return BasePseudoSection.run(self)
97: 
98: 
99: class LineBlock(Directive):
100:     """Legacy directive for line blocks.
101: 
102:     Use is deprecated in favour of the line block syntax,
103:     cf. `parsers.rst.states.Body.line_block()`.
104:     """
105: 
106:     option_spec = {'class': directives.class_option,
107:                    'name': directives.unchanged}
108:     has_content = True
109: 
110:     def run(self):
111:         self.assert_has_content()
112:         block = nodes.line_block(classes=self.options.get('class', []))
113:         (block.source,
114:          block.line) = self.state_machine.get_source_and_line(self.lineno)
115:         self.add_name(block)
116:         node_list = [block]
117:         for i, line_text in enumerate(self.content):
118:             text_nodes, messages = self.state.inline_text(
119:                 line_text.strip(), self.lineno + self.content_offset)
120:             line = nodes.line(line_text, '', *text_nodes)
121:             line.source = block.source
122:             line.line = block.line + i
123:             if line_text.strip():
124:                 line.indent = len(line_text) - len(line_text.lstrip())
125:             block += line
126:             node_list.extend(messages)
127:             self.content_offset += 1
128:         self.state.nest_line_block_lines(block)
129:         return node_list
130: 
131: 
132: class ParsedLiteral(Directive):
133: 
```

## 28. docutils `Include`

- Path: `docutils-0.22.4\docutils\parsers\rst\directives\misc.py`
- Score: 10
- Selection reason: +4 likely true positive; +2 read/getter-like mutation; +2 later/cache/branch/composition hint; +1 simple constructor; +1 source import path available
- Suspected observer/read operation: `run`
- Suspected latent state: `clip_options,settings,tab_width`
- Suspected later read/behavior: repeat the same read-shaped operation and compare result/state
- Harness classification: `could_not_construct`
- Result A summary: {}
- Result B summary: {}
- Failure reason: constructor requires arguments: name, arguments, options, content, lineno, content_offset, block_text, state, state_machine

```python
37:         base = Path(source).parent
38:     # pepend "base" and convert to relative path for shorter system messages
39:     return utils.relative_path(None, base/path)
40: 
41: 
42: class Include(Directive):
43: 
44:     """
45:     Include content read from a separate source file.
46: 
47:     Content may be parsed by the parser, or included as a literal
48:     block.  The encoding of the included file can be specified.  Only
49:     a part of the given file argument may be included by specifying
50:     start and end line or text to match before and/or after the text
51:     to be used.
52: 
53:     https://docutils.sourceforge.io/docs/ref/rst/directives.html#include
54:     """
55: 
56:     required_arguments = 1
57:     optional_arguments = 0
58:     final_argument_whitespace = True
59:     option_spec = {'literal': directives.flag,
60:                    'code': directives.unchanged,
61:                    'encoding': directives.encoding,
62:                    'parser': directives.parser_name,
63:                    'tab-width': int,
64:                    'start-line': int,
65:                    'end-line': int,
66:                    'start-after': directives.unchanged_required,
67:                    'end-before': directives.unchanged_required,
68:                    # ignored except for 'literal' or 'code':
69:                    'number-lines': directives.value_or((None,), int),
70:                    'class': directives.class_option,
71:                    'name': directives.unchanged}
72: 
73:     standard_include_path = Path(states.__file__).parent / 'include'
74: 
75:     def run(self) -> list:
76:         """Include a file as part of the content of this reST file.
```

## 29. docutils `MetaBody`

- Path: `docutils-0.22.4\docutils\parsers\rst\directives\misc.py`
- Score: 10
- Selection reason: +4 likely true positive; +2 read/getter-like mutation; +2 later/cache/branch/composition hint; +1 simple constructor; +1 source import path available
- Suspected observer/read operation: `field_marker`
- Suspected latent state: `parent`
- Suspected later read/behavior: repeat the same read-shaped operation and compare result/state
- Harness classification: `could_not_construct`
- Result A summary: {}
- Result B summary: {}
- Failure reason: constructor requires arguments: state_machine

```python
566:     def run(self):
567:         self.state_machine.document['title'] = self.arguments[0]
568:         return []
569: 
570: 
571: class MetaBody(states.SpecializedBody):
572: 
573:     def field_marker(self, match, context, next_state):
574:         """Meta element."""
575:         node, blank_finish = self.parsemeta(match)
576:         self.parent += node
577:         return [], next_state, []
578: 
579:     def parsemeta(self, match):
580:         name = self.parse_field_marker(match)
581:         name = nodes.unescape(utils.escape2null(name))
582:         (indented, indent, line_offset, blank_finish
583:          ) = self.state_machine.get_first_known_indented(match.end())
584:         node = nodes.meta()
585:         node['content'] = nodes.unescape(utils.escape2null(
586:                                             ' '.join(indented)))
587:         if not indented:
588:             line = self.state_machine.line
589:             msg = self.reporter.info(
590:                   'No content for meta tag "%s".' % name,
591:                   nodes.literal_block(line, line))
592:             return msg, blank_finish
593:         tokens = name.split()
594:         try:
595:             attname, val = utils.extract_name_value(tokens[0])[0]
596:             node[attname.lower()] = val
597:         except utils.NameValueError:
598:             node['name'] = tokens[0]
599:         for token in tokens[1:]:
600:             try:
601:                 attname, val = utils.extract_name_value(token)[0]
602:                 node[attname.lower()] = val
603:             except utils.NameValueError as detail:
604:                 line = self.state_machine.line
605:                 msg = self.reporter.error(
```

## 30. docutils `Body`

- Path: `docutils-0.22.4\docutils\parsers\rst\states.py`
- Score: 10
- Selection reason: +4 likely true positive; +2 read/getter-like mutation; +2 later/cache/branch/composition hint; +1 simple constructor; +1 source import path available
- Suspected observer/read operation: `indent`
- Suspected latent state: `parent`
- Suspected later read/behavior: repeat the same read-shaped operation and compare result/state
- Harness classification: `could_not_construct`
- Result A summary: {}
- Result B summary: {}
- Failure reason: constructor requires arguments: state_machine

```python
1176: 
1177: def _upperalpha_to_int(s, _zero=(ord('A')-1)):
1178:     return ord(s) - _zero
1179: 
1180: 
1181: class Body(RSTState):
1182: 
1183:     """
1184:     Generic classifier of the first line of a block.
1185:     """
1186: 
1187:     double_width_pad_char = tableparser.TableParser.double_width_pad_char
1188:     """Padding character for East Asian double-width text."""
1189: 
1190:     enum = Struct()
1191:     """Enumerated list parsing information."""
1192: 
1193:     enum.formatinfo = {
1194:           'parens': Struct(prefix='(', suffix=')', start=1, end=-1),
1195:           'rparen': Struct(prefix='', suffix=')', start=0, end=-1),
1196:           'period': Struct(prefix='', suffix='.', start=0, end=-1)}
1197:     enum.formats = enum.formatinfo.keys()
1198:     enum.sequences = ['arabic', 'loweralpha', 'upperalpha',
1199:                       'lowerroman', 'upperroman']  # ORDERED!
1200:     enum.sequencepats = {'arabic': '[0-9]+',
1201:                          'loweralpha': '[a-z]',
1202:                          'upperalpha': '[A-Z]',
1203:                          'lowerroman': '[ivxlcdm]+',
1204:                          'upperroman': '[IVXLCDM]+'}
1205:     enum.converters = {'arabic': int,
1206:                        'loweralpha': _loweralpha_to_int,
1207:                        'upperalpha': _upperalpha_to_int,
1208:                        'lowerroman': RomanNumeral.from_string,
1209:                        'upperroman': RomanNumeral.from_string}
1210: 
1211:     enum.sequenceregexps = {}
1212:     for sequence in enum.sequences:
1213:         enum.sequenceregexps[sequence] = re.compile(
1214:               enum.sequencepats[sequence] + '$')
1215: 
```

## 31. docutils `BulletList`

- Path: `docutils-0.22.4\docutils\parsers\rst\states.py`
- Score: 10
- Selection reason: +4 likely true positive; +2 read/getter-like mutation; +2 later/cache/branch/composition hint; +1 simple constructor; +1 source import path available
- Suspected observer/read operation: `bullet`
- Suspected latent state: `blank_finish,parent`
- Suspected later read/behavior: repeat the same read-shaped operation and compare result/state
- Harness classification: `could_not_construct`
- Result A summary: {}
- Result B summary: {}
- Failure reason: constructor requires arguments: state_machine

```python
2652:     anonymous = invalid_input
2653:     line = invalid_input
2654:     text = invalid_input
2655: 
2656: 
2657: class BulletList(SpecializedBody):
2658: 
2659:     """Second and subsequent bullet_list list_items."""
2660: 
2661:     def bullet(self, match, context, next_state):
2662:         """Bullet list item."""
2663:         if match.string[0] != self.parent['bullet']:
2664:             # different bullet: new list
2665:             self.invalid_input()
2666:         listitem, blank_finish = self.list_item(match.end())
2667:         self.parent += listitem
2668:         self.blank_finish = blank_finish
2669:         return [], next_state, []
2670: 
2671: 
2672: class DefinitionList(SpecializedBody):
2673: 
2674:     """Second and subsequent definition_list_items."""
2675: 
2676:     def text(self, match, context, next_state):
2677:         """Definition lists."""
2678:         return [match.string], 'Definition', []
2679: 
2680: 
2681: class EnumeratedList(SpecializedBody):
2682: 
2683:     """Second and subsequent enumerated_list list_items."""
2684: 
2685:     def enumerator(self, match, context, next_state):
2686:         """Enumerated list item."""
2687:         format, sequence, text, ordinal = self.parse_enumerator(
2688:               match, self.parent['enumtype'])
2689:         if (format != self.format
2690:             or (sequence != '#' and (sequence != self.parent['enumtype']
2691:                                      or self.auto
```

## 32. docutils `Definition`

- Path: `docutils-0.22.4\docutils\parsers\rst\states.py`
- Score: 10
- Selection reason: +4 likely true positive; +2 read/getter-like mutation; +2 later/cache/branch/composition hint; +1 simple constructor; +1 source import path available
- Suspected observer/read operation: `indent`
- Suspected latent state: `blank_finish,parent`
- Suspected later read/behavior: repeat the same read-shaped operation and compare result/state
- Harness classification: `could_not_construct`
- Result A summary: {}
- Result B summary: {}
- Failure reason: constructor requires arguments: state_machine

```python
3043:     indent = invalid_input
3044:     underline = invalid_input
3045:     text = invalid_input
3046: 
3047: 
3048: class Definition(SpecializedText):
3049: 
3050:     """Second line of potential definition_list_item."""
3051: 
3052:     def eof(self, context):
3053:         """Not a definition."""
3054:         self.state_machine.previous_line(2)  # so parent SM can reassess
3055:         return []
3056: 
3057:     def indent(self, match, context, next_state):
3058:         """Definition list item."""
3059:         dl_item, blank_finish = self.definition_list_item(context)
3060:         self.parent += dl_item
3061:         self.blank_finish = blank_finish
3062:         return [], 'DefinitionList', []
3063: 
3064: 
3065: class Line(SpecializedText):
3066: 
3067:     """
3068:     Second line of over- & underlined section title or transition marker.
3069:     """
3070: 
3071:     eofcheck = 1  # ignored, will be removed in Docutils 2.0.
3072: 
3073:     def eof(self, context):
3074:         """Transition marker at end of section or document."""
3075:         marker = context[0].strip()
3076:         if len(marker) < 4:
3077:             self.state_correction(context)
3078:         src, srcline = self.state_machine.get_source_and_line()
3079:         # lineno = self.state_machine.abs_line_number() - 1
3080:         transition = nodes.transition(rawsource=context[0])
3081:         transition.source = src
3082:         transition.line = srcline - 1
```

## 33. docutils `EnumeratedList`

- Path: `docutils-0.22.4\docutils\parsers\rst\states.py`
- Score: 10
- Selection reason: +4 likely true positive; +2 read/getter-like mutation; +2 later/cache/branch/composition hint; +1 simple constructor; +1 source import path available
- Suspected observer/read operation: `enumerator`
- Suspected latent state: `auto,blank_finish,lastordinal,parent`
- Suspected later read/behavior: repeat the same read-shaped operation and compare result/state
- Harness classification: `could_not_construct`
- Result A summary: {}
- Result B summary: {}
- Failure reason: constructor requires arguments: state_machine

```python
2676:     def text(self, match, context, next_state):
2677:         """Definition lists."""
2678:         return [match.string], 'Definition', []
2679: 
2680: 
2681: class EnumeratedList(SpecializedBody):
2682: 
2683:     """Second and subsequent enumerated_list list_items."""
2684: 
2685:     def enumerator(self, match, context, next_state):
2686:         """Enumerated list item."""
2687:         format, sequence, text, ordinal = self.parse_enumerator(
2688:               match, self.parent['enumtype'])
2689:         if (format != self.format
2690:             or (sequence != '#' and (sequence != self.parent['enumtype']
2691:                                      or self.auto
2692:                                      or ordinal != (self.lastordinal + 1)))
2693:             or not self.is_enumerated_list_item(ordinal, sequence, format)):
2694:             # different enumeration: new list
2695:             self.invalid_input()
2696:         if sequence == '#':
2697:             self.auto = 1
2698:         listitem, blank_finish = self.list_item(match.end())
2699:         self.parent += listitem
2700:         self.blank_finish = blank_finish
2701:         self.lastordinal = ordinal
2702:         return [], next_state, []
2703: 
2704: 
2705: class FieldList(SpecializedBody):
2706: 
2707:     """Second and subsequent field_list fields."""
2708: 
2709:     def field_marker(self, match, context, next_state):
2710:         """Field list field."""
2711:         field, blank_finish = self.field(match)
2712:         self.parent += field
2713:         self.blank_finish = blank_finish
2714:         return [], next_state, []
2715: 
```

## 34. docutils `Explicit`

- Path: `docutils-0.22.4\docutils\parsers\rst\states.py`
- Score: 10
- Selection reason: +4 likely true positive; +2 read/getter-like mutation; +2 later/cache/branch/composition hint; +1 simple constructor; +1 source import path available
- Suspected observer/read operation: `explicit_markup`
- Suspected latent state: `blank_finish,parent`
- Suspected later read/behavior: repeat the same read-shaped operation and compare result/state
- Harness classification: `could_not_construct`
- Result A summary: {}
- Result B summary: {}
- Failure reason: constructor requires arguments: state_machine

```python
2780:         self.parent.parent += messages
2781:         self.blank_finish = blank_finish
2782:         return [], next_state, []
2783: 
2784: 
2785: class Explicit(SpecializedBody):
2786: 
2787:     """Second and subsequent explicit markup construct."""
2788: 
2789:     def explicit_markup(self, match, context, next_state):
2790:         """Footnotes, hyperlink targets, directives, comments."""
2791:         nodelist, blank_finish = self.explicit_construct(match)
2792:         self.parent += nodelist
2793:         self.blank_finish = blank_finish
2794:         return [], next_state, []
2795: 
2796:     def anonymous(self, match, context, next_state):
2797:         """Anonymous hyperlink targets."""
2798:         nodelist, blank_finish = self.anonymous_target(match)
2799:         self.parent += nodelist
2800:         self.blank_finish = blank_finish
2801:         return [], next_state, []
2802: 
2803:     blank = SpecializedBody.invalid_input
2804: 
2805: 
2806: class SubstitutionDef(Body):
2807: 
2808:     """
2809:     Parser for the contents of a substitution_definition element.
2810:     """
2811: 
2812:     patterns = {
2813:           'embedded_directive': re.compile(r'(%s)::( +|$)'
2814:                                            % Inliner.simplename),
2815:           'text': r''}
2816:     initial_transitions = ['embedded_directive', 'text']
2817: 
2818:     def embedded_directive(self, match, context, next_state):
2819:         nodelist, blank_finish = self.directive(match,
```

## 35. docutils `FieldList`

- Path: `docutils-0.22.4\docutils\parsers\rst\states.py`
- Score: 10
- Selection reason: +4 likely true positive; +2 read/getter-like mutation; +2 later/cache/branch/composition hint; +1 simple constructor; +1 source import path available
- Suspected observer/read operation: `field_marker`
- Suspected latent state: `blank_finish,parent`
- Suspected later read/behavior: repeat the same read-shaped operation and compare result/state
- Harness classification: `could_not_construct`
- Result A summary: {}
- Result B summary: {}
- Failure reason: constructor requires arguments: state_machine

```python
2700:         self.blank_finish = blank_finish
2701:         self.lastordinal = ordinal
2702:         return [], next_state, []
2703: 
2704: 
2705: class FieldList(SpecializedBody):
2706: 
2707:     """Second and subsequent field_list fields."""
2708: 
2709:     def field_marker(self, match, context, next_state):
2710:         """Field list field."""
2711:         field, blank_finish = self.field(match)
2712:         self.parent += field
2713:         self.blank_finish = blank_finish
2714:         return [], next_state, []
2715: 
2716: 
2717: class OptionList(SpecializedBody):
2718: 
2719:     """Second and subsequent option_list option_list_items."""
2720: 
2721:     def option_marker(self, match, context, next_state):
2722:         """Option list item."""
2723:         try:
2724:             option_list_item, blank_finish = self.option_list_item(match)
2725:         except MarkupError:
2726:             self.invalid_input()
2727:         self.parent += option_list_item
2728:         self.blank_finish = blank_finish
2729:         return [], next_state, []
2730: 
2731: 
2732: class RFC2822List(SpecializedBody, RFC2822Body):
2733: 
2734:     """Second and subsequent RFC2822-style field_list fields."""
2735: 
2736:     patterns = RFC2822Body.patterns
2737:     initial_transitions = RFC2822Body.initial_transitions
2738: 
2739:     def rfc2822(self, match, context, next_state):
```

## 36. docutils `Inliner`

- Path: `docutils-0.22.4\docutils\parsers\rst\states.py`
- Score: 10
- Selection reason: +4 likely true positive; +2 read/getter-like mutation; +2 later/cache/branch/composition hint; +1 simple constructor; +1 source import path available
- Suspected observer/read operation: `parse`
- Suspected latent state: `document,language,parent,reporter`
- Suspected later read/behavior: repeat the same read-shaped operation and compare result/state
- Harness classification: `structural_only_no_runtime_difference`
- Result A summary: {"after": {"implicit_dispatch": "[]"}, "before": {"implicit_dispatch": "[]"}, "result": {"kind": "not_callable_without_args", "required": ["text", "lineno", "memo", "parent"]}}
- Result B summary: {"after": {"implicit_dispatch": "[]"}, "after_observation": {"implicit_dispatch": "[]"}, "before": {"implicit_dispatch": "[]"}, "observation_result": {"kind": "not_callable_without_args", "required": ["text", "lineno", "memo", "parent"]}, "result": {"kind": "not_callable_without_args", "required"...
- Failure reason: 

```python
566:         return re.compile(regexp)
567:     else:
568:         return regexp
569: 
570: 
571: class Inliner:
572: 
573:     """
574:     Parse inline markup; call the `parse()` method.
575:     """
576: 
577:     def __init__(self) -> None:
578:         self.implicit_dispatch = []
579:         """List of (pattern, bound method) tuples, used by
580:         `self.implicit_inline`."""
581: 
582:     def init_customizations(self, settings) -> None:
583:         # lookahead and look-behind expressions for inline markup rules
584:         if getattr(settings, 'character_level_inline_markup', False):
585:             start_string_prefix = '(^|(?<!\x00))'
586:             end_string_suffix = ''
587:         else:
588:             start_string_prefix = ('(^|(?<=\\s|[%s%s]))' %
589:                                    (punctuation_chars.openers,
590:                                     punctuation_chars.delimiters))
591:             end_string_suffix = ('($|(?=\\s|[\x00%s%s%s]))' %
592:                                  (punctuation_chars.closing_delimiters,
593:                                   punctuation_chars.delimiters,
594:                                   punctuation_chars.closers))
595:         args = locals().copy()
596:         args.update(vars(self.__class__))
597: 
598:         parts = ('initial_inline', start_string_prefix, '',
599:            [
600:             ('start', '', self.non_whitespace_after,  # simple start-strings
601:              [r'\*\*',                # strong
602:               r'\*(?!\*)',            # emphasis but not strong
603:               r'``',                  # literal
604:               r'_`',                  # inline internal target
605:               r'\|(?!\|)']            # substitution reference
```

## 37. docutils `Line`

- Path: `docutils-0.22.4\docutils\parsers\rst\states.py`
- Score: 10
- Selection reason: +4 likely true positive; +2 read/getter-like mutation; +2 later/cache/branch/composition hint; +1 simple constructor; +1 source import path available
- Suspected observer/read operation: `eof`
- Suspected latent state: `parent`
- Suspected later read/behavior: repeat the same read-shaped operation and compare result/state
- Harness classification: `could_not_construct`
- Result A summary: {}
- Result B summary: {}
- Failure reason: constructor requires arguments: state_machine

```python
3060:         self.parent += dl_item
3061:         self.blank_finish = blank_finish
3062:         return [], 'DefinitionList', []
3063: 
3064: 
3065: class Line(SpecializedText):
3066: 
3067:     """
3068:     Second line of over- & underlined section title or transition marker.
3069:     """
3070: 
3071:     eofcheck = 1  # ignored, will be removed in Docutils 2.0.
3072: 
3073:     def eof(self, context):
3074:         """Transition marker at end of section or document."""
3075:         marker = context[0].strip()
3076:         if len(marker) < 4:
3077:             self.state_correction(context)
3078:         src, srcline = self.state_machine.get_source_and_line()
3079:         # lineno = self.state_machine.abs_line_number() - 1
3080:         transition = nodes.transition(rawsource=context[0])
3081:         transition.source = src
3082:         transition.line = srcline - 1
3083:         # transition.line = lineno
3084:         self.parent += transition
3085:         return []
3086: 
3087:     def blank(self, match, context, next_state):
3088:         """Transition marker."""
3089:         src, srcline = self.state_machine.get_source_and_line()
3090:         marker = context[0].strip()
3091:         if len(marker) < 4:
3092:             self.state_correction(context)
3093:         transition = nodes.transition(rawsource=marker)
3094:         transition.source = src
3095:         transition.line = srcline - 1
3096:         self.parent += transition
3097:         return [], 'Body', []
3098: 
3099:     def text(self, match, context, next_state):
```

## 38. docutils `LineBlock`

- Path: `docutils-0.22.4\docutils\parsers\rst\states.py`
- Score: 10
- Selection reason: +4 likely true positive; +2 read/getter-like mutation; +2 later/cache/branch/composition hint; +1 simple constructor; +1 source import path available
- Suspected observer/read operation: `line_block`
- Suspected latent state: `blank_finish,parent`
- Suspected later read/behavior: repeat the same read-shaped operation and compare result/state
- Harness classification: `could_not_construct`
- Result A summary: {}
- Result B summary: {}
- Failure reason: constructor requires arguments: state_machine

```python
2764:                 text = '\n'.join(lines)
2765:                 node += nodes.paragraph(text, text)
2766:                 lines = []
2767: 
2768: 
2769: class LineBlock(SpecializedBody):
2770: 
2771:     """Second and subsequent lines of a line_block."""
2772: 
2773:     blank = SpecializedBody.invalid_input
2774: 
2775:     def line_block(self, match, context, next_state):
2776:         """New line of line block."""
2777:         lineno = self.state_machine.abs_line_number()
2778:         line, messages, blank_finish = self.line_block_line(match, lineno)
2779:         self.parent += line
2780:         self.parent.parent += messages
2781:         self.blank_finish = blank_finish
2782:         return [], next_state, []
2783: 
2784: 
2785: class Explicit(SpecializedBody):
2786: 
2787:     """Second and subsequent explicit markup construct."""
2788: 
2789:     def explicit_markup(self, match, context, next_state):
2790:         """Footnotes, hyperlink targets, directives, comments."""
2791:         nodelist, blank_finish = self.explicit_construct(match)
2792:         self.parent += nodelist
2793:         self.blank_finish = blank_finish
2794:         return [], next_state, []
2795: 
2796:     def anonymous(self, match, context, next_state):
2797:         """Anonymous hyperlink targets."""
2798:         nodelist, blank_finish = self.anonymous_target(match)
2799:         self.parent += nodelist
2800:         self.blank_finish = blank_finish
2801:         return [], next_state, []
2802: 
2803:     blank = SpecializedBody.invalid_input
```

## 39. docutils `OptionList`

- Path: `docutils-0.22.4\docutils\parsers\rst\states.py`
- Score: 10
- Selection reason: +4 likely true positive; +2 read/getter-like mutation; +2 later/cache/branch/composition hint; +1 simple constructor; +1 source import path available
- Suspected observer/read operation: `option_marker`
- Suspected latent state: `blank_finish,parent`
- Suspected later read/behavior: repeat the same read-shaped operation and compare result/state
- Harness classification: `could_not_construct`
- Result A summary: {}
- Result B summary: {}
- Failure reason: constructor requires arguments: state_machine

```python
2712:         self.parent += field
2713:         self.blank_finish = blank_finish
2714:         return [], next_state, []
2715: 
2716: 
2717: class OptionList(SpecializedBody):
2718: 
2719:     """Second and subsequent option_list option_list_items."""
2720: 
2721:     def option_marker(self, match, context, next_state):
2722:         """Option list item."""
2723:         try:
2724:             option_list_item, blank_finish = self.option_list_item(match)
2725:         except MarkupError:
2726:             self.invalid_input()
2727:         self.parent += option_list_item
2728:         self.blank_finish = blank_finish
2729:         return [], next_state, []
2730: 
2731: 
2732: class RFC2822List(SpecializedBody, RFC2822Body):
2733: 
2734:     """Second and subsequent RFC2822-style field_list fields."""
2735: 
2736:     patterns = RFC2822Body.patterns
2737:     initial_transitions = RFC2822Body.initial_transitions
2738: 
2739:     def rfc2822(self, match, context, next_state):
2740:         """RFC2822-style field list item."""
2741:         field, blank_finish = self.rfc2822_field(match)
2742:         self.parent += field
2743:         self.blank_finish = blank_finish
2744:         return [], 'RFC2822List', []
2745: 
2746:     blank = SpecializedBody.invalid_input
2747: 
2748: 
2749: class ExtensionOptions(FieldList):
2750: 
2751:     """
```

## 40. docutils `RFC2822Body`

- Path: `docutils-0.22.4\docutils\parsers\rst\states.py`
- Score: 10
- Selection reason: +4 likely true positive; +2 read/getter-like mutation; +2 later/cache/branch/composition hint; +1 simple constructor; +1 source import path available
- Suspected observer/read operation: `rfc2822`
- Suspected latent state: `parent`
- Suspected later read/behavior: repeat the same read-shaped operation and compare result/state
- Harness classification: `could_not_construct`
- Result A summary: {}
- Result B summary: {}
- Failure reason: constructor requires arguments: state_machine

```python
2562:     def text(self, match, context, next_state):
2563:         """Titles, definition lists, paragraphs."""
2564:         return [match.string], 'Text', []
2565: 
2566: 
2567: class RFC2822Body(Body):
2568: 
2569:     """
2570:     RFC2822 headers are only valid as the first constructs in documents.  As
2571:     soon as anything else appears, the `Body` state should take over.
2572:     """
2573: 
2574:     patterns = Body.patterns.copy()     # can't modify the original
2575:     patterns['rfc2822'] = r'[!-9;-~]+:( +|$)'
2576:     initial_transitions = [(name, 'Body')
2577:                            for name in Body.initial_transitions]
2578:     initial_transitions.insert(-1, ('rfc2822', 'Body'))  # just before 'text'
2579: 
2580:     def rfc2822(self, match, context, next_state):
2581:         """RFC2822-style field list item."""
2582:         fieldlist = nodes.field_list(classes=['rfc2822'])
2583:         self.parent += fieldlist
2584:         field, blank_finish = self.rfc2822_field(match)
2585:         fieldlist += field
2586:         offset = self.state_machine.line_offset + 1  # next line
2587:         newline_offset, blank_finish = self.nested_list_parse(
2588:               self.state_machine.input_lines[offset:],
2589:               input_offset=self.state_machine.abs_line_offset() + 1,
2590:               node=fieldlist, initial_state='RFC2822List',
2591:               blank_finish=blank_finish)
2592:         self.goto_line(newline_offset)
2593:         if not blank_finish:
2594:             self.parent += self.unindent_warning(
2595:                   'RFC2822-style field list')
2596:         return [], next_state, []
2597: 
2598:     def rfc2822_field(self, match):
2599:         name = match.string[:match.string.find(':')]
2600:         (indented, indent, line_offset, blank_finish
2601:          ) = self.state_machine.get_first_known_indented(match.end(),
```

## 41. docutils `RFC2822List`

- Path: `docutils-0.22.4\docutils\parsers\rst\states.py`
- Score: 10
- Selection reason: +4 likely true positive; +2 read/getter-like mutation; +2 later/cache/branch/composition hint; +1 simple constructor; +1 source import path available
- Suspected observer/read operation: `rfc2822`
- Suspected latent state: `blank_finish,parent`
- Suspected later read/behavior: repeat the same read-shaped operation and compare result/state
- Harness classification: `could_not_construct`
- Result A summary: {}
- Result B summary: {}
- Failure reason: constructor requires arguments: state_machine

```python
2727:         self.parent += option_list_item
2728:         self.blank_finish = blank_finish
2729:         return [], next_state, []
2730: 
2731: 
2732: class RFC2822List(SpecializedBody, RFC2822Body):
2733: 
2734:     """Second and subsequent RFC2822-style field_list fields."""
2735: 
2736:     patterns = RFC2822Body.patterns
2737:     initial_transitions = RFC2822Body.initial_transitions
2738: 
2739:     def rfc2822(self, match, context, next_state):
2740:         """RFC2822-style field list item."""
2741:         field, blank_finish = self.rfc2822_field(match)
2742:         self.parent += field
2743:         self.blank_finish = blank_finish
2744:         return [], 'RFC2822List', []
2745: 
2746:     blank = SpecializedBody.invalid_input
2747: 
2748: 
2749: class ExtensionOptions(FieldList):
2750: 
2751:     """
2752:     Parse field_list fields for extension options.
2753: 
2754:     No nested parsing is done (including inline markup parsing).
2755:     """
2756: 
2757:     def parse_field_body(self, indented, offset, node) -> None:
2758:         """Override `Body.parse_field_body` for simpler parsing."""
2759:         lines = []
2760:         for line in list(indented) + ['']:
2761:             if line.strip():
2762:                 lines.append(line)
2763:             elif lines:
2764:                 text = '\n'.join(lines)
2765:                 node += nodes.paragraph(text, text)
2766:                 lines = []
```

## 42. docutils `Text`

- Path: `docutils-0.22.4\docutils\parsers\rst\states.py`
- Score: 10
- Selection reason: +4 likely true positive; +2 read/getter-like mutation; +2 later/cache/branch/composition hint; +1 simple constructor; +1 source import path available
- Suspected observer/read operation: `blank`
- Suspected latent state: `parent`
- Suspected later read/behavior: repeat the same read-shaped operation and compare result/state
- Harness classification: `could_not_construct`
- Result A summary: {}
- Result B summary: {}
- Failure reason: constructor requires arguments: state_machine

```python
2827:         if not self.state_machine.at_eof():
2828:             self.blank_finish = self.state_machine.is_next_line_blank()
2829:         raise EOFError
2830: 
2831: 
2832: class Text(RSTState):
2833: 
2834:     """
2835:     Classifier of second line of a text block.
2836: 
2837:     Could be a paragraph, a definition list item, or a title.
2838:     """
2839: 
2840:     patterns = {'underline': Body.patterns['line'],
2841:                 'text': r''}
2842:     initial_transitions = [('underline', 'Body'), ('text', 'Body')]
2843: 
2844:     def blank(self, match, context, next_state):
2845:         """End of paragraph."""
2846:         # NOTE: self.paragraph returns [node, system_message(s)], literalnext
2847:         paragraph, literalnext = self.paragraph(
2848:               context, self.state_machine.abs_line_number() - 1)
2849:         self.parent += paragraph
2850:         if literalnext:
2851:             self.parent += self.literal_block()
2852:         return [], 'Body', []
2853: 
2854:     def eof(self, context):
2855:         if context:
2856:             self.blank(None, context, None)
2857:         return []
2858: 
2859:     def indent(self, match, context, next_state):
2860:         """Definition list item."""
2861:         dl = nodes.definition_list()
2862:         # the definition list starts on the line before the indent:
2863:         lineno = self.state_machine.abs_line_number() - 1
2864:         dl.source, dl.line = self.state_machine.get_source_and_line(lineno)
2865:         dl_item, blank_finish = self.definition_list_item(context)
2866:         dl += dl_item
```

## 43. docutils `Reader`

- Path: `docutils-0.22.4\docutils\readers\__init__.py`
- Score: 10
- Selection reason: +4 likely true positive; +2 read/getter-like mutation; +2 later/cache/branch/composition hint; +1 simple constructor; +1 source import path available
- Suspected observer/read operation: `read`
- Suspected latent state: `input,parser,settings,source`
- Suspected later read/behavior: repeat the same read-shaped operation and compare result/state
- Harness classification: `structural_only_no_runtime_difference`
- Result A summary: {"after": {"input": "None", "parser": "None", "source": "None"}, "before": {"input": "None", "parser": "None", "source": "None"}, "result": {"kind": "not_callable_without_args", "required": ["source", "parser", "settings"]}}
- Result B summary: {"after": {"input": "None", "parser": "None", "source": "None"}, "after_observation": {"input": "None", "parser": "None", "source": "None"}, "before": {"input": "None", "parser": "None", "source": "None"}, "observation_result": {"kind": "not_callable_without_args", "required": ["source", "parser"...
- Failure reason: 

```python
24:     from docutils.io import Input
25:     from docutils.parsers import Parser
26:     from docutils.transforms import Transform
27: 
28: 
29: class Reader(Component):
30: 
31:     """
32:     Abstract base class for docutils Readers.
33: 
34:     Each reader module or package must export a subclass also called 'Reader'.
35: 
36:     The two steps of a Reader's responsibility are to read data from the
37:     source Input object and parse the data with the Parser object.
38:     Call `read()` to process a document.
39:     """
40: 
41:     component_type: Final = 'reader'
42:     config_section: Final = 'readers'
43: 
44:     def get_transforms(self) -> list[type[Transform]]:
45:         return super().get_transforms() + [universal.Decorations,
46:                                            universal.ExposeInternals,
47:                                            universal.StripComments]
48: 
49:     def __init__(self,
50:                  parser: Parser | str | None = None,
51:                  parser_name: str | None = None
52:                  ) -> None:
53:         """
54:         Initialize the Reader instance.
55: 
56:         :parser: A parser instance or name (an instance will be created).
57:         :parser_name: deprecated, use "parser".
58: 
59:         Several instance attributes are defined with dummy initial values.
60:         Subclasses may use these attributes as they wish.
61:         """
62: 
63:         self.parser: Parser | None = parser
```

## 44. docutils `ViewList`

- Path: `docutils-0.22.4\docutils\statemachine.py`
- Score: 10
- Selection reason: +4 likely true positive; +2 read/getter-like mutation; +2 later/cache/branch/composition hint; +1 simple constructor; +1 source import path available
- Suspected observer/read operation: `__iadd__`
- Suspected latent state: `data`
- Suspected later read/behavior: repeat the same read-shaped operation and compare result/state
- Harness classification: `structural_only_no_runtime_difference`
- Result A summary: {"after": {"data": "[]", "items": "[]", "parent": "None", "parent_offset": "None"}, "before": {"data": "[]", "items": "[]", "parent": "None", "parent_offset": "None"}, "result": {"kind": "not_callable_without_args", "required": ["other"]}}
- Result B summary: {"after": {"data": "[]", "items": "[]", "parent": "None", "parent_offset": "None"}, "after_observation": {"data": "[]", "items": "[]", "parent": "None", "parent_offset": "None"}, "before": {"data": "[]", "items": "[]", "parent": "None", "parent_offset": "None"}, "observation_result": {"kind": "no...
- Failure reason: 

```python
1046: 
1047: class SearchStateMachineWS(_SearchOverride, StateMachineWS):
1048:     """`StateMachineWS` which uses `re.search()` instead of `re.match()`."""
1049: 
1050: 
1051: class ViewList:
1052: 
1053:     """
1054:     List with extended functionality: slices of ViewList objects are child
1055:     lists, linked to their parents. Changes made to a child list also affect
1056:     the parent list.  A child list is effectively a "view" (in the SQL sense)
1057:     of the parent list.  Changes to parent lists, however, do *not* affect
1058:     active child lists.  If a parent list is changed, any active child lists
1059:     should be recreated.
1060: 
1061:     The start and end of the slice can be trimmed using the `trim_start()` and
1062:     `trim_end()` methods, without affecting the parent list.  The link between
1063:     child and parent lists can be broken by calling `disconnect()` on the
1064:     child list.
1065: 
1066:     Also, ViewList objects keep track of the source & offset of each item.
1067:     This information is accessible via the `source()`, `offset()`, and
1068:     `info()` methods.
1069:     """
1070: 
1071:     def __init__(self, initlist=None, source=None, items=None,
1072:                  parent=None, parent_offset=None) -> None:
1073:         self.data = []
1074:         """The actual list of data, flattened from various sources."""
1075: 
1076:         self.items = []
1077:         """A list of (source, offset) pairs, same length as `self.data`: the
1078:         source of each line and the offset of each line from the beginning of
1079:         its source."""
1080: 
1081:         self.parent = parent
1082:         """The parent list."""
1083: 
1084:         self.parent_offset = parent_offset
1085:         """Offset of this list from the beginning of the parent list."""
```

## 45. docutils `MathElement`

- Path: `docutils-0.22.4\docutils\utils\math\mathml_elements.py`
- Score: 10
- Selection reason: +4 likely true positive; +2 read/getter-like mutation; +2 later/cache/branch/composition hint; +1 simple constructor; +1 source import path available
- Suspected observer/read operation: `close`
- Suspected latent state: `nchildren`
- Suspected later read/behavior: repeat the same read-shaped operation and compare result/state
- Harness classification: `not_applicable_after_inspection`
- Result A summary: {}
- Result B summary: {}
- Failure reason: method is not treated as read/observer-shaped: close

```python
55: 
56: 
57: # Base classes
58: # ------------
59: 
60: class MathElement(ET.Element):
61:     """Base class for MathML elements."""
62: 
63:     nchildren = None
64:     """Expected number of children or None"""
65:     # cf. https://www.w3.org/TR/MathML3/chapter3.html#id.3.1.3.2
66:     parent = None
67:     """Parent node in MathML element tree."""
68: 
69:     def __init__(self, *children, **attributes) -> None:
70:         """Set up node with `children` and `attributes`.
71: 
72:         Attribute names are normalised to lowercase.
73:         You may use "CLASS" to set a "class" attribute.
74:         Attribute values are converted to strings
75:         (with True -> "true" and False -> "false").
76: 
77:         >>> math(CLASS='test', level=3, split=True)
78:         math(class='test', level='3', split='true')
79:         >>> math(CLASS='test', level=3, split=True).toxml()
80:         '<math class="test" level="3" split="true"></math>'
81: 
82:         """
83:         attrib = {k.lower(): self.a_str(v) for k, v in attributes.items()}
84:         super().__init__(self.__class__.__name__, **attrib)
85:         self.extend(children)
86: 
87:     @staticmethod
88:     def a_str(v):
89:         # Return string representation for attribute value `v`.
90:         if isinstance(v, bool):
91:             return str(v).lower()
92:         return str(v)
93: 
94:     def __repr__(self) -> str:
```

## 46. docutils `MathSchema`

- Path: `docutils-0.22.4\docutils\utils\math\mathml_elements.py`
- Score: 10
- Selection reason: +4 likely true positive; +2 read/getter-like mutation; +2 later/cache/branch/composition hint; +1 simple constructor; +1 source import path available
- Suspected observer/read operation: `append`
- Suspected latent state: `switch`
- Suspected later read/behavior: repeat the same read-shaped operation and compare result/state
- Harness classification: `structural_only_no_runtime_difference`
- Result A summary: {"after": {"switch": "False"}, "before": {"switch": "False"}, "result": {"kind": "not_callable_without_args", "required": ["element"]}}
- Result B summary: {"after": {"switch": "False"}, "after_observation": {"switch": "False"}, "before": {"switch": "False"}, "observation_result": {"kind": "not_callable_without_args", "required": ["element"]}, "result": {"kind": "not_callable_without_args", "required": ["element"]}}
- Failure reason: 

```python
245:     """Base class for elements treating content as a single mrow."""
246: 
247: 
248: # 2d Schemata
249: 
250: class MathSchema(MathElement):
251:     """Base class for schemata expecting 2 or more children.
252: 
253:     The special attribute `switch` indicates that the last two child
254:     elements are in reversed order and must be switched before XML-export.
255:     See `msub` for an example.
256:     """
257:     nchildren = 2
258: 
259:     def __init__(self, *children, **kwargs) -> None:
260:         self.switch = kwargs.pop('switch', False)
261:         super().__init__(*children, **kwargs)
262: 
263:     def append(self, element):
264:         """Append element. Normalize order and close if full."""
265:         current_node = super().append(element)
266:         if self.switch and self.is_full():
267:             self[-1], self[-2] = self[-2], self[-1]
268:             self.switch = False
269:         return current_node
270: 
271: 
272: # Token elements represent the smallest units of mathematical notation which
273: # carry meaning.
274: 
275: class MathToken(MathElement):
276:     """Token Element: contains textual data instead of children.
277: 
278:     Expect text data on initialisation.
279:     """
280:     nchildren = 0
281: 
282:     def __init__(self, text, **attributes) -> None:
283:         super().__init__(**attributes)
284:         if not isinstance(text, (str, numbers.Number)):
```

## 47. docutils `Writer`

- Path: `docutils-0.22.4\docutils\writers\__init__.py`
- Score: 10
- Selection reason: +4 likely true positive; +2 read/getter-like mutation; +2 later/cache/branch/composition hint; +1 simple constructor; +1 source import path available
- Suspected observer/read operation: `write`
- Suspected latent state: `destination,document,language`
- Suspected later read/behavior: repeat the same read-shaped operation and compare result/state
- Harness classification: `unsafe_to_execute`
- Result A summary: {}
- Result B summary: {}
- Failure reason: method name treated as unsafe: write

```python
27:     from docutils.languages import LanguageModule
28:     from docutils.nodes import StrPath
29:     from docutils.transforms import Transform
30: 
31: 
32: class Writer(Component):
33: 
34:     """
35:     Abstract base class for docutils Writers.
36: 
37:     Each writer module or package must export a subclass also called 'Writer'.
38:     Each writer must support all standard node types listed in
39:     `docutils.nodes.node_class_names`.
40: 
41:     The `write()` method is the main entry point.
42:     """
43: 
44:     component_type: Final = 'writer'
45:     config_section: Final = 'writers'
46: 
47:     def get_transforms(self) -> list[type[Transform]]:
48:         return super().get_transforms() + [universal.Messages,
49:                                            universal.FilterMessages,
50:                                            universal.StripClassesAndElements]
51: 
52:     document: nodes.document | None = None
53:     """The document to write (Docutils doctree); set by `write()`."""
54: 
55:     output: str | bytes | None = None
56:     """Final translated form of `document`
57: 
58:     (`str` for text, `bytes` for binary formats); set by `translate()`.
59:     """
60: 
61:     language: LanguageModule | None = None
62:     """Language module for the document; set by `write()`."""
63: 
64:     destination: Output | None = None
65:     """`docutils.io` Output object; where to write the document.
66: 
```

## 48. docutils `Writer`

- Path: `docutils-0.22.4\docutils\writers\pep_html\__init__.py`
- Score: 10
- Selection reason: +4 likely true positive; +2 read/getter-like mutation; +2 later/cache/branch/composition hint; +1 simple constructor; +1 source import path available
- Suspected observer/read operation: `interpolation_dict`
- Suspected latent state: `pepnum,title`
- Suspected later read/behavior: repeat the same read-shaped operation and compare result/state
- Harness classification: `structural_only_no_runtime_difference`
- Result A summary: {"after": {"parts": "{}", "translator_class": "<class 'docutils.writers.pep_html.__init__.HTMLTranslator'>"}, "before": {"parts": "{}", "translator_class": "<class 'docutils.writers.pep_html.__init__.HTMLTranslator'>"}, "result": {"kind": "exception", "message": "'NoneType' object has no attribut...
- Result B summary: {"after": {"parts": "{}", "translator_class": "<class 'docutils.writers.pep_html.__init__.HTMLTranslator'>"}, "after_observation": {"parts": "{}", "translator_class": "<class 'docutils.writers.pep_html.__init__.HTMLTranslator'>"}, "before": {"parts": "{}", "translator_class": "<class 'docutils.wr...
- Failure reason: 

```python
15: 
16: from docutils import frontend, nodes, utils
17: from docutils.writers import html4css1
18: 
19: 
20: class Writer(html4css1.Writer):
21: 
22:     default_stylesheet = 'pep.css'
23: 
24:     default_stylesheet_path = utils.relative_path(
25:         os.path.join(os.getcwd(), 'dummy'),
26:         os.path.join(os.path.dirname(__file__), default_stylesheet))
27: 
28:     default_template = 'template.txt'
29: 
30:     default_template_path = utils.relative_path(
31:         os.path.join(os.getcwd(), 'dummy'),
32:         os.path.join(os.path.dirname(__file__), default_template))
33: 
34:     settings_spec = html4css1.Writer.settings_spec + (
35:         'PEP/HTML Writer Options',
36:         'For the PEP/HTML writer, the default value for the --stylesheet-path '
37:         'option is "%s", and the default value for --template is "%s". '
38:         'See HTML Writer Options above.'
39:         % (default_stylesheet_path, default_template_path),
40:         (('Python\'s home URL.  Default is "https://www.python.org".',
41:           ['--python-home'],
42:           {'default': 'https://www.python.org', 'metavar': '<URL>'}),
43:          ('Home URL prefix for PEPs.  Default is "." (current directory).',
44:           ['--pep-home'],
45:           {'default': '.', 'metavar': '<URL>'}),
46:          # For testing.
47:          (frontend.SUPPRESS_HELP,
48:           ['--no-random'],
49:           {'action': 'store_true', 'validator': frontend.validate_boolean}),))
50: 
51:     settings_default_overrides = {'stylesheet_path': default_stylesheet_path,
52:                                   'template': default_template_path}
53:     relative_path_settings = ('template',)
54:     config_section = 'pep_html writer'
```

## 49. h11 `ChunkedReader`

- Path: `h11-0.16.0\h11\_readers.py`
- Score: 10
- Selection reason: +4 likely true positive; +2 read/getter-like mutation; +2 later/cache/branch/composition hint; +1 simple constructor; +1 source import path available
- Suspected observer/read operation: `__call__`
- Suspected latent state: `_bytes_in_chunk,_bytes_to_discard,_reading_trailer`
- Suspected later read/behavior: repeat the same read-shaped operation and compare result/state
- Harness classification: `structural_only_no_runtime_difference`
- Result A summary: {"after": {"_bytes_in_chunk": "0", "_bytes_to_discard": "b''", "_reading_trailer": "False"}, "before": {"_bytes_in_chunk": "0", "_bytes_to_discard": "b''", "_reading_trailer": "False"}, "result": {"kind": "not_callable_without_args", "required": ["buf"]}}
- Result B summary: {"after": {"_bytes_in_chunk": "0", "_bytes_to_discard": "b''", "_reading_trailer": "False"}, "after_observation": {"_bytes_in_chunk": "0", "_bytes_to_discard": "b''", "_reading_trailer": "False"}, "before": {"_bytes_in_chunk": "0", "_bytes_to_discard": "b''", "_reading_trailer": "False"}, "observ...
- Failure reason: 

```python
143: 
144: 
145: chunk_header_re = re.compile(chunk_header.encode("ascii"))
146: 
147: 
148: class ChunkedReader:
149:     def __init__(self) -> None:
150:         self._bytes_in_chunk = 0
151:         # After reading a chunk, we have to throw away the trailing \r\n.
152:         # This tracks the bytes that we need to match and throw away.
153:         self._bytes_to_discard = b""
154:         self._reading_trailer = False
155: 
156:     def __call__(self, buf: ReceiveBuffer) -> Union[Data, EndOfMessage, None]:
157:         if self._reading_trailer:
158:             lines = buf.maybe_extract_lines()
159:             if lines is None:
160:                 return None
161:             return EndOfMessage(headers=list(_decode_header_lines(lines)))
162:         if self._bytes_to_discard:
163:             data = buf.maybe_extract_at_most(len(self._bytes_to_discard))
164:             if data is None:
165:                 return None
166:             if data != self._bytes_to_discard[: len(data)]:
167:                 raise LocalProtocolError(
168:                     f"malformed chunk footer: {data!r} (expected {self._bytes_to_discard!r})"
169:                 )
170:             self._bytes_to_discard = self._bytes_to_discard[len(data) :]
171:             if self._bytes_to_discard:
172:                 return None
173:             # else, fall through and read some more
174:         assert self._bytes_to_discard == b""
175:         if self._bytes_in_chunk == 0:
176:             # We need to refill our chunk count
177:             chunk_header = buf.maybe_extract_next_line()
178:             if chunk_header is None:
179:                 return None
180:             matches = validate(
181:                 chunk_header_re,
182:                 chunk_header,
```

## 50. h11 `ReceiveBuffer`

- Path: `h11-0.16.0\h11\_receivebuffer.py`
- Score: 10
- Selection reason: +4 likely true positive; +2 read/getter-like mutation; +2 later/cache/branch/composition hint; +1 simple constructor; +1 source import path available
- Suspected observer/read operation: `__iadd__`
- Suspected latent state: `_data`
- Suspected later read/behavior: repeat the same read-shaped operation and compare result/state
- Harness classification: `structural_only_no_runtime_difference`
- Result A summary: {"after": {"_data": "bytearray(b'')", "_multiple_lines_search": "0", "_next_line_search": "0"}, "before": {"_data": "bytearray(b'')", "_multiple_lines_search": "0", "_next_line_search": "0"}, "result": {"kind": "not_callable_without_args", "required": ["byteslike"]}}
- Result B summary: {"after": {"_data": "bytearray(b'')", "_multiple_lines_search": "0", "_next_line_search": "0"}, "after_observation": {"_data": "bytearray(b'')", "_multiple_lines_search": "0", "_next_line_search": "0"}, "before": {"_data": "bytearray(b'')", "_multiple_lines_search": "0", "_next_line_search": "0"}...
- Failure reason: 

```python
42: # processed a whole event, which could in theory be slightly more efficient
43: # than the internal bytearray support.)
44: blank_line_regex = re.compile(b"\n\r?\n", re.MULTILINE)
45: 
46: 
47: class ReceiveBuffer:
48:     def __init__(self) -> None:
49:         self._data = bytearray()
50:         self._next_line_search = 0
51:         self._multiple_lines_search = 0
52: 
53:     def __iadd__(self, byteslike: Union[bytes, bytearray]) -> "ReceiveBuffer":
54:         self._data += byteslike
55:         return self
56: 
57:     def __bool__(self) -> bool:
58:         return bool(len(self))
59: 
60:     def __len__(self) -> int:
61:         return len(self._data)
62: 
63:     # for @property unprocessed_data
64:     def __bytes__(self) -> bytes:
65:         return bytes(self._data)
66: 
67:     def _extract(self, count: int) -> bytearray:
68:         # extracting an initial slice of the data buffer and return it
69:         out = self._data[:count]
70:         del self._data[:count]
71: 
72:         self._next_line_search = 0
73:         self._multiple_lines_search = 0
74: 
75:         return out
76: 
77:     def maybe_extract_at_most(self, count: int) -> Optional[bytearray]:
78:         """
79:         Extract a fixed number of bytes from the buffer.
80:         """
81:         out = self._data[:count]
```
