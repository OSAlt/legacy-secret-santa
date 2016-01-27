import inspect
import logging
import os


def setup_logger(settings, file_name):
    #Create logs directory
    if not os.path.exists('logs'):
        os.mkdir('logs')

    if file_name is None:
        path = os.path.join(os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))))
        log_file = os.path.basename(__file__).replace(".py", ".log")
    else:
        log_file = file_name
        path = os.path.join(os.getcwd(), 'logs')

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
