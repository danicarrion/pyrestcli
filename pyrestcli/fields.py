from dateutil.parser import parse


class Field(object):
    """
    Fields represent attributes of resources. This class is meant to be subclassed everytime a new specific data type wants to be defined
    on the value_class attribute.

    This default field simply stores the value in the instance as it comes, suitable for basic types such as integers, chars, etc.

    Fields are a very handy way to parse jsons coming from the REST API and store real Python objects on the resource
    """
    def __init__(self, many=False):
        """
        Initialize the field
        :param many: Set to True if this field will host a list of items
        """
        self.many = many
        self.name = None  # Name of the field on the corresponding instance, must be filled in when the corresponding resource is initialized

    def __get__(self, instance, owner):
        """
        Normal descriptor get method
        :param instance: Resource instance where the field lives
        :param instance: Resource class where the field lives
        :return: Value stored in instance.name (TODO: maybe change this in the future to instance.Cache.name)
        """
        if instance is not None and self.name is not None:
            return instance.__dict__.get(self.name)
        else:
            return self

    def __set__(self, instance, value):
        """
        Normal descriptor set method
        :param instance: Resource instance where the field lives
        :param value: Value to store in instance.name (TODO: maybe change this in the future to instance.Cache.name)
        """
        if instance is not None and self.name is not None:
            instance.__dict__[self.name] = value


class BooleanField(Field):
    """
    Convenient class to make explicit that an attribute will store booleans
    """
    pass


class IntegerField(Field):
    """
    Convenient class to make explicit that an attribute will store integers
    """
    pass


class FloatField(Field):
    """
    Convenient class to make explicit that an attribute will store floats
    """
    pass


class CharField(Field):
    """
    Convenient class to make explicit that an attribute will store chars
    """
    pass


class DateTimeField(Field):
    """
    Field to store datetimes in resources
    """
    def __set__(self, instance, value):
        """
        Normal descriptor set method
        :param instance: Resource instance where the field lives
        :param value: Might be a datetime object or a string to be parsed
        """
        if self.many is False:
            if isinstance(value, str):
                value = parse(value)
        else:
            datetime_list = []
            for datetime_value in value:
                if isinstance(datetime_value, str):
                    datetime_value = parse(datetime_value)
                datetime_list.append(datetime_value)
            value = datetime_list

        super(DateTimeField, self).__set__(instance, value)


class DictField(Field):
    """
    Convenient class to make explicit that an attribute will store a dictionary
    """
    pass


class ResourceField(Field):
    """
    Field to store resources inside other resources
    """
    value_class = "pyrestcli.resources.Resource"  # Subclasses should update this according to the resource type they are pointing at
    _initialized = False

    def set_real_value_class(self):
        """
        value_class is initially a string with the import path to the resource class, but we need to get the actual class before doing any work

        We do not expect the actual clas to be in value_class since the beginning to avoid nasty import egg-before-chicken errors
        """
        if self.value_class is not None and isinstance(self.value_class, str):
            module_name, dot, class_name = self.value_class.rpartition(".")
            module = __import__(module_name, fromlist=[class_name])
            self.value_class = getattr(module, class_name)
            self._initialized = True

    def __set__(self, instance, value):
        if self._initialized is False:
            self.set_real_value_class()

        if self.many is False:
            resource = self.value_class(instance.client)
            if isinstance(value, dict):
                resource.update_from_dict(value)
            else:
                resource.update_from_dict({resource.Meta.id_field: value})
            value = resource
        else:
            resource_list = []
            for resource_value in value:
                resource = self.value_class(instance.client)
                if isinstance(resource_value, dict):
                    resource.update_from_dict(resource_value)
                else:
                    resource.update_from_dict({resource.Meta.id_field: resource_value})
                resource_list.append(resource)
            value = resource_list

        super(ResourceField, self).__set__(instance, value)
