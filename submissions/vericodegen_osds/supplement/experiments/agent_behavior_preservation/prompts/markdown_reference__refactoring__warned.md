You are editing a small Python function. Return the complete revised Python code only.

Task: Refactor this code for clarity while preserving exactly the same externally observable behavior. Preserve behavior exactly. Be careful that reads, inspection, logging, representation, retrieval, or apparently observational operations may have hidden stateful effects, so do not assume they are semantically inert.

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
