# pyrestcli

*Generic, object-oriented Python client for REST APIs*

_pyrestcli_ allows you to define data models, with a syntax that is derived from Django's model framework, that you can use directly against REST APIs. All the internals of the communication with the API is transparently handled by _pyrestcli_ for you.

## Installation

```
$ pip install pyrestcli
```

## Usage

### API base URL and authentication

First, you need to define how to reach and be authorized to use the API. _pyrestcli_ includes out-of-the-box support for no authentication, HTTP basic authentication and HTTP-header-based token authentication. This is an example for HTTP basic authentication on http://test.com/api:

```python
from pyrestcli.auth import BasicAuthClient

auth_client = BasicAuthClient("admin", "admin", "http://test.com/api")
```

# Basic model definition and operations

Now, you need to create your models, according to the schema of the data available on the server.

For instance, let us take a REST object that represents a person like this:

```json
{
    id: 1,
    name: "John Doe",
    email: "johndoe@test.com"
}
```

The corresponding model in _pyrestcli_ would be:

```python
from pyrestcli.fields import CharField, IntegerField
from pyrestcli.resources import Resource, Manager

class Person(Resource):
    id = IntegerField()
    name = CharField()
    email = CharField()

class PersonManager(Manager):
    resource_class = Person
```

Also, `BooleanField` and `DateTimeField` are available.

Now we could very easily get the list of persons found at http://test.com/api/persons, assuming the list returned by the server looks like:

```json
{
    data: [
        {
            id: 1,
            name: "Jane Doe",
            email: "janedoe@test.com"
        },
        {
            id: 2,
            name: "John Doe",
            email: "johndoe@test.com"
        }
    ]
}
```

For this, we would simply do:

```python
person_manager = PersonManager()
persons = PersonManager.all()
```

Now ```persons``` is an array of 2 ```Person``` objects. You can also get one single object like this:

```python
jane_doe = person_manager.get(1)
```

Similarly, you can also get a filtered list of persons, if supported by the API:

```python
persons = PersonManager.filter(name="John Doe")
```

That would be translated into a request like this: http://test.com/api/persons/?name=John%20Doe

Pagination is supported. A paginator compatible with Django REST Framework is provided, but it should be pretty straightforward to subclass the main `Paginator` object and adapt it for each particular case:

```python
from pyrestcli.paginators import NextWithUrlPaginator


class PersonManager(Manager):
    resource_class = Person
    paginator_class = NextWithUrlPaginator
```

When defining the models, it's also possible to use another field as the _id_ of the model, another name for the endpoint, or another name for the JSON attribute that holds the collection, instead of the default `data`:

```python
class Person(Resource):
    id = IntegerField()
    name = CharField()
    email = CharField()

    class Meta:
        id_field = "email"
        collection_endpoint = "people"

class PersonManager(Manager):
    resource_class = Person
    json_collection_attribute = "results"
```

Our `jane_doe` object can be updated easily:

```python
jane_doe.email = "jane.doe@test.com"
jone_doe.save()
```

Or deleted:

```python
jone_doe.delete()
```

Creating another person is also straightforward:

```python
jimmy_doe = person_manager.create(name="Jimmy Doe", email="jimmydoe@test.com")
```

### Custom fields and resources

Let us assume there is another API model for cars, where `owner` is linked to a person.

```json
{
    id: 1,
    make: "Toyota",
    owner: 1
}
```

We could create another _pyrestcli_ model such as this:

```python
from pyrestcli.fields import CharField, IntegerField, ResourceField
from pyrestcli.resources import Resource, Manager


class PersonField(ResourceField):
    value_class = "Person"


class Car(Resource):
    id = IntegerField()
    make = CharField()
    owner = PersonField()

    class Meta:
        name_field = "make"

class CarManager(Manager):
    resource_class = Car
```

Because `Car` does not have a `name` field, we need to specify which field to be used to get a friendly representation of the model.

This works as expected, and the `owner` attribute of a `Car` object is a `Person` object. One caveat is, if the API does not give the full `Person` object when getting a `Car` object, but only its id instead (quite usual), you will have to call the `refresh` method on the `Person` object to have it populated.

### What's next?

Full documentation is yet to be written, but code is reasonably well commented and the test suite includes a basic, yet complete example of how to use _pyrestcli_.

## Test suite

_pyrestcli_ includes a test suite on the `tests`. The test suite is not available if you install _pyrestcli_ with _pip_. Rather, you need to download _pyrestcli_ directly from GitHub and install it locally.

First, clone the repo:

```
$ git clone git@github.com:danicarrion/pyrestcli.git
```

Cd into the folder, create and enable the virtualenv, install _pyrestcli_ and [pytest](http://doc.pytest.org/en/latest/):

```
$ cd pyrestcli
$ virtualenv env
$ source env/bin/activate
$ pip install -e .
$ pip install pytest
```

The test suite is run against a [Django](https://www.djangoproject.com/) server that uses [Django Rest Framework](http://www.django-rest-framework.org/) to serve some test models over a REST API. In order to install these, you need to:

```
$ cd tests
$ pip install -r requirements.txt
```

Now, you need to migrate the database and start the server:

```
$ cd restserver
$ python manage.py migrate
$ python manage.py runserver
```

The test app creates two models `Question` and `Choice` exactly as defined by the [Django tutorial](https://docs.djangoproject.com/en/1.10/intro/tutorial01/), together with their corresponding REST serializers. Also, a user is created to test authentication. User name is "admin" and password is "admin" too. You can use that user to take a look at how the REST API looks like on the Web browsable API located at http://localhost:8000/.

In order to run the tests, you need to go back to the main folder, on a terminal with the virtualenv activated, and do:

```
$ py.test tests
```

Any time, you can clean up the test database by deleting the database file and running the migrations again.
