import json
import sys

ERRORS = {
    400: 'BadRequestException',
    401: 'UnauthorizedErrorException',
    403: 'ForbiddenErrorException',
    404: 'NotFoundException',
    422: 'UnprocessableEntityError',
    429: 'RateLimitException',
    500: 'ServerErrorException'
}


class BaseException(Exception):
    def __init__(self, message, status_code=None, headers=None, reason=None, url=None):
        super(Exception, self).__init__(message)
        self.status_code = status_code
        self.headers = headers
        self.reason = reason
        self.url = url

    @staticmethod
    def create(response):
        response_json = {}
        try:
            response_json = response.json()
        except json.decoder.JSONDecodeError:
            pass
        message = response_json.get("error", response_json.get("errors", response.text))
        headers = response.headers
        status_code = response.status_code
        reason = response.reason
        url = response.url

        error = ERRORS.get(status_code, 'BaseException')
        klass = getattr(sys.modules[__name__], error)
        raise klass(message, status_code, headers, reason, url)


class BadRequestException(BaseException):
    pass


class UnauthorizedErrorException(BaseException):
    def __init__(self, message, status_code=None, headers=None, reason=None, url=None):
        super(BaseException, self).__init__('Access denied')


class ForbiddenErrorException(BaseException):
    def __init__(self, message, status_code=None, headers=None, reason=None, url=None):
        super(BaseException, self).__init__('Access denied')


class NotFoundException(BaseException):
    pass


class UnprocessableEntityError(BaseException):
    pass


class RateLimitException(BaseException):
    pass


class ServerErrorException(BaseException):
    pass
