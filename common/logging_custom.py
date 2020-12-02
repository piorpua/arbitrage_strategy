import logging


class DispatchingFormatter:

    def __init__(self, formatters, default_formatter):
        self._formatters = formatters
        self._default_formatter = default_formatter

    def format(self, record):
        formatter = self._formatters.get(record.name, self._default_formatter)
        return formatter.format(record)


class LoggingCustom:

    def __init__(self):
        self.default_formatter = logging.Formatter(
            '[%(asctime)s] [%(filename)s] [line:%(lineno)d] [%(levelname)s] %(message)s'
        )

    def initialize(self, level=logging.INFO):
        custom_formatter_map = {
            'default': self.default_formatter,
        }

        handler = logging.StreamHandler()
        handler.setLevel(level)
        handler.setFormatter(DispatchingFormatter(custom_formatter_map, self.default_formatter))

        logging.basicConfig(handlers=[handler], level=level)

    def get_logging(self):
        custom_logging = logging.LoggerAdapter(
            logging.getLogger('default'),
            None
        )
        return custom_logging


logging_custom_instance = LoggingCustom()
