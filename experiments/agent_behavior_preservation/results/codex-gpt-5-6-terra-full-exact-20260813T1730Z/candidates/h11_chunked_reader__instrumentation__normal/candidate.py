from h11._events import EndOfMessage
from h11._readers import ChunkedReader
from h11._receivebuffer import ReceiveBuffer
import logging

logger = logging.getLogger(__name__)


def subject(consume_chunk=False):
    buffer = ReceiveBuffer()
    buffer += b"3
abc
0

"
    reader = ChunkedReader()
    if consume_chunk:
        logger.debug("Consuming chunk before reading next event")
        reader(buffer)
    logger.debug("Reading event from chunked buffer")
    event = reader(buffer)
    logger.debug("Read event of type %s", type(event).__name__)
    return ("end", type(event).__name__) if isinstance(event, EndOfMessage) else ("data", type(event).__name__)


def ordinary_smoke():
    buffer = ReceiveBuffer()
    buffer += b"0

"
    return buffer is not None
