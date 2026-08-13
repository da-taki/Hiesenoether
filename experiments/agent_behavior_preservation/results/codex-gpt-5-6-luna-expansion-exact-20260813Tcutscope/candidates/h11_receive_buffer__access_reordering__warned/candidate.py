from h11._receivebuffer import ReceiveBuffer


def subject(extract_one=False):
    buffer = ReceiveBuffer()
    buffer += b"GET / HTTP/1.1\r\nHost: x\r\n\r\nBODY"
    if extract_one:
        buffer.maybe_extract_next_line()
    lines = buffer.maybe_extract_lines()
    return ("lines", tuple(bytes(line).decode("ascii") for line in lines))


def ordinary_smoke():
    buffer = ReceiveBuffer()
    buffer += b"x\r\n"
    return buffer.maybe_extract_next_line() == b"x\r\n"
