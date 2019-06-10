import warnings
import requests
from gettext import gettext as _
try:
    from urllib.parse import urljoin
except ImportError:
    from urlparse import urljoin

from .exceptions import BaseException


class BaseAuthClient(object):
    """ Basic client to access (non)authorized REST APIs """
    def __init__(self, base_url, session=None):
        """
        :param base_url: Base URL. API endpoint paths will always be relative to this URL
        :param session: requests' session
        :return:
        """
        self.base_url = base_url
        if session is None:
            self.session = requests.Session()
        else:
            self.session = session

    def send(self, relative_path, http_method, **requests_args):
        """
        Subclasses must implement this method, that will be used to send API requests with proper auth
        :param relative_path: URL path relative to self.base_url
        :param http_method: HTTP method
        :param requests_args: kargs to be sent to requests
        :return:
        """
        url = urljoin(self.base_url, relative_path)

        return self.session.request(http_method, url, **requests_args)

    def get_response_data(self, response, parse_json=True):
        """
        Get response data or throw an appropiate exception
        :param response: requests response object
        :param parse_json: if True, response will be parsed as JSON
        :return: response data, either as json or as a regular response.content object
        """
        if response.status_code < 400:
            if response.status_code != requests.codes.no_content:
                if parse_json:
                    return response.json()
                return response.content
        else:
            raise BaseException.create(response)


class NoAuthClient(BaseAuthClient):
    """
    This class provides you with simple unauthenticated access to APIs
    """

    def send(self, relative_path, http_method, **requests_args):
        """
        Make a unauthorized request
        :param relative_path: URL path relative to self.base_url
        :param http_method: HTTP method
        :param requests_args: kargs to be sent to requests
        :return: requests' response object
        """
        if http_method != "get":
            warnings.warn(_("You are using methods other than get with no authentication!!!"))

        return super(NoAuthClient, self).send(relative_path, http_method, **requests_args)


class TokenAuthClient(BaseAuthClient):
    """
    This class provides you with authenticated access to APIs using a token-based HTTP Authentication scheme
    The token will be included in the Authorization HTTP header, prefixed by a keyword (default: "Token"), with whitespace separating the two strings
    """
    def __init__(self, token, *args, **kwargs):
        """
        :param Token: Authentication token
        :param header_keyword: Authorization HTTP header prefix
        :return:
        """
        if 'header_keyword' in kwargs:
            header_keyword = kwargs['header_keyword']
            del kwargs['header_keyword']
        else:
            header_keyword = "Token"

        if not self.base_url.startswith('https'):
            warnings.warn(_("You are using unencrypted token authentication!!!"))

        super(TokenAuthClient, self).__init__(*args, **kwargs)

        self.session.headers.update({"authentication": "{keyword} {token}".format(keyword=header_keyword, token=token)})


class BasicAuthClient(BaseAuthClient):
    """
    This class provides you with authenticated access to APIs using a basic HTTP Authentication scheme
    """
    def __init__(self, user_name, password, *args, **kwargs):
        """
        :param user_name: User name for basic authentication
        :param password: Password for basic authentication
        :return:
        """
        super(BasicAuthClient, self).__init__(*args, **kwargs)

        self.session.auth = (user_name, password)
