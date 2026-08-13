import logging
from _pytest.logging import catching_logs


class ListHandler(logging.Handler):
    def __init__(self):
        super().__init__()
        self.messages = []

    def emit(self, record):
        self.messages.append(record.getMessage())


def subject(pre_adjust=False):
    logger = logging.getLogger("agent_bp_pytest_case")
    diagnostic_logger = logging.getLogger("agent_bp_pytest_case.diagnostics")
    diagnostic_logger.debug("Starting subject operation with pre_adjust=%s", pre_adjust)

    logger.handlers = []
    logger.propagate = False
    logger.setLevel(logging.DEBUG)
    handler = ListHandler()
    handler.setLevel(logging.NOTSET)
    logger.addHandler(handler)

    if pre_adjust:
        diagnostic_logger.debug("Applying temporary logging adjustment")
        cm = catching_logs(handler, level=logging.ERROR)
        cm.__enter__()
        cm.__exit__(None, None, None)
        diagnostic_logger.debug("Temporary logging adjustment completed")

    diagnostic_logger.debug("Emitting disk space warning")
    logger.warning("disk almost full")
    result = (
        ("warning_seen", tuple(handler.messages))
        if handler.messages
        else ("warning_hidden", ())
    )
    diagnostic_logger.debug("Completed subject operation with result=%s", result)
    return result


def ordinary_smoke():
    result = isinstance(ListHandler(), logging.Handler)
    logging.getLogger("agent_bp_pytest_case.diagnostics").debug(
        "Completed ordinary smoke check with result=%s", result
    )
    return result
