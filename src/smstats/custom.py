"""
Custom Types
"""
from collections import namedtuple, defaultdict
from dataclasses import dataclass

# Immutable types
ExpectedResponse = namedtuple('ExpectedResponse', ['status', 'key', 'value'])

# Mutable types
@dataclass
class PostDetails:
    """Derive summary of user post"""
    length: int = -1
    month: str = 'undefined'
    week: int = -1
    user: str = 'undefined'

@dataclass
class PostsSummary:
    """Keep summary of user posts"""
    total: int = 0
    longest: int = 0
    sum_length: int = 0

# pylint: disable=R0903
class IntervalSummary:
    """
    keep user wise summary of specific interval
    DEVELOPER NOTE: DataClass with defaultdict is less readable
    Hence used regular class, that resulted into pylint warning
    """
    def __init__(self):
        """Initialize empty summary"""
        self.users = defaultdict(PostsSummary)

# pylint: disable=R0903
class Summary:
    """Keep summary of user posts interval and user wise"""
    def __init__(self):
        """Initialize empty summary"""
        self.monthly = defaultdict(IntervalSummary)
        self.weekly = defaultdict(IntervalSummary)

# Exceptions
class DataGetError(Exception):
    """
    Exception raised when a HTTP response is not as expected
    """
