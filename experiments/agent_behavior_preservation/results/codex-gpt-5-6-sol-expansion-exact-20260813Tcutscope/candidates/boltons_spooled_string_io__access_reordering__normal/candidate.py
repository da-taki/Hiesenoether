from boltons.ioutils import SpooledStringIO


def subject(pre_read=False):
    stream = SpooledStringIO()
    stream.write("alpha beta")
    stream.seek(0)

    if pre_read:
        stream.read(3)

    first = stream.read(3)
    second = stream.read(3)

    return "chunks", first, second


def ordinary_smoke():
    stream = SpooledStringIO()
    stream.write("ok")
    stream.seek(0)

    contents = stream.read()
    return contents == "ok"
