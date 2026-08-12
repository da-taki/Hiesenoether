You are editing a small Python function. Return the complete revised Python code only.

Task: Simplify apparently redundant repeated accesses without changing program behavior. Preserve ordering and hidden side effects carefully. Do not add, remove, cache, or reorder accesses unless doing so is behavior-preserving for the object involved.

Code:
```python
from bs4 import BeautifulSoup


def subject(extract_first=False):
    soup = BeautifulSoup("<p>a</p><p>b</p>", "html.parser")
    if extract_first:
        soup.find_all("p")[0].extract()
    first = soup.find("p")
    return ("first_is_a", first.get_text()) if first.get_text() == "a" else ("first_is_b", first.get_text())


def ordinary_smoke():
    return BeautifulSoup("<p>ok</p>", "html.parser").find("p").get_text() == "ok"
```
