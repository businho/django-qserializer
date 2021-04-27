# django-qserializer

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
class BusSerializer(BaseSerializer):
    select_related = ['company']

    def serialize_object(self, obj):
        return {
            'id': self.id,
            'company': {
                'name': self.company.name,
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
            'id': self.id,
            'company': {
                'name': self.company.name,
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