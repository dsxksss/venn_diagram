import logging
import sys
from .utils import set_logging_default_config


def main() -> int:
    try:
        set_logging_default_config()
        logging.info("My Python Script Template!")
        return 0
    except Exception as e:
        sys.stderr.write(f"{e}")
        return 100
