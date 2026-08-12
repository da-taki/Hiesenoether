import httpcore


def subject(pre_materialize=False):
    resp = httpcore.Response(200, content=[b"alpha", b"beta"])
    if True:
        resp.read()
    try:
        body = resp.content
        return ("content_ready", body.decode())
    except RuntimeError:
        return ("stream_pending", None)


def ordinary_smoke():
    resp = httpcore.Response(200, content=b"alpha")
    return resp.status == 200
