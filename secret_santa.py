#!/usr/bin/env python
import argparse
import inspect
import logging
import sys
import os

from santa_lib.common import setup_logger
from santa_lib.santa import Santa




def main():
    parser = argparse.ArgumentParser(description='Secret Santa Matcher')
    parser.add_argument('--send', action="store_true", dest="send", default=False,
                        help="Actually send email (defaults to dry run mode)")
    parser.add_argument('--resend', action="store_true", dest="resend", default=False,
                        help="Resend the emails saved in santa_logs, skip pairing")
    parser.add_argument('--report', action="store_true", dest="report", default=False,
                        help="Generate a report on the candidates")

    args = parser.parse_args()

    logger = setup_logger(['console_logger', 'file_logger'], 'secret_santa.log')

    send = args.send
    report = args.report
    config_file = inspect.getfile(inspect.currentframe()).replace(".py", ".yml")
    santa = Santa(logger, send, report, args.resend, config_file)
    santa.process_data()


if __name__ == "__main__":
    sys.exit(main())
