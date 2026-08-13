import logging

import httpcore


logger = logging.getLogger(__name__)


def subject(pre_materialize=False):
    resp = httpcore.Response(200, content=[b"alpha", b"beta"])
    if pre_materialize:
        logger.debug("Pre-materializing response content")
        resp.read()
    try:
        logger.debug("Accessing response content")
        body = resp.content
        logger.debug("Response content is ready")
        return ("content_ready", body.decode())
    except RuntimeError:
        logger.debug("Response content stream is pending")
        return ("stream_pending", None)


def ordinary_smoke():
    resp = httpcore.Response(200, content=b"alpha")
    logger.debug("Checking ordinary response status")
    return resp.status == 200
