class BadRequestException(Exception):
    pass


class NotFoundException(Exception):
    pass


class ServerErrorException(Exception):
    pass


class AuthErrorException(Exception):
    pass


class RateLimitException(Exception):
    """429 Too Many Requests Error"""
    pass
