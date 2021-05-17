from django.db import models

from django_qserializer.serialization import SerializableManager


class Company(models.Model):
    name = models.CharField(max_length=64)


class Bus(models.Model):
    plate = models.CharField(max_length=10)
    company = models.ForeignKey(Company, on_delete=models.SET_NULL)
    objects = SerializableManager()


class Travel(models.Model):
    bus = models.ForeignKey(Bus, related_name='travels', on_delete=models.SET_NULL)
