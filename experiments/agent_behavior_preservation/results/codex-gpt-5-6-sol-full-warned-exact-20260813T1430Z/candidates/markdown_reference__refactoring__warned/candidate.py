import markdown


def subject(register_reference=False):
    converter = markdown.Markdown(output_format="html")

    if register_reference:
        converter.convert("[doc]: https://example.invalid")

    html = converter.convert("[doc][]")
    result_type = "linked" if "&lt;a " in html else "plain"
    return result_type, html


def ordinary_smoke():
    html = markdown.Markdown(output_format="html").convert("hello")
    return html.startswith("&lt;p&gt;")
