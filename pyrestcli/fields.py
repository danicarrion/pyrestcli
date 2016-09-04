from dateutil.parser import parse
from datetime import datetime


class Field(object):
    name = None
    value_class = None
    many = False

    def __init__(self):
        if self.value_class is not None:
            module_name, dot, class_name = self.value_class.rpartition(".")
            module = __import__(module_name, fromlist=[class_name])
            self.value_class = getattr(module, class_name)

    def __get__(self, instance, owner):
        if instance is not None:
            return instance.__dict__.get(self.name)
        else:
            return self

    def __set__(self, instance, value):
        if self.many is False:
            if self.value_class is None or isinstance(value, self.value_class):
                instance.__dict__[self.name] = value
        else:
            final_list = []
            for individual_value in value:
                if self.value_class is None or isinstance(individual_value, self.value_class):
                    final_list.append(individual_value)
            instance.__dict__[self.name] = final_list


class BooleanField(Field):
    pass


class IntegerField(Field):
    pass


class CharField(Field):
    pass


class DateTimeField(Field):
    def __set__(self, instance, value):
        if isinstance(value, datetime):
            instance.__dict__[self.name] = value
        else:
            instance.__dict__[self.name] = parse(value)


class ResourceField(Field):
    value_class = "pyrestcli.resources.Resource"

    def __set__(self, instance, value):
        instance.__dict__[self.name] = self.value_class(instance.client)
        if isinstance(value, dict):
            instance.__dict__[self.name].update_from_dict(value)
        else:
            setattr(instance, instance.id_field, value)
