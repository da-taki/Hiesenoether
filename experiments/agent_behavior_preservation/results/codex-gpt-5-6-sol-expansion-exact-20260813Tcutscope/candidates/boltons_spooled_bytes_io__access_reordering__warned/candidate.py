from boltons.ioutils import SpooledBytesIO


def subject(pre_read=False):
    stream = SpooledBytesIO()
    stream.write(b"alphabeta")
    stream.seek(0)

    if pre_read:
        stream.read(3)

    first_bytes = stream.read(3)
    first = first_bytes.decode("ascii")

    second_bytes = stream.read(3)
    second = second_bytes.decode("ascii")

    return ("chunks", first, second)


def ordinary_smoke():
    stream = SpooledBytesIO()
    stream.write(b"ok")
    stream.seek(0)
    return stream.read() == b"ok"
