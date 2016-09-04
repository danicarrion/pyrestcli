class Paginator:
    def get_urls(self, initial_url):
        raise NotImplemented

    def process_response(self):
        raise NotImplemented


class DummyPaginator(Paginator):
    def get_urls(self, initial_url):
        url = initial_url
        while url is not None:
            yield url
            url = None

    def process_response(self, response):
        return response


class NextWithUrlPaginator(Paginator):
    def get_urls(self, initial_url):
        self.url = initial_url
        while self.url is not None:
            yield self.url

    def process_response(self, response):
        self.url = response["next"] if "next" in response else None

        return response
