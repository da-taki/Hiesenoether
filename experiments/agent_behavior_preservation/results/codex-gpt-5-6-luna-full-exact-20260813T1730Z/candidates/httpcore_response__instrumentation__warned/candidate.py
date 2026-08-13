import logging

import httpcore


logger = logging.getLogger(__name__)


def subject(pre_materialize=False):
    resp = httpcore.Response(200, content=[b"alpha", b"beta"])
    if pre_materialize:
        resp.read()
    try:
        logger.debug("Reading response content")
        body = resp.content
        logger.debug("Response content read successfully")
        return ("content_ready", body.decode())
    except RuntimeError:
        logger.debug("Response content is still pending")
        return ("stream_pending", None)


def ordinary_smoke():
    resp = httpcore.Response(200, content=b"alpha")
    return resp.status == 200
