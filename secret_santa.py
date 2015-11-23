#!/usr/bin/env python
import argparse
import inspect
import logging
import sys
import os
from santa_lib.santa import Santa


def setup_logger(settings):
    path = os.path.join(os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))))
    log_file = os.path.basename(__file__).replace(".py", ".log")
    location = os.path.join(path, log_file)

    # Seting up file logging
    logger = logging.getLogger(log_file)
    logger.setLevel(logging.DEBUG)
    # Ensures that log is only kept for one iteration.

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    if 'file_logger' in settings:
        # file Logger settings
        file_handler = logging.FileHandler(filename=location, mode='w')
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    if 'console_logger' in settings:
        # Console logging
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    return logger


def main():
    parser = argparse.ArgumentParser(description='Secret Santa Matcher')
    parser.add_argument('--send', action="store_true", dest="send", default=False,
                        help="Actually send email (defaults to dry run mode)")

    args = parser.parse_args()

    logger = setup_logger(['console_logger'])

    send = args.send
    config_file = inspect.getfile(inspect.currentframe()).replace(".py", ".yml")
    santa = Santa(logger, send, config_file)
    santa.process_data()


if __name__ == "__main__":
    sys.exit(main())
