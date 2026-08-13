from boltons.ioutils import SpooledBytesIO


def subject(pre_read=False):
    stream = SpooledBytesIO()
    stream.write(b"alphabeta")
    stream.seek(0)

    if pre_read:
        stream.read(3)

    first = stream.read(3).decode("ascii")
    second = stream.read(3).decode("ascii")

    return ("chunks", first, second)


def ordinary_smoke():
    stream = SpooledBytesIO()
    stream.write(b"ok")
    stream.seek(0)

    return stream.read() == b"ok"
