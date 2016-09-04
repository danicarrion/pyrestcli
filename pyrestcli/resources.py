import requests
from datetime import datetime
from urllib.parse import urljoin

from .fields import Field
from .paginators import DummyPaginator


class APIConnected:
    parse_json = True

    class Meta:
        collection_endpoint = None  # /-terminated

    def __init__(self, auth_client):
        """
        :param auth_client: Client to make (non)authorized requests
        :return:
        """
        self.client = auth_client

    @classmethod
    def get_resource_endpoint(cls, resource_id):
        return urljoin(cls.get_collection_endpoint(), str(resource_id)) if resource_id is not None else None

    @classmethod
    def get_collection_endpoint(cls):
        return cls.Meta.collection_endpoint if cls.Meta.collection_endpoint is not None else cls.__name__.lower() + "s/"

    def send(self, url, http_method, **client_args):
        """
        Make the actual request to the API
        :param url: URL
        :param http_method: The method used to make the request to the API
        :param client_args: Arguments to be sent to the auth client
        :return: requests' response object
        """
        return self.client.send(url, http_method, **client_args)


class ResourceMetaclass(type):
    def __init__(cls, name, bases, nmspc):
        super(ResourceMetaclass, cls).__init__(name, bases, nmspc)

        for klass in bases:
            if hasattr(klass, "Meta"):
                for attribute_name, attribute in klass.Meta.__dict__.items():
                    if not (attribute_name.startswith("__") or hasattr(cls.Meta, attribute_name)):
                        setattr(cls.Meta, attribute_name, attribute)

        cls.fields = []
        for attribute_name, attribute in cls.__dict__.items():
            if isinstance(attribute, Field):
                attribute.name = attribute_name
                cls.fields.append(attribute_name)


class Resource(APIConnected, metaclass=ResourceMetaclass):
    """
    Resource
    """
    class Meta():
        id_field = "id"
        name_field = "id"
        json_data = True

    def __str__(self):
        return getattr(self, self.Meta.name_field, super(Resource, self).__str__())

    def get_resource_endpoint(self):
        return super(Resource, self).get_resource_endpoint(getattr(self, self.Meta.id_field))

    def update_from_dict(self, attribute_dict):
        """
        :param data_dict: Dictionary to be mapped into object attributes
        :return:
        """
        # TODO: field support
        for field_name, field_value in attribute_dict.items():
            if self.fields is None or field_name in self.fields:
                setattr(self, field_name, field_value)

    def send(self, url, http_method, **client_args):
        """
        Make the actual request to the API
        :param url: Endpoint URL
        :param http_method: The method used to make the request to the API
        :param client_args: Arguments to be sent to the auth client
        :return:
        """
        response = super(Resource, self).send(url, http_method, **client_args)

        # Update Python object if we get back a full object from the API
        if response.status_code in (requests.codes.ok, requests.codes.created):
            try:
                self.update_from_dict(self.client.get_response_data(response, self.parse_json))
            except ValueError:
                pass

    def save(self):
        """
        Saves (creates or updates) resource on the server
        :return:
        """
        values = {}
        for field_name in self.fields:
            value = getattr(self, field_name)
            if isinstance(value, datetime):
                # TODO: Allow for different formats
                value = value.isoformat()
            if value is not None:
                values[field_name] = value

        http_headers = {'content-type': 'application/json'} if self.Meta.json_data is True else None
        json = values if self.Meta.json_data is True else None
        data = values if self.Meta.json_data is False else None

        if self.get_resource_endpoint() is not None:
            self.send(self.get_resource_endpoint(), "put", headers=http_headers, json=json, data=data)
        else:
            self.send(self.get_collection_endpoint(), "post", headers=http_headers, json=json, data=data)

    def refresh(self):
        """
        Refreshes a resource by checking against the API
        """
        if self.get_resource_endpoint() is not None:
            self.send(self.get_resource_endpoint(), "get")

    def delete(self):
        """
        Deletes the resource from the server; Python object remains untouched
        :return:
        """
        if self.get_resource_endpoint() is not None:
            self.send(self.get_resource_endpoint(), http_method="delete")


class Manager(APIConnected):
    model_class = None
    json_collection_attribute = "data"
    paginator_class = DummyPaginator

    def __init__(self, auth_client):
        """
        :param auth_client: Client to make (non)authorized requests
        :return:
        """
        self.paginator = self.paginator_class()
        super(Manager, self).__init__(auth_client)

    @classmethod
    def get_collection_endpoint(cls):
        return cls.model_class.get_collection_endpoint()

    def get(self, resource_id):
        """
        Get one single resource from the API
        :param resource_id: Id of the resource to be retrieved
        :return: Retrieved resource
        """
        response = self.send(self.get_resource_endpoint(resource_id), "get")

        try:
            resource = self.model_class(self.client)
        except (ValueError, TypeError):
            return None
        else:
            resource.update_from_dict(self.client.get_response_data(response, self.parse_json))
            return resource

    def filter(self, **search_args):
        """
        Get a filtered list of resources
        :param search_args: To be translated into ?arg1=value1&arg2=value2...
        :return: A list of resources
        """
        raw_resources = []

        for url in self.paginator.get_urls(self.get_collection_endpoint()):
            response = self.paginator.process_response(self.send(url, "get", params=search_args))
            raw_resources += self.client.get_response_data(response, self.parse_json)[self.json_collection_attribute] if self.json_collection_attribute is not None else self.client.get_response_data(response, self.parse_json)

        resources = []

        for raw_resource in raw_resources:
            try:
                resource = self.model_class(self.client)
            except (ValueError, TypeError):
                continue
            else:
                resource.update_from_dict(raw_resource)
                resources.append(resource)

        return resources

    def all(self):
        """
        Get a list of all the resources
        :return: A list of resources
        """
        return self.filter()

    def create(self, **kwargs):
        resource = self.model_class(self.client)
        resource.update_from_dict(kwargs)
        resource.save()

        return resource
