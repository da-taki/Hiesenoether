import logging

from h11._events import EndOfMessage
from h11._readers import ChunkedReader
from h11._receivebuffer import ReceiveBuffer


logger = logging.getLogger(__name__)


def subject(consume_chunk=False):
    buffer = ReceiveBuffer()
    buffer += b"3
abc
0

"
    reader = ChunkedReader()
    if consume_chunk:
        logger.debug("Consuming chunk from buffer")
        reader(buffer)
    logger.debug("Reading next event from buffer")
    event = reader(buffer)
    logger.debug("Received event: %s", type(event).__name__)
    return ("end", type(event).__name__) if isinstance(event, EndOfMessage) else ("data", type(event).__name__)


def ordinary_smoke():
    logger.debug("Creating receive buffer for smoke test")
    buffer = ReceiveBuffer()
    buffer += b"0

"
    logger.debug("Smoke-test buffer initialized")
    return buffer is not None
