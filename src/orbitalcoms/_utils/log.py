import logging


def make_logger(name: str, level: int) -> logging.Logger:
    """Creates a logger at the specifed level with given name

    :param name: name of the logger
    :type name: str
    :param level: level of the logger
    :type level: int
    :returns: the logger with the given name
    :rtype: logging.Logger
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    return logger
