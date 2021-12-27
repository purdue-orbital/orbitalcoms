class ComsMessageParseError(ValueError):
    """Failed to parse a com message"""


class ComsDriverReadError(Exception):
    """Called when a ComsDriver cannot read a ComsMessage"""


class ComsDriverWriteError(Exception):
    """Called when a ComsDriver cannot write a message"""
