class Paginator(object):
    def __init__(self, base_url, params=None):
        self.base_url = base_url
        self.params = params or {}

    def get_urls(self, initial_url):
        raise NotImplemented

    def process_response(self):
        raise NotImplemented


class DummyPaginator(Paginator):
    def get_urls(self, initial_url):
        url = initial_url
        while url is not None:
            yield url, self.params
            url = None

    def process_response(self, response):
        return response


class NextWithUrlPaginator(Paginator):
    def get_urls(self, initial_url):
        self.url = initial_url
        while self.url is not None:
            yield self.url, self.params

    def process_response(self, response):
        response_json = response.json()
        try:
            self.url = response_json["next"].replace(self.base_url, "")
        except AttributeError:
            self.url = None

        return response
