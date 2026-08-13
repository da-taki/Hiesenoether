from io import BytesIO

from boltons.ioutils import MultiFileReader


def subject(pre_read=False):
    reader = MultiFileReader(BytesIO(b"abc"), BytesIO(b"de"))
    if pre_read:
        reader.read(3)

    first_bytes = reader.read(3)
    second_bytes = reader.read(3)
    first = first_bytes.decode("ascii")
    second = second_bytes.decode("ascii")
    return ("chunks", first, second)


def ordinary_smoke():
    return MultiFileReader(BytesIO(b"ok")).read(2) == b"ok"
