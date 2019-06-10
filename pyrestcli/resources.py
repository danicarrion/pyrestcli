import requests
from six import with_metaclass, iteritems
from future.utils import python_2_unicode_compatible
from datetime import datetime
try:
    from urllib.parse import urljoin
except ImportError:
    from urlparse import urljoin

from .fields import Field
from .paginators import DummyPaginator


class APIConnected(object):
    """
    This class handle API endpoints and interfaces with the authorization client for actually sending requests
    """
    class Meta:
        """
        This class hosts all the configuration parameters of the main class
        :param collection_endpoint: Relative path to the collection, /-terminated
        :param parse_json: Must be True is response data comes as a json string on the body of the response, False otherwise
        """
        collection_endpoint = None
        parse_json = True

    def __init__(self, auth_client):
        """
        Initializes the instance
        :param auth_client: Client to make (non)authorized requests
        :return:
        """
        self.client = auth_client

    @classmethod
    def get_resource_endpoint(cls, resource_id):
        """
        Get the relative path to a specific API resource
        :param cls: Resource class
        :param resource_id: Resource id
        :return: Relative path to the resource
        """
        return urljoin(cls.get_collection_endpoint(), str(resource_id)) if resource_id is not None else None

    @classmethod
    def get_collection_endpoint(cls):
        """
        Get the relative path to the API resource collection

        If self.collection_endpoint is not set, it will default to the lowercase name of the resource class plus an "s" and the terminating "/"
        :param cls: Resource class
        :return: Relative path to the resource collection
        """
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
    """
    Handle all the work that needs to be done on class initialization to deal with fields
    """
    def __init__(cls, name, bases, nmspc):
        """
        Manage Meta inheritance and create the self.fields list of field attributes
        :param cls: Class object
        :param name: Class name
        :param bases: Class inheritance
        :param nmspc: Class namespace
        :return:
        """
        super(ResourceMetaclass, cls).__init__(name, bases, nmspc)

        for klass in bases:
            if hasattr(klass, "Meta"):
                for attribute_name, attribute in iteritems(klass.Meta.__dict__):
                    if not (attribute_name.startswith("__") or hasattr(cls.Meta, attribute_name)):
                        setattr(cls.Meta, attribute_name, attribute)

        cls.fields = []
        for attribute_name, attribute in iteritems(cls.__dict__):
            if isinstance(attribute, Field):
                attribute.name = attribute_name
                cls.fields.append(attribute_name)


@python_2_unicode_compatible
class Resource(with_metaclass(ResourceMetaclass, APIConnected)):
    """
    Resource on the REST API

    API attributes are expected to be defined as attributes on the class by using fields. Configuration parameters go in the Meta class
    """
    class Meta:
        """
        This class hosts all the configuration parameters of the main class
        :param id_field: Name of the field that acts as the unique API identifier for the resouce
        :param name_field: Name of the field whose value can be used as a friendly representation of the resource
        :param json_data: Whether the API expects data to be sent as json or not
        """
        id_field = "id"
        name_field = "id"
        json_data = True

    def __init__(self, auth_client, **kwargs):
        """
        Initializes the resource
        :param auth_client: Client to make (non)authorized requests
        :param kwargs: Initial value for attributes
        :return:
        """
        for name, value in iteritems(kwargs):
            setattr(self, name, value)

        super(Resource, self).__init__(auth_client)

    def __str__(self):
        """
        Give a nice representation for the resource
        :param return: Resource friendly representation based on the self.Meta.name_field attribute
        """
        return getattr(self, self.Meta.name_field, super(Resource, self).__str__())

    def get_id(self):
        return getattr(self, self.Meta.id_field, None)

    def get_resource_endpoint(self):
        """
        Get the relative path to the specific API resource
        :return: Relative path to the resource
        """
        return super(Resource, self).get_resource_endpoint(self.get_id())

    def update_from_dict(self, attribute_dict):
        """
        Update the fields of the resource out of a data dictionary taken out of an API response
        :param attribute_dict: Dictionary to be mapped into object attributes
        :return:
        """
        for field_name, field_value in iteritems(attribute_dict):
            if self.fields is None or field_name in self.fields:
                setattr(self, field_name, field_value)

    def send(self, url, http_method, **client_args):
        """
        Make the actual request to the API, updating the resource if necessary
        :param url: Endpoint URL
        :param http_method: The method used to make the request to the API
        :param client_args: Arguments to be sent to the auth client
        :return:
        """
        response = super(Resource, self).send(url, http_method, **client_args)
        response_data = self.client.get_response_data(response, self.Meta.parse_json)

        # Update Python object if we get back a full object from the API
        try:
            if response_data:
                self.update_from_dict(response_data)
        except ValueError:
            pass

        return response if response is not None else None

    def save(self, force_create=False, fields=None):
        """
        Saves (creates or updates) resource on the server
        :param force_create: If True, forces resource creation even if it already has an Id.
        :param fields: List of fields to be saved. If None, all fields will be saved.
        :return:
        """
        values = {}
        fields = fields or self.fields

        for field_name in fields:
            value = getattr(self, field_name)

            # When creating or updating, only references to other resources are sent, instead of the whole resource
            if isinstance(value, Resource):
                value = value.get_id()

            if isinstance(value, list):
                # Lists of resources are not sent when creating or updating a resource
                if len(value) > 0 and isinstance(value[0], Resource):
                    value = None
                else:
                    # We need to check for datetimes in the list
                    final_value_list = []
                    for item in value:
                        final_value_list.append(item.isoformat() if isinstance(item, datetime) else item)
                    value = final_value_list

            if isinstance(value, datetime):
                # TODO: Allow for different formats
                value = value.isoformat()

            if value is not None:
                values[field_name] = value

        http_headers = {'content-type': 'application/json'} if self.Meta.json_data is True else None
        json = values if self.Meta.json_data is True else None
        data = values if self.Meta.json_data is False else None

        if self.get_resource_endpoint() is not None and force_create is False:
            return self.send(self.get_resource_endpoint(), "put", headers=http_headers, json=json, data=data)
        else:
            return self.send(self.get_collection_endpoint(), "post", headers=http_headers, json=json, data=data)

    def refresh(self):
        """
        Refreshes a resource by checking against the API
        :return:
        """
        if self.get_resource_endpoint() is not None:
            return self.send(self.get_resource_endpoint(), "get")

    def delete(self):
        """
        Deletes the resource from the server; Python object remains untouched
        :return:
        """
        if self.get_resource_endpoint() is not None:
            return self.send(self.get_resource_endpoint(), http_method="delete")


class Manager(APIConnected):
    """
    Manager class for resources
    :param resource_class: Resource class
    :param json_collection_attribute: Which attribute of the response json hosts the list of resources when retrieving the resource collection
    :param paginator_class: Which paginator class to use when retrieving the resource collection
    """
    resource_class = None
    json_collection_attribute = "data"
    paginator_class = DummyPaginator

    def __init__(self, auth_client):
        """
        :param auth_client: Client to make (non)authorized requests
        :return:
        """
        self.paginator = self.paginator_class(auth_client.base_url)
        super(Manager, self).__init__(auth_client)

    @classmethod
    def get_collection_endpoint(cls):
        """
        Get the relative path to the API resource collection, using the corresponding resource class

        :param cls: Manager class
        :return: Relative path to the resource collection
        """
        return cls.resource_class.get_collection_endpoint()

    def get(self, resource_id):
        """
        Get one single resource from the API
        :param resource_id: Id of the resource to be retrieved
        :return: Retrieved resource
        """
        response = self.send(self.get_resource_endpoint(resource_id), "get")

        try:
            resource = self.resource_class(self.client)
        except (ValueError, TypeError):
            return None
        else:
            response_data = self.client.get_response_data(response, self.Meta.parse_json)
            if response_data:
                resource.update_from_dict(response_data)
            return resource

    def filter(self, **search_args):
        """
        Get a filtered list of resources
        :param search_args: To be translated into ?arg1=value1&arg2=value2...
        :return: A list of resources
        """
        search_args = search_args or {}
        raw_resources = []

        for url, paginator_params in self.paginator.get_urls(self.get_collection_endpoint()):
            search_args.update(paginator_params)
            response = self.paginator.process_response(self.send(url, "get", params=search_args))
            raw_resources += self.client.get_response_data(response, self.Meta.parse_json)[self.json_collection_attribute] if self.json_collection_attribute is not None else self.client.get_response_data(response, self.Meta.parse_json)

        resources = []

        for raw_resource in raw_resources:
            try:
                resource = self.resource_class(self.client)
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
        """
        Create a resource on the server
        :params kwargs: Attributes (field names and values) of the new resource
        """
        resource = self.resource_class(self.client)
        resource.update_from_dict(kwargs)
        resource.save(force_create=True)

        return resource
