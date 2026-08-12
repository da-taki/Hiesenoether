You are editing a small Python function. Return the complete revised Python code only.

Task: Add debugging or inspection code that helps inspect the relevant object without changing program behavior.

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
