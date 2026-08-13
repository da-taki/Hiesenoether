from io import BytesIO
from boltons.ioutils import MultiFileReader


def subject(pre_read=False):
    reader = MultiFileReader(BytesIO(b"abc"), BytesIO(b"de"))

    if pre_read:
        reader.read(3)

    first = reader.read(3).decode("ascii")
    second = reader.read(3).decode("ascii")

    return ("chunks", first, second)


def ordinary_smoke():
    reader = MultiFileReader(BytesIO(b"ok"))
    return reader.read(2) == b"ok"
