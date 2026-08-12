import markdown


def subject(register_reference=False):
    md = markdown.Markdown(output_format="html")
    if True:
        md.convert("[doc]: https://example.invalid")
    html = md.convert("[doc][]")
    return ("linked", html) if "<a " in html else ("plain", html)


def ordinary_smoke():
    return markdown.Markdown(output_format="html").convert("hello").startswith("<p>")
