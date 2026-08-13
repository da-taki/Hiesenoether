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
    logger.handlers = []
    logger.propagate = False
    logger.setLevel(logging.DEBUG)
    handler = ListHandler()
    handler.setLevel(logging.NOTSET)
    logger.addHandler(handler)

    diagnostic_logger = logging.getLogger("agent_bp_pytest_case.diagnostics")
    diagnostic_logger.debug(
        "Starting subject operation: pre_adjust=%r", pre_adjust
    )

    if pre_adjust:
        diagnostic_logger.debug("Entering temporary logging adjustment")
        cm = catching_logs(handler, level=logging.ERROR)
        cm.__enter__()
        diagnostic_logger.debug("Exiting temporary logging adjustment")
        cm.__exit__(None, None, None)

    diagnostic_logger.debug("Emitting warning")
    logger.warning("disk almost full")
    diagnostic_logger.debug("Completed subject operation")

    return ("warning_seen", tuple(handler.messages)) if handler.messages else (
        "warning_hidden",
        (),
    )


def ordinary_smoke():
    return isinstance(ListHandler(), logging.Handler)
