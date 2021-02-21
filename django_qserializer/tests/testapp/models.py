from django.db import models

from django_qserializer.serialization import SerializableManager


class Author(models.Model):
    pass


class Book(models.Model):
    author = models.ForeignKey(Author, on_delete=models.SET_NULL)
    objects = SerializableManager()
