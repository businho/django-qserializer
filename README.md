# django-qserializer

[![Continuos Integration](https://github.com/buserbrasil/django-qserializer/actions/workflows/python-app.yml/badge.svg)](https://github.com/buserbrasil/django-qserializer/actions)
[![Continuos Delivery](https://github.com/buserbrasil/django-qserializer/actions/workflows/python-publish.yml/badge.svg)](https://github.com/buserbrasil/django-qserializer/actions)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Imports: isort](https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336)](https://pycqa.github.io/isort/)

Django QSerializer started as an internal [Buser](https://www.buser.com.br)
project to improve our serialization process.

Database queries and serialization are two separated steps, but really ORM
coupled. Relationships must be fetched from database before serialization,
but Django don't have an easy way to setup that.

Start with a custom manager `SerializableManager`.

```python
from django.db import models
from django_qserializer import SerializableManager


class Company(models.Model):
    name = models.CharField(max_length=64)


class Bus(models.Model):
    objects = SerializableManager()
    company = models.ForeignKey(Company, on_delete=models.SET_NULL)
```

A basic serializer implementation would be:

```python
from django_qserializer import BaseSerializer


class BusSerializer(BaseSerializer):
    select_related = ['company']

    def serialize_object(self, obj):
        return {
            'id': obj.id,
            'company': {
                'name': obj.company.name,
            }
        }
```

Add the serializer to your queryset as:

```python
buses = Bus.objects.to_serialize(BusSerializer).all()

for bus in buses:
    # The serialize method is bound to BusSerializer.serialize_object.
    print(bus.serialize())
```

## API

### `BaseSerializer.select_related`

List of model fields to add to queryset with a `select_related` call.

### `BaseSerializer.prefetch_related`

List of model fields to add to queryset with a `prefetch_related` call.

```python
class BusSerializer(BaseSerializer):
    prefetch_related = ['company']

    def serialize_object(self, obj):
        return {
            'id': obj.id,
            'company': {
                'name': obj.company.name,
            }
        }
```

### `BaseSerializer.prepare_queryset`

Callable to change the queryset. It is possible to implement `select_related`
and `prefetch_related` attributes with it, but they work together with
`prepare_queryset`.

```python
class BusSerializer(BaseSerializer):
    select_related = ['company']

    def prepare_queryset(self, qs):
        return qs.annotate(state=Value('broken'))
```

### `BaseSerializer.prepare_objects`

Prepare objects after they are loaded to memory. Add data in bulk to them, like
fetching information from cache and attaching to loaded objects.

### `BaseSerializer.serialize_object`

Required implementation. It converts the Django model to a serializable
dict. Avoid slow calls here because it will cause N+1 issues.

### `BaseSerializer.serialize`

Execute `serialize_object` for each model object.

## Development
TODO update readme

To run the project, it is necessary the following tools:

- [Python](https://wiki.python.org/moin/BeginnersGuide/Download) 3.9 or higher

To create a virtual environment, run
```
python3 -m venv .venv
```

To activate the virtual environment, run
```
source .venv/bin/activate
```

To install the project's requirements in the virtual environment, run
```
pip install -e .\[test\]
```

To deactivate the virtual environment, run `deactivate`.

Run the commands of the following sections with the virtual environment active.

### Quality

The quality metrics of the project are reproduced by the continuos integration (CI) pipeline of the project. CI configuration in [`.github/workflows/ci.yml`](.github/workflows/python-app.yml) file.

#### Tests and linter

To run tests, coverage report and linter, run
```
pytest
```
To see the html report, check `htmlcov/index.html`.

Tests and coverage configuration in [`setup.cfg`](setup.cfg) file, at `[tool:pytest]` section.

Linter configuration in [`setup.cfg`](setup.cfg) file, at `[flake8]` section.

## License

This repository is licensed under the terms of [MIT License](LICENSE).
