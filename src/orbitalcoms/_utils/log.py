import logging


def make_logger(name, level):

    logger = logging.getLogger(name)
    logger.setLevel(level)
    return logger
