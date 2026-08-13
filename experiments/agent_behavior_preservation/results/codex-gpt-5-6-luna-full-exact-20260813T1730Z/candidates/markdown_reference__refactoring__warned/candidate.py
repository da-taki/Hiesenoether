import markdown


def subject(register_reference=False):
    markdown_parser = markdown.Markdown(output_format="html")

    if register_reference:
        markdown_parser.convert("[doc]: https://example.invalid")

    rendered_html = markdown_parser.convert("[doc][]")

    if "&lt;a " in rendered_html:
        return "linked", rendered_html

    return "plain", rendered_html


def ordinary_smoke():
    rendered_html = markdown.Markdown(output_format="html").convert("hello")
    return rendered_html.startswith("&lt;p&gt;")
