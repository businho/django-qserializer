# django-qserializer

Django QSerializer started as an internal [Buser](https://www.buser.com.br)
project to improve our serialization process.

Database queries and serialization are two separated step, but really ORM
coupled. Relationships must be fetched from database before serialization,
but Django don't have an easy way to define that.


```python
from django.db import models
from django_qserializer import SerializableManager


class Company(models.Model):
    name = models.CharField(max_length=64)


class Bus(models.Model):
    company = models.ForeignKey(Company, on_delete=models.SET_NULL)
    objects = SerializableManager()
```
