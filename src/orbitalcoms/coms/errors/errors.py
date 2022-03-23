class ComsMessageParseError(ValueError):
    """Raised when failed to parse a com message"""


class ComsDriverReadError(Exception):
    """Raised when a ComsDriver cannot read a ComsMessage"""


class ComsDriverWriteError(Exception):
    """Raised when a ComsDriver cannot write a message"""
