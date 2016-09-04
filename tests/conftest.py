import pytest

from pyrestcli.auth import BasicAuthClient


@pytest.fixture(scope="session")
def basic_auth_client():
    """
    Returns a basic HTTP authentication client that can be used to send authenticated test requests to the server
    :return: BasicAuthClient instance
    """
    return BasicAuthClient("admin", "password123", "http://localhost:8000")
