import markdown


def subject(register_reference=False):
    md = markdown.Markdown(output_format="html")
    if register_reference:
        md.convert("[doc]: https://example.invalid")

    html = md.convert("[doc][]")
    result = "linked" if "&lt;a " in html else "plain"
    return result, html


def ordinary_smoke():
    md = markdown.Markdown(output_format="html")
    return md.convert("hello").startswith("&lt;p&gt;")
