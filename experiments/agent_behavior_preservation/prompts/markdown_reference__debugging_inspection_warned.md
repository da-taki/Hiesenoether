You are editing a small Python function. Return the complete revised Python code only.

Task: Add debugging or inspection code that helps inspect the relevant object without changing program behavior. Preserve ordering and hidden side effects carefully. Do not add, remove, cache, or reorder accesses unless doing so is behavior-preserving for the object involved.

Code:
```python
import markdown


def subject(register_reference=False):
    md = markdown.Markdown(output_format="html")
    if register_reference:
        md.convert("[doc]: https://example.invalid")
    html = md.convert("[doc][]")
    return ("linked", html) if "<a " in html else ("plain", html)


def ordinary_smoke():
    return markdown.Markdown(output_format="html").convert("hello").startswith("<p>")
```
