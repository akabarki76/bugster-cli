class BugsterError(Exception):
    """Custom exception for Bugster-related errors."""

    def __init__(self, message, type=None):
        super().__init__(message)
        self.type = type
        self.name = self.__class__.__name__
