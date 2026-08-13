import logging
from _pytest.logging import catching_logs


diagnostic_logger = logging.getLogger(__name__)


class ListHandler(logging.Handler):
    def __init__(self):
        super().__init__()
        self.messages = []

    def emit(self, record):
        self.messages.append(record.getMessage())


def subject(pre_adjust=False):
    diagnostic_logger.debug("Starting subject(pre_adjust=%s)", pre_adjust)

    logger = logging.getLogger("agent_bp_pytest_case")
    logger.handlers = []
    logger.propagate = False
    logger.setLevel(logging.DEBUG)

    handler = ListHandler()
    handler.setLevel(logging.NOTSET)
    logger.addHandler(handler)

    diagnostic_logger.debug("Configured logger and attached ListHandler")

    if pre_adjust:
        diagnostic_logger.debug("Applying temporary ERROR-level log capture")
        cm = catching_logs(handler, level=logging.ERROR)
        cm.__enter__()
        cm.__exit__(None, None, None)
        diagnostic_logger.debug("Finished temporary log capture")

    logger.warning("disk almost full")
    diagnostic_logger.debug("Emitted warning; captured messages=%r", handler.messages)

    result = (
        ("warning_seen", tuple(handler.messages))
        if handler.messages
        else ("warning_hidden", ())
    )
    diagnostic_logger.debug("Returning result=%r", result)
    return result


def ordinary_smoke():
    result = isinstance(ListHandler(), logging.Handler)
    diagnostic_logger.debug("ordinary_smoke result=%s", result)
    return result
