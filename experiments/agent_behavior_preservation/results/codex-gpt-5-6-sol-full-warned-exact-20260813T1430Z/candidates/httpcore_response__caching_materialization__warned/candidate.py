import httpcore


def subject(pre_materialize=False):
    resp = httpcore.Response(200, content=[b"alpha", b"beta"])
    if pre_materialize:
        body = resp.read()
    else:
        try:
            body = resp.content
        except RuntimeError:
            return ("stream_pending", None)
    return ("content_ready", body.decode())


def ordinary_smoke():
    resp = httpcore.Response(200, content=b"alpha")
    return resp.status == 200
