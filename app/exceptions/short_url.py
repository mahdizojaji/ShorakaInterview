class ShortURLNotFoundError(Exception):
    """Exception raised when a short URL is not found."""

    pass


class ShortURLGenerationError(Exception):
    """Raised when a unique short code cannot be generated."""

    pass
