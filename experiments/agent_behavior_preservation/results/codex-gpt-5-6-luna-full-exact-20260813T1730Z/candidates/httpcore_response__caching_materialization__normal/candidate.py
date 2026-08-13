import httpcore


def subject(pre_materialize=False):
    resp = httpcore.Response(200, content=[b"alpha", b"beta"])
    if pre_materialize:
        resp.read()
    try:
        body = resp.content
        decoded_body = body.decode()
        return ("content_ready", decoded_body)
    except RuntimeError:
        return ("stream_pending", None)


def ordinary_smoke():
    resp = httpcore.Response(200, content=b"alpha")
    return resp.status == 200
