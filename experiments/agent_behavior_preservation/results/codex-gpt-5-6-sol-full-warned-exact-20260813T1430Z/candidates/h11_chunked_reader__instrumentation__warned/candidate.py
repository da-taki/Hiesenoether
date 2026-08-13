import logging

from h11._events import EndOfMessage
from h11._readers import ChunkedReader
from h11._receivebuffer import ReceiveBuffer


logger = logging.getLogger(__name__)


def subject(consume_chunk=False):
    buffer = ReceiveBuffer()
    buffer += b"3\r\nabc\r\n0\r\n\r\n"
    reader = ChunkedReader()
    if consume_chunk:
        logger.debug("Calling ChunkedReader to consume a chunk")
        reader(buffer)
        logger.debug("Finished consuming a chunk")
    logger.debug("Calling ChunkedReader to read the next event")
    event = reader(buffer)
    logger.debug("Finished reading the next event")
    return ("end", type(event).__name__) if isinstance(event, EndOfMessage) else ("data", type(event).__name__)


def ordinary_smoke():
    buffer = ReceiveBuffer()
    buffer += b"0\r\n\r\n"
    return buffer is not None
