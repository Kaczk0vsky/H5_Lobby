import logging
import os

from datetime import datetime

os.system("")
logger = logging.getLogger(__name__)


class CustomFormatter(logging.Formatter):
    __white = "\x1b[97m"
    __light_green = "\x1b[92;20m"
    __green = "\x1b[32;20m"
    __yellow = "\x1b[33;20m"
    __red = "\x1b[31;20m"
    __bold_red = "\x1b[31;1m"
    __dark_blue = "\x1b[34;20m"
    __reset = "\x1b[0m"

    # __base_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    __time = __green + "%(asctime)s" + __reset + " - "
    __file_name = __dark_blue + "%(name)s" + __reset + " - "
    __message = __white + "%(message)s" + __reset

    FORMATS = {
        logging.DEBUG: __time + __file_name + __white + "%(levelname)s" + __reset + " - " + __message,
        logging.INFO: __time + __file_name + __light_green + "%(levelname)s" + __reset + " - " + __message,
        logging.WARNING: __time + __file_name + __yellow + "%(levelname)s" + __reset + " - " + __message,
        logging.ERROR: __time + __file_name + __red + "%(levelname)s" + __reset + " - " + __message,
        logging.CRITICAL: __time + __file_name + __bold_red + "%(levelname)s" + __reset + " - " + __message,
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


def get_logger(name: str = None, log_dir: str = "logs") -> logging.Logger:
    logger = logging.getLogger(name or os.path.basename(__file__))
    logger.setLevel(logging.DEBUG)

    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    ch.setFormatter(CustomFormatter())

    if not logger.handlers:
        logger.addHandler(ch)

    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, f"{datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}.log")

    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)

    return logger


if __name__ == "__main__":
    log = get_logger()

    log.debug("This is DEBUG")
    log.info("This is INFO")
    log.warning("This is WARNING")
    log.error("This is ERROR")
    log.critical("This is CRITICAL")
