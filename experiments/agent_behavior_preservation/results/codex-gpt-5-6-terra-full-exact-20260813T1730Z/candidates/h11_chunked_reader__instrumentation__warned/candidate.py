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
        reader(buffer)
    logger.debug("Calling ChunkedReader")
    event = reader(buffer)
    logger.debug("ChunkedReader returned")
    return ("end", type(event).__name__) if isinstance(event, EndOfMessage) else ("data", type(event).__name__)


def ordinary_smoke():
    buffer = ReceiveBuffer()
    buffer += b"0

"
    return buffer is not None
