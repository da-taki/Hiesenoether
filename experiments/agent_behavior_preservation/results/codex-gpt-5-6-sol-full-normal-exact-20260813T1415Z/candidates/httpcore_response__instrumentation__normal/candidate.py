import logging

import httpcore


logger = logging.getLogger(__name__)


def subject(pre_materialize=False):
    resp = httpcore.Response(200, content=[b"alpha", b"beta"])
    if pre_materialize:
        logger.debug("Materializing response body")
        resp.read()
        logger.debug("Response body materialized")
    try:
        logger.debug("Accessing response content")
        body = resp.content
        logger.debug("Response content is ready")
        return ("content_ready", body.decode())
    except RuntimeError:
        logger.debug("Response content is still streaming")
        return ("stream_pending", None)


def ordinary_smoke():
    resp = httpcore.Response(200, content=b"alpha")
    return resp.status == 200
