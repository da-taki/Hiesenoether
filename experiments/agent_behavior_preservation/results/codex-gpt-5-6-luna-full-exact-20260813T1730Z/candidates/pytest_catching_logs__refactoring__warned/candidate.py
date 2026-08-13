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

    if pre_adjust:
        log_context = catching_logs(handler, level=logging.ERROR)
        log_context.__enter__()
        log_context.__exit__(None, None, None)

    logger.warning("disk almost full")

    if handler.messages:
        return "warning_seen", tuple(handler.messages)
    return "warning_hidden", ()


def ordinary_smoke():
    return isinstance(ListHandler(), logging.Handler)
