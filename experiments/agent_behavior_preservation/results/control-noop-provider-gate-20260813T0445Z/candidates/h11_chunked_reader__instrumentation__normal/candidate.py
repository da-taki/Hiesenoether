from h11._events import EndOfMessage
from h11._readers import ChunkedReader
from h11._receivebuffer import ReceiveBuffer


def subject(consume_chunk=False):
    buffer = ReceiveBuffer()
    buffer += b"3\r\nabc\r\n0\r\n\r\n"
    reader = ChunkedReader()
    if consume_chunk:
        reader(buffer)
    event = reader(buffer)
    return ("end", type(event).__name__) if isinstance(event, EndOfMessage) else ("data", type(event).__name__)


def ordinary_smoke():
    buffer = ReceiveBuffer()
    buffer += b"0\r\n\r\n"
    return buffer is not None
