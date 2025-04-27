import logging
import os
import sys
from colorama import Fore, init

init(autoreset=True)
ROOT = os.path.dirname(__file__)


class ColorizeFilter(logging.Filter):
    def filter(self, record):
        if record.levelno == logging.DEBUG:
            record.levelname = f"{Fore.BLUE}{record.levelname}{Fore.RESET}"
        elif record.levelno == logging.INFO:
            record.levelname = f"{Fore.GREEN}{record.levelname}{Fore.RESET}"
        elif record.levelno == logging.WARNING:
            record.levelname = f"{Fore.YELLOW}{record.levelname}{Fore.RESET}"
        elif record.levelno == logging.ERROR:
            record.levelname = f"{Fore.RED}{record.levelname}{Fore.RESET}"
        elif record.levelno == logging.CRITICAL:
            record.levelname = f"{Fore.MAGENTA}{record.levelname}{Fore.RESET}"
        return True


def get_logger(name="main-logger", level=logging.INFO):
    if not os.path.exists(os.path.join(ROOT, "logs")):
        os.mkdir(os.path.join(ROOT, "logs"))

    logger = logging.getLogger(name)
    logger.setLevel(level)
    if not logger.handlers:
        fh = logging.FileHandler(os.path.join(ROOT, "logs", "app.log"), mode="a")
        fh.setLevel(level)
        fh.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))

        eh = logging.FileHandler(os.path.join(ROOT, "logs", "error.log"), mode="a")
        eh.setLevel(level)
        eh.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))

        sh = logging.StreamHandler(sys.stdout)
        sh.setLevel(level)
        sh.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))
        sh.addFilter(ColorizeFilter())

        logger.addHandler(fh)
        logger.addHandler(eh)
        logger.addHandler(sh)

    return logger


def change_logger_level(logger, level=logging.DEBUG):
    logger.setLevel(level)
    for handler in logger.handlers:
        handler.setLevel(level)
