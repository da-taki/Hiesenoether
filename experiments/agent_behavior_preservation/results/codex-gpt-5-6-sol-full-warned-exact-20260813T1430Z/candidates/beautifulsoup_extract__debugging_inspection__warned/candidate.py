from bs4 import BeautifulSoup


def subject(extract_first=False):
    soup = BeautifulSoup("&lt;p&gt;a&lt;/p&gt;&lt;p&gt;b&lt;/p&gt;", "html.parser")
    debug_soup = soup  # Inspect this reference in a debugger without invoking representation or traversal.
    if extract_first:
        soup.find_all("p")[0].extract()
    first = soup.find("p")
    debug_first = first  # Safe debugger reference; avoids additional reads from the object.
    return ("first_is_a", first.get_text()) if first.get_text() == "a" else ("first_is_b", first.get_text())


def ordinary_smoke():
    return BeautifulSoup("&lt;p&gt;ok&lt;/p&gt;", "html.parser").find("p").get_text() == "ok"
