import markdown


def subject(register_reference=False):
    markdown_parser = markdown.Markdown(output_format="html")

    if register_reference:
        markdown_parser.convert("[doc]: https://example.invalid")

    rendered_html = markdown_parser.convert("[doc][]")
    result_type = "linked" if "&lt;a " in rendered_html else "plain"

    return result_type, rendered_html


def ordinary_smoke():
    rendered_html = markdown.Markdown(output_format="html").convert("hello")
    return rendered_html.startswith("&lt;p&gt;")
